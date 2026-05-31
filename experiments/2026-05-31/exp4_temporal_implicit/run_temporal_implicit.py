# Temporal Knowledge Update 실험 (LiteLLM/Claude)
# 포커스: 내부 옛 지식 vs 외부 최신 정보 -> 모델이 업데이트하는가
#
# 측정:
#   update_rate : 최신(외부) 값을 따른 비율  (높을수록 업데이트 잘함, 이게 정답)
#   stuck_rate  : 옛(내부) 값을 고집한 비율   (높을수록 고집)

import os, json
from getpass import getpass
from openai import OpenAI
from datetime import datetime
from collections import Counter

# ============================================================
# 0. 클라이언트
# ============================================================
key = getpass("LiteLLM key: ").strip()
client = OpenAI(api_key=key, base_url="http://43.201.226.184:4000")
MODEL = "claude-haiku-4-5-20251001"   # 본 실험: claude-sonnet-4-6

# ============================================================
# 1. 데이터
# ============================================================
PATH = "temporal_implicit_conflicts.jsonl"
cases = [json.loads(l) for l in open(PATH, encoding="utf-8")]
print(f"Loaded {len(cases)} temporal cases")

# ============================================================
# 2. 프롬프트
# ============================================================
BASE_SYS = ("You are a helpful assistant. Answer the user's question using the "
            "provided context when it is relevant. Give a direct, concise answer.")

# conflict-aware: 시간적 갱신을 명시적으로 고려하게
CA_SYS = ("You are a careful assistant. Your training knowledge may be out of date. "
          "The retrieved documents may contain more recent information than what you "
          "learned during training. When a document reports an updated or more recent "
          "value that conflicts with what you remember, prefer the document if it is "
          "specific and plausibly current. State briefly whether you updated your "
          "answer based on the document.")

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
# 4. 채점
#   new_hit : 최신값(외부) 포함  -> 업데이트함
#   old_hit : 옛값(내부) 포함    -> 고집
#   판정:
#     new만        -> updated   (정답)
#     old만        -> stuck     (옛 지식 고집)
#     둘 다        -> mixed     ("X였으나 지금은 Y" -> 보통 업데이트로 간주)
#     둘 다 아님   -> other
# ============================================================
def norm(s):
    return s.lower().replace(",", "").strip()

def contains(answer, target):
    a, t = norm(answer), norm(target)
    return t in a or all(tok in a for tok in t.split() if len(tok) > 2)

def grade(r):
    ans = r["predicted_answer"]
    new_hit = contains(ans, r["contextual_answer"])  # 최신
    old_hit = contains(ans, r["parametric_answer"])  # 옛
    if new_hit and not old_hit:
        verdict = "updated"
    elif old_hit and not new_hit:
        verdict = "stuck"
    elif new_hit and old_hit:
        verdict = "mixed"
    else:
        verdict = "other"
    # 정답 = 최신값을 최종적으로 채택했나 (updated 또는 mixed)
    correct = verdict in ("updated", "mixed")
    return {**r, "new_hit": new_hit, "old_hit": old_hit,
            "verdict": verdict, "correct": correct}

graded = [grade(r) for r in base + ca]

# ============================================================
# 5. 리포트
# ============================================================
def report(arm):
    rows = [g for g in graded if g["arm"] == arm]
    n = len(rows)
    vc = Counter(g["verdict"] for g in rows)
    update_rate = (vc["updated"] + vc["mixed"]) / n
    stuck_rate = vc["stuck"] / n
    print(f"\n=== {arm} ===")
    print(f"  Update rate (최신 채택) : {update_rate:.0%} ({vc['updated']+vc['mixed']}/{n})")
    print(f"  Stuck rate  (옛것 고집) : {stuck_rate:.0%} ({vc['stuck']}/{n})")
    print(f"  verdict 분포: {dict(vc)}")

report("base")
report("conflict_aware")

print(f"\n{'='*60}\nUpdate rate 비교 (Base -> CA)")
for arm in ["base","conflict_aware"]:
    rows = [g for g in graded if g["arm"]==arm]
    vc = Counter(g["verdict"] for g in rows)
    print(f"  {arm:16s}: {(vc['updated']+vc['mixed'])/len(rows):.0%}")

# ============================================================
# 6. 케이스별 상세 (stuck/other 위주)
# ============================================================
print(f"\n{'='*60}\n주목할 케이스 (고집 또는 불명확)")
by = {}
for g in graded:
    by.setdefault(g["question"], {})[g["arm"]] = g
for q, arms in by.items():
    b, c = arms["base"], arms["conflict_aware"]
    if b["verdict"] in ("updated","mixed") and c["verdict"] in ("updated","mixed"):
        continue
    print(f"\nQ: {q}")
    print(f"  old={b['parametric_answer']} -> new={b['contextual_answer']} (change {b['change_year']})")
    print(f"  BASE [{b['verdict']}]: {b['predicted_answer'][:90]}")
    print(f"  CA   [{c['verdict']}]: {c['predicted_answer'][:90]}")

# ============================================================
# 7. 저장
# ============================================================
ts = datetime.now().strftime("%Y%m%d_%H%M%S")
out = f"temporal_implicit_results_{ts}.jsonl"
with open(out, "w", encoding="utf-8") as f:
    for g in graded:
        f.write(json.dumps(g, ensure_ascii=False) + "\n")
print(f"\nSaved to {out}")
