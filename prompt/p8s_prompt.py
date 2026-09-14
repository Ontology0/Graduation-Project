"""
p8s 실험용 팀 공용 프롬프트 규격.

이 파일은 수정하지 않는다. 수정이 필요하면 PROMPT_VERSION을 올리고 팀에 공지한 뒤
전원이 재실행한다. 실험 결과 CSV에는 반드시 PROMPT_VERSION 컬럼을 남긴다.

사용법 (Colab):
    !wget -q -O p8s_prompt.py <RAW_GITHUB_URL>
    from p8s_prompt import build_messages, truncate_answer, score_row, PROMPT_VERSION

    msgs = build_messages(question, ctx_text)
    prompt = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
    # ... 이후 생성 / steering / attention 추출은 각자 구현

설계 메모:
    - "single word" 지시는 쓰지 않는다. p8s gold의 67%가 2단어 이상이라
      (Milton Friedman, Tel Aviv, United States of America) 지시가 오히려 형식을 깨뜨린다.
      대신 "정답 문자열만 출력 + 최대한 짧게"로 규정하고 few-shot이 길이 감각을 잡는다.
    - few-shot 3개는 전부 non-conflict(문맥 주장 == gold)이며,
      p8 / p8s 어느 쪽에도 없는 수기 예시라 데이터 누수가 없다.
    - few-shot은 하나의 blob이 아니라 user/assistant 턴으로 넣는다
      (Llama-3.1-Instruct에서 형식 고정이 더 안정적).
"""

import re
import string
import unicodedata

PROMPT_VERSION = "p8s-v1"
MODEL_ID = "meta-llama/Llama-3.1-8B-Instruct"
MAX_NEW_TOKENS = 48  # 팀 결정사항

# ---------------------------------------------------------------- 프롬프트 상수

SYSTEM_PROMPT = (
    "You are a question answering system. "
    "Answer the question using ONLY the given context. "
    "Output the answer string itself and nothing else: no sentence, no explanation, "
    "no punctuation, no quotes. Keep it as short as possible (a name or a term). "
    "If the context does not state the answer, output the most likely short answer anyway."
)

# closed-book(K± 재판정용): 문맥 없음
SYSTEM_PROMPT_CB = (
    "You are a question answering system. Answer from your own knowledge. "
    "Output the answer string itself and nothing else: no sentence, no explanation, "
    "no punctuation, no quotes. Keep it as short as possible (a name or a term)."
)

FEWSHOT = [
    {
        "context": (
            "Reykjavik Reykjavik is the capital and largest city of Iceland. "
            "Located in the south-western part of the island, it is the seat of the "
            "national government and the country's main cultural centre."
        ),
        "question": "What is the capital of Iceland?",
        "answer": "Reykjavik",
    },
    {
        "context": (
            "The Old Man and the Sea The Old Man and the Sea is a short novel written by "
            "Ernest Hemingway in 1951 in Cuba and published in 1952. It was the last major "
            "work of fiction produced by Hemingway during his lifetime."
        ),
        "question": "Who is the author of The Old Man and the Sea?",
        "answer": "Ernest Hemingway",
    },
    {
        "context": (
            "Ada Lovelace Augusta Ada King, Countess of Lovelace, was an English mathematician "
            "chiefly known for her work on Charles Babbage's Analytical Engine. She is often "
            "regarded as the first computer programmer."
        ),
        "question": "What is Ada Lovelace's occupation?",
        "answer": "mathematician",
    },
]

USER_TMPL = "Context: {ctx}\nQuestion: {q}\nAnswer:"
USER_TMPL_CB = "Question: {q}\nAnswer:"


# ---------------------------------------------------------------- 메시지 빌더

def build_messages(question, context):
    """본 실험용 messages (context 포함)."""
    msgs = [{"role": "system", "content": SYSTEM_PROMPT}]
    for ex in FEWSHOT:
        msgs.append({"role": "user",
                     "content": USER_TMPL.format(ctx=ex["context"], q=ex["question"])})
        msgs.append({"role": "assistant", "content": ex["answer"]})
    msgs.append({"role": "user", "content": USER_TMPL.format(ctx=context, q=question)})
    return msgs


def build_messages_cb(question):
    """closed-book용 messages (K± 재판정)."""
    msgs = [{"role": "system", "content": SYSTEM_PROMPT_CB}]
    for ex in FEWSHOT:
        msgs.append({"role": "user", "content": USER_TMPL_CB.format(q=ex["question"])})
        msgs.append({"role": "assistant", "content": ex["answer"]})
    msgs.append({"role": "user", "content": USER_TMPL_CB.format(q=question)})
    return msgs


# ------------------------------------------------- 토큰 인덱스 (attention / hook용)

def ctx_char_offset(question, context):
    """프롬프트 문자열 안에서 이 행의 ctx_text가 시작하는 문자 위치.

    데이터셋의 ans_start/ans_end는 ctx_text 내부 기준이므로,
    프롬프트 전체 기준으로 쓰려면 이 값을 더해야 한다.
    few-shot 예시에도 'Context: '가 있으므로 마지막 것을 기준으로 찾는다.
    """
    last_user = USER_TMPL.format(ctx=context, q=question)
    return last_user.index(context)


def answer_token_span(tok, question, context, ans_start, ans_end):
    """ctx_text 내 문자 구간(ans_start, ans_end)을 프롬프트 토큰 인덱스 구간으로 변환.

    반환: (tok_start, tok_end_exclusive). 매칭 실패 시 (None, None).
    주의: few-shot 프리픽스 때문에 인덱스가 크게 밀리므로 하드코딩 금지.
    """
    msgs = build_messages(question, context)
    prompt = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)

    # 마지막 user 턴(= 실제 질문)의 context를 기준으로 절대 문자 위치 계산
    base = prompt.rindex(context)
    abs_start, abs_end = base + int(ans_start), base + int(ans_end)

    enc = tok(prompt, return_offsets_mapping=True, add_special_tokens=False)
    idx = [i for i, (s, e) in enumerate(enc["offset_mapping"])
           if s < abs_end and e > abs_start]
    if not idx:
        return None, None
    return idx[0], idx[-1] + 1


# ---------------------------------------------------------------- 출력 후처리 / 채점

def truncate_answer(raw):
    """모델 출력 -> 채점용 짧은 span. 원문(raw)은 항상 별도 컬럼에 보존할 것."""
    s = str(raw).strip()
    s = s.split("\n")[0].strip()                      # 첫 줄만
    s = re.sub(r"^(answer|the answer is)\s*:?\s*", "", s, flags=re.I)
    s = s.split(". ")[0]                              # 문장화된 경우 첫 문장
    s = s.strip().strip('"\'')
    return re.sub(r"[.,;:\s]+$", "", s).strip()


_ARTICLES = {"a", "an", "the"}


def norm(s):
    s = unicodedata.normalize("NFKC", str(s)).lower()
    s = "".join(ch for ch in s if ch not in set(string.punctuation))
    return " ".join(t for t in s.split() if t not in _ARTICLES)


def score_row(pred, gold_list, answer_surface=""):
    """반환: (em, sub, follows_ctx)

    em          : 정규화 후 gold 별칭과 완전일치  <- 주지표
    sub         : gold 별칭이 출력에 부분포함     <- 과거 실험 호환용 보조지표
    follows_ctx : 출력이 문맥 주장(answer_surface)과 일치 <- accept/retain 판정용

    C- 행에서 em=1 이면 retain(파라메트릭 유지), follows_ctx=1 이면 accept(문맥 추종).
    """
    p = norm(pred)
    golds = [norm(g) for g in gold_list]
    em = int(any(p == g for g in golds))
    sub = int(any(g and g in p for g in golds))
    fc = int(bool(answer_surface) and norm(answer_surface) in p)
    return em, sub, fc


def format_check(preds):
    """프롬프트가 먹었는지 확인. 매 실험 로그에 남길 것."""
    n = [len(str(p).split()) for p in preds]
    over = sum(1 for x in n if x > 6) / max(len(n), 1)
    return {"mean_words": round(sum(n) / max(len(n), 1), 2),
            "over_6_words_ratio": round(over, 3),
            "prompt_version": PROMPT_VERSION}
