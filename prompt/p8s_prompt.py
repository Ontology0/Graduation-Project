"""
p8s 실험용 팀 공용 프롬프트 규격.

이 파일은 수정하지 않는다. 수정이 필요하면 PROMPT_VERSION을 올리고 팀에 공지한 뒤
전원이 재실행한다. 실험 결과 CSV에는 반드시 PROMPT_VERSION 컬럼을 남긴다.
버전이 다른 CSV끼리는 비교하지 않는다.

사용법 (Colab):
    !wget -q -O p8s_prompt.py <RAW_GITHUB_URL>
    from p8s_prompt import build_messages, truncate_answer, score_row, PROMPT_VERSION

    msgs = build_messages(question, ctx_text)
    prompt = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
    # ... 이후 생성 / steering / attention 추출은 각자 구현


================================ v1 -> v2 변경 ================================

E0(프롬프트 편향 실험, 812행, arm별 paired, McNemar)에서 v1의 지시문이 실험의
종속변수 자체를 오염시키고 있음이 확인되어 세 가지를 제거했다.

주지표: K+C- 칸(모델이 답을 아는데 컨텍스트가 딴소리하는 칸, n=378)의 accept율.

    arm  변경                                   accept   em(retain)
    A0   v1 원본 (ONLY + C+ few-shot)            0.595      0.106
    A1   using ONLY -> based on                  0.503      0.214
    A2   + abstain 금지 문장 삭제                 0.503      0.212
    A3   + few-shot 삭제                         0.394      0.373
    A5   v2 최종 (= A2 + A3)                     0.405      0.370

    A0->A1 (ONLY 제거)      n01=1,  n10=36  p=5.5e-10
    A1->A3 (few-shot 제거)  n01=13, n10=54  p=4.5e-07
    A1<->A2 (abstain 문장)  n01=7,  n10=7   p=1.00   (null)
    A3<->A5 (abstain 문장)  n01=9,  n10=5   p=0.42   (null)

1) "using ONLY the given context" -> "based on the given context"
   ONLY는 충돌 시 컨텍스트를 따르라는 지시다. 우리 종속변수가 바로 그 선택이라
   지시가 답을 미리 정해버린다. based on은 "컨텍스트가 이 태스크의 입력"이라는
   사실만 말하고 충돌 시 무엇을 고르라고는 하지 않는다.

2) abstain 금지 문장("If the context does not state the answer...") 삭제
   few-shot 유무와 무관하게 완전 null. 효과는 없고 중의성만 있어 제거.

3) few-shot 3개 삭제
   3개 모두 non-conflict(C+)라 "충돌하면 컨텍스트를 따르라"를 예시로 가르치고
   있었다. 형식은 few-shot 없이도 유지된다(mean_tok 3.05, over6 0.000,
   hit_limit 0.000)므로 "예시는 구조만 보라" 류의 추가 지시도 불필요하다.

편향이 아니라 모델 손상이라는 반론은 다음으로 막힌다:
  - C+ 칸 em은 전 arm 불변(0.870 / 0.710) -> 독해 능력 그대로
  - K-C- accept는 6개 비교 전부 null(p 0.23~0.75) -> 모르는 질문에선 변화 없음
  - 움직인 칸은 K+C- 하나뿐. 모델에게 선택지가 있는 유일한 칸.

사람 검증: A0/A5가 갈린 96건을 직접 라벨링(GOLD/CTX/NONE).
  자동채점 Δ=19.0%p, 사람 라벨 Δ=19.8%p로 0.8%p 이내 일치.
  accept가 꺼진 83건 중 72건(86.7%)이 파라메트릭 정답으로 전환.


============================ 베이스라인 민감도 ============================

"based on도 지시문이니 무지시 기준점이 필요하다"는 지적에 따라 추가 측정.

    arm  시스템 프롬프트                          accept   em
    A6   역할 선언 + 형식 지시                     0.317   0.471
    A8   "According to the given information
          and your knowledge" + 형식 지시          0.376   0.402
    A7   형식 지시만                               0.389   0.381
    A5   v2 (역할 + based on + 형식)               0.405   0.370

    A5<->A7  n01=6,  n10=12  p=0.238   (null)
    A5<->A8  n01=2,  n10=13  p=7.4e-03
    A5<->A6  n01=0,  n10=33  p=2.3e-10
    A6<->A7  n01=30, n10=3   p=1.4e-06

v2는 더 뺄 것이 없는 최소 프롬프트(A7)와 통계적으로 구분되지 않는다(p=0.238).
반면 역할 선언 문장 자체가 accept를 7.2%p 움직이므로(A6 vs A7) 단일 중립
기준점은 정의되지 않으며, 0.317~0.389를 민감도 구간으로 보고한다. 이 폭(7%p)은
v1 대비 효과(19%p)의 1/3 수준이라 기준점을 어디로 잡든 결론은 불변이다.

역할 선언은 v1에서 그대로 유지했다. 이것이 더 낫다는 판단이 아니라, 제거 대상
세 가지에 포함되지 않았기 때문이다. 7.2%p는 사후적으로 관측된 값이며, 이를 근거로
프롬프트를 재선정하면 outcome-driven selection이 된다.


================================== 선행연구 ==================================

Xie et al., "Adaptive Chameleon or Stubborn Sloth" (ICLR 2024, arXiv:2305.13300)
  - 부록 C 프롬프트 표: ONLY도 abstain 금지 문장도 없는 지시문 사용
  - 전 실험을 zero-shot으로 수행. 이유를 demonstration 편향 회피로 명시
  - 예비 실험에서 지시문 10종을 안정성 기준으로 평가 후 채택
단, 측정 방식이 객관식(memory answer / counter-answer / Uncertain)이라
free-form EM인 우리 절대값과는 비교 불가. 프롬프트 설계의 선례로만 인용한다.


================================== 기타 결정 ==================================

MAX_NEW_TOKENS = 192. 48은 retract된 세팅이다(절단률이 조건별로 비대칭이라
효과가 큰 조건이 가장 많이 깎였음). E0 전 arm에서 hit_limit 0.000이었다.

채점 한계 (논문에 명시 필요):
  - 성(last name)만 출력하면 EM이 0이 된다. DeLillo(gold: Don DeLillo),
    Scott(gold: Ridley Scott) 등.
  - p8s gold 별칭 리스트 자체가 불완전하다(Kanye 직업에 rapper 없음,
    Toy Story 각본가에 Joel Cohen 없음, First Contact에 Ronald D. Moore 없음).
  - 둘 다 retain 방향 손실이므로 보고되는 em/retain 수치는 하한이다.
"""

import re
import string
import unicodedata

PROMPT_VERSION = "p8s-v2"
MODEL_ID = "meta-llama/Llama-3.1-8B-Instruct"
MAX_NEW_TOKENS = 192  # 팀 결정사항. 48로 내리지 말 것

# ---------------------------------------------------------------- 프롬프트 상수

SYSTEM_PROMPT = (
    "You are a question answering system. "
    "Answer the question based on the given context. "
    "Output the answer string itself and nothing else: no sentence, no explanation, "
    "no punctuation, no quotes. Keep it as short as possible (a name or a term)."
)

# closed-book(K± 재판정용): 문맥 없음
SYSTEM_PROMPT_CB = (
    "You are a question answering system. Answer from your own knowledge. "
    "Output the answer string itself and nothing else: no sentence, no explanation, "
    "no punctuation, no quotes. Keep it as short as possible (a name or a term)."
)

# v2에서 few-shot을 제거했다. E0에서 C+ 전용 예시가 accept를 10.9%p 밀고 있었고,
# 형식은 few-shot 없이도 유지된다. 빈 리스트를 유지하되 구조는 남겨둔다.
FEWSHOT = []

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
    """closed-book용 messages (K± 재판정).

    주의: v1 기준 kside/knows 라벨은 v2에서 유효성이 보장되지 않는다.
    형식 지시가 출력을 크게 바꾸므로 closed-book 정확도도 바뀐다.
    이전 프롬프트 변경 때 10.9% flip 전례가 있다. E1 전에 반드시 재판정할 것.
    """
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
    """
    last_user = USER_TMPL.format(ctx=context, q=question)
    return last_user.index(context)


def answer_token_span(tok, question, context, ans_start, ans_end):
    """ctx_text 내 문자 구간(ans_start, ans_end)을 프롬프트 토큰 인덱스 구간으로 변환.

    반환: (tok_start, tok_end_exclusive). 매칭 실패 시 (None, None).

    v2에서 few-shot이 빠져 프리픽스가 약 280토큰 짧아졌다. v1 기준으로 하드코딩된
    인덱스는 전부 어긋난다. 절대 인덱스 대신 이 함수를 쓸 것.
    """
    msgs = build_messages(question, context)
    prompt = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)

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
    C+ 행의 em은 그냥 정확도다. 두 칸에서 의미가 다르니 집계 시 반드시 분리할 것.

    알려진 한계 (파일 상단 '채점 한계' 참고):
      - 성만 출력하면 em=0 -> retain 과소집계
      - follows_ctx는 부분포함이라 나열형 출력을 accept로 잘못 잡음
    """
    p = norm(pred)
    golds = [norm(g) for g in gold_list]
    em = int(any(p == g for g in golds))
    sub = int(any(g and g in p for g in golds))
    fc = int(bool(answer_surface) and norm(answer_surface) in p)
    return em, sub, fc


def format_check(preds):
    """프롬프트가 먹었는지 확인. 매 실험 로그에 남길 것.

    E0 기준값: mean_words 약 3.0, over_6_words_ratio 0.000~0.013.
    크게 벗어나면 프롬프트가 안 먹은 것이므로 결과 해석 전에 확인할 것.
    """
    n = [len(str(p).split()) for p in preds]
    over = sum(1 for x in n if x > 6) / max(len(n), 1)
    return {"mean_words": round(sum(n) / max(len(n), 1), 2),
            "over_6_words_ratio": round(over, 3),
            "prompt_version": PROMPT_VERSION}
