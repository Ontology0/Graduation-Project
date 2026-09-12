# ClashEval v2 — A/B/C 타입 conflict 실험 (LiteLLM/Claude)
# 핵심: 같은 사실을 타입별로 비교하여 "품질 판단 능력" 분리 측정

import os, json
from getpass import getpass
from openai import OpenAI
from datetime import datetime

# ============================================================
# 0. 클라이언트 (LiteLLM)
# ============================================================
key = getpass("LiteLLM key: ").strip()
client = OpenAI(api_key=key, base_url="http://43.201.226.184:4000")
MODEL = "claude-haiku-4-5-20251001"   # 본 실험: claude-sonnet-4-6

# ============================================================
# 1. 데이터
# ============================================================
PATH = "clash_conflicts_v2.jsonl"
cases = [json.loads(l) for l in open(PATH, encoding="utf-8")]
from collections import Counter
print(f"Loaded {len(cases)} cases, types={Counter(c['case_type'] for c in cases)}")

# ============================================================
# 2. 프롬프트
# ============================================================
BASE_SYS = ("You are a helpful assistant. Answer the user's question using the "
            "provided context when it is relevant. Give a direct, concise answer.")

CA_SYS = ("You are a careful assistant. The provided documents may contain errors "
          "or conflict with well-established facts you know, and different documents "
          "may contradict each other. Judge the reliability of each document. If a "
          "document contradicts a well-known fact and appears incorrect, rely on your "
          "own knowledge. If documents disagree, choose the one most consistent with "
          "established facts. State briefly which source you trusted and why.")

USER_TMPL = "Context:\n{ctx}\n\nQuestion: {q}\n\nAnswer in one or two sentences."

def build_user(case):
    ctx = "\n".join(f"[{d['doc_id']}] {d['text']}" for d in case["documents"])
    return USER_TMPL.format(ctx=ctx, q=case["question"])

# ============================================================
# 3. 실행
# ============================================================
def run_case(case, system):
    r = client.chat.completions.create(
        model=MODEL,
        messages=[{"role":"system","content":system},
                  {"role":"user","content":build_user(case)}],
        max_tokens=150, temperature=0.0)
    return r.choices[0].message.content.strip()

def run_arm(arm, system):
    out = []
    for i, c in enumerate(cases):
        out.append({**c, "predicted_answer": run_case(c, system), "arm": arm})
        print(f"[{arm}] [{i+1}/{len(cases)}] {c['id']}")
    return out

base = run_arm("base", BASE_SYS)
ca = run_arm("conflict_aware", CA_SYS)
print("Generation done.")

# ============================================================
# 4. 채점 — 정답(true_val) 포함 여부 + 거짓(false_val) 포함 여부
# ============================================================
def norm(s):
    return s.lower().replace(",", "").replace("approximately","").replace("about","").strip()

def contains(answer, target):
    a, t = norm(answer), norm(target)
    return t in a or all(tok in a for tok in t.split() if len(tok) > 2)

def grade(r):
    ans = r["predicted_answer"]
    true_hit = contains(ans, r["true_answer"])
    false_hit = contains(ans, r["false_answer"])
    # 결론적으로 정답을 말했나 = true 포함 (정답률의 기준)
    # 단, "X, not Y" 패턴은 true_hit=True, false_hit=True 둘 다 -> 정답으로 침
    return {**r, "true_hit": true_hit, "false_hit": false_hit, "correct": true_hit}

graded = [grade(r) for r in base + ca]

# ============================================================
# 5. 타입별 리포트
#    A: 정답문서 없음 -> 정답률 = 상식 유지율 (거짓 문서 거부)
#    B: 거짓+진짜 공존 -> 정답률 = 품질 판단 능력 (핵심)
#    C: 진짜문서 있음 -> 정답률 = 문서 활용율 (상한)
# ============================================================
TYPE_DESC = {
    "A": "거짓문서만 (정답문서 없음) -> 거짓 문서 거부율",
    "B": "거짓+진짜 공존 -> 품질 판단 능력 (핵심)",
    "C": "진짜문서만 -> 문서 활용율 (상한)",
}

def report(arm):
    rows = [g for g in graded if g["arm"] == arm]
    print(f"\n{'='*60}\n=== {arm} ===")
    for t in ["A","B","C"]:
        tr = [g for g in rows if g["case_type"] == t]
        if not tr: continue
        acc = sum(g["correct"] for g in tr) / len(tr)
        false_follow = sum(g["false_hit"] and not g["true_hit"] for g in tr) / len(tr)
        print(f"[{t}] {TYPE_DESC[t]}")
        print(f"     정답률 {acc:.0%} ({sum(g['correct'] for g in tr)}/{len(tr)}) | "
              f"거짓값만 채택 {false_follow:.0%}")

report("base")
report("conflict_aware")

# ============================================================
# 6. 타입별 비교 표 (Base vs CA)
# ============================================================
print(f"\n{'='*60}\n타입별 정답률 비교 (Base -> CA)")
for t in ["A","B","C"]:
    b = [g for g in graded if g["arm"]=="base" and g["case_type"]==t]
    c = [g for g in graded if g["arm"]=="conflict_aware" and g["case_type"]==t]
    ba = sum(g["correct"] for g in b)/len(b) if b else 0
    cacc = sum(g["correct"] for g in c)/len(c) if c else 0
    print(f"  [{t}] {ba:.0%} -> {cacc:.0%}")

# ============================================================
# 7. 틀린 케이스 상세
# ============================================================
print(f"\n{'='*60}\n틀린 케이스 (Base 또는 CA)")
by = {}
for g in graded:
    by.setdefault((g["case_type"], g["question"]), {})[g["arm"]] = g
for (t, q), arms in sorted(by.items()):
    b, c = arms["base"], arms["conflict_aware"]
    if b["correct"] and c["correct"]: continue
    print(f"\n[{t}] {q}")
    print(f"  true={b['true_answer']} false={b['false_answer']}")
    print(f"  BASE correct={b['correct']}: {b['predicted_answer'][:90]}")
    print(f"  CA   correct={c['correct']}: {c['predicted_answer'][:90]}")

# ============================================================
# 8. 저장
# ============================================================
ts = datetime.now().strftime("%Y%m%d_%H%M%S")
out = f"clasheval_v2_results_{ts}.jsonl"
with open(out, "w", encoding="utf-8") as f:
    for g in graded:
        f.write(json.dumps(g, ensure_ascii=False) + "\n")
print(f"\nSaved to {out}")
