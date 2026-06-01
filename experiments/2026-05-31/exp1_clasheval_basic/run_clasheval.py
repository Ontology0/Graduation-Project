# ClashEval-style Conflict Experiment (Colab)
# parametric vs contextual knowledge conflict
# 자동 채점 포함

import os, json
from getpass import getpass
from openai import OpenAI

# ============================================================
# 0. API 키 + 클라이언트
# ============================================================
key = getpass("LiteLLM key: ").strip()
client = OpenAI(api_key=key, base_url="http://43.201.226.184:4000")
MODEL = "claude-haiku-4-5-20251001"   # 가벼운 테스트. 본 실험은 claude-sonnet-4-6

# ============================================================
# 1. 데이터 로드
#    clash_conflicts.jsonl 을 Colab에 업로드하거나
#    레포에서 가져온다
# ============================================================
PATH = "clash_conflicts.jsonl"
cases = [json.loads(l) for l in open(PATH, encoding="utf-8")]
print(f"Loaded {len(cases)} cases "
      f"({sum(c['doc_truthful'] for c in cases)} truthful docs, "
      f"{sum(not c['doc_truthful'] for c in cases)} false docs)")

# ============================================================
# 2. 프롬프트 (Base vs Conflict-aware)
#    레포의 .md 대신 여기 직접 정의 (실험 자립성)
# ============================================================
BASE_SYS = ("You are a helpful assistant. Answer the user's question using the "
            "provided context when it is relevant. Give a direct, concise answer.")

CA_SYS = ("You are a careful assistant. The provided documents may contain errors "
          "or may conflict with well-established facts you already know. For each "
          "question, judge whether the document is reliable. If the document "
          "contradicts a well-known fact and appears incorrect, rely on your own "
          "knowledge instead. If the document provides updated or specific "
          "information that is plausibly correct, use it. State briefly which "
          "source you trusted and why.")

USER_TMPL = ("Context:\n{ctx}\n\nQuestion: {q}\n\n"
             "Answer in one or two sentences.")

def build_user(case):
    ctx = "\n".join(f"[{d['doc_id']}] {d['text']}" for d in case["documents"])
    return USER_TMPL.format(ctx=ctx, q=case["question"])

# ============================================================
# 3. 실행
# ============================================================
def run_case(case, system):
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "system", "content": system},
                  {"role": "user", "content": build_user(case)}],
        max_tokens=150, temperature=0.0,
    )
    return resp.choices[0].message.content.strip()

def run_arm(arm, system):
    out = []
    for i, c in enumerate(cases):
        ans = run_case(c, system)
        out.append({**c, "predicted_answer": ans, "arm": arm})
        print(f"[{arm}] [{i+1}/{len(cases)}] {c['id']}")
    return out

base = run_arm("base", BASE_SYS)
ca = run_arm("conflict_aware", CA_SYS)
print("Generation done.")

# ============================================================
# 4. 자동 채점
#    - correct: gold_answer 핵심값이 답에 포함?
#    - followed: contextual / parametric / unclear
# ============================================================
def norm(s):
    return s.lower().replace(",", "").replace("approximately", "").replace("about", "").strip()

def contains(answer, target):
    # 핵심 토큰(숫자/단어) 포함 여부 (느슨한 substring)
    a, t = norm(answer), norm(target)
    # 숫자가 포함된 경우 숫자 단위로도 체크
    return t in a or all(tok in a for tok in t.split() if len(tok) > 2)

def grade(r):
    ans = r["predicted_answer"]
    gold_hit = contains(ans, r["gold_answer"])
    ctx_hit = contains(ans, r["contextual_answer"])
    par_hit = contains(ans, r["parametric_answer"])

    # 따른 출처 판정
    if ctx_hit and not par_hit:
        followed = "contextual"
    elif par_hit and not ctx_hit:
        followed = "parametric"
    elif ctx_hit and par_hit:
        followed = "both"
    else:
        followed = "unclear"

    return {**r, "correct": gold_hit, "followed": followed}

graded = [grade(r) for r in base + ca]

# ============================================================
# 5. 지표 집계
# ============================================================
def report(arm):
    rows = [g for g in graded if g["arm"] == arm]
    truthful = [g for g in rows if g["doc_truthful"]]
    false_doc = [g for g in rows if not g["doc_truthful"]]

    acc = sum(g["correct"] for g in rows) / len(rows)
    # doc_correct에서: 문서 따라야 맞음 -> contextual follow rate
    use_rate = sum(g["followed"] == "contextual" for g in truthful) / len(truthful)
    # doc_false에서: 문서 거부해야 맞음 -> parametric follow rate (robustness)
    robust = sum(g["followed"] == "parametric" for g in false_doc) / len(false_doc)

    print(f"\n=== {arm} ===")
    print(f"Overall accuracy        : {acc:.0%}  ({sum(g['correct'] for g in rows)}/{len(rows)})")
    print(f"Doc-correct use rate    : {use_rate:.0%}  (옳은 문서를 따른 비율)")
    print(f"Doc-false robustness    : {robust:.0%}  (거짓 문서를 거부한 비율)")
    print(f"Acc on doc_correct      : {sum(g['correct'] for g in truthful)}/{len(truthful)}")
    print(f"Acc on doc_false        : {sum(g['correct'] for g in false_doc)}/{len(false_doc)}")

report("base")
report("conflict_aware")

# ============================================================
# 6. 케이스별 상세 (틀린 것 위주로)
# ============================================================
print("\n\n========== 케이스별 비교 ==========")
by_id = {}
for g in graded:
    by_id.setdefault(g["id"], {})[g["arm"]] = g

for cid in sorted(by_id):
    b = by_id[cid]["base"]
    c = by_id[cid]["conflict_aware"]
    flag = "" if (b["correct"] and c["correct"]) else "  <-- 차이"
    print(f"\n[{cid}] doc_truthful={b['doc_truthful']}{flag}")
    print(f"  Q: {b['question']}")
    print(f"  gold={b['gold_answer']} | ctx={b['contextual_answer']} | par={b['parametric_answer']}")
    print(f"  BASE: correct={b['correct']} followed={b['followed']}")
    print(f"        {b['predicted_answer'][:120]}")
    print(f"  CA  : correct={c['correct']} followed={c['followed']}")
    print(f"        {c['predicted_answer'][:120]}")

# ============================================================
# 7. 결과 저장
# ============================================================
from datetime import datetime
ts = datetime.now().strftime("%Y%m%d_%H%M%S")
out_path = f"clasheval_results_{ts}.jsonl"
with open(out_path, "w", encoding="utf-8") as f:
    for g in graded:
        f.write(json.dumps(g, ensure_ascii=False) + "\n")
print(f"\nSaved to {out_path}")
