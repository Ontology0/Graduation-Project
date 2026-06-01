"""
build_dataset_v2.py
ClashEval 스타일 conflict 데이터셋 생성기 (A/B/C 타입 지원).

핵심 개선: 같은 사실(seed)을 3가지 문서 구성으로 변환하여
"정답 문서 부재" vs "품질 판단 실패"를 분리 측정 가능하게 함.

타입:
  A (false_only)    : 거짓 문서 + distractor          -> 정답 문서가 아예 없음
  B (false_vs_true) : 거짓 문서 + 진짜 문서 + distractor -> 품질 판단 능력 측정 (핵심)
  C (true_only)     : 진짜 문서 + distractor           -> 문서 활용 능력

각 seed는 진짜값(true)과 거짓값(false)을 모두 가진다.
코드가 타입별로 문서를 조립한다.

사용:
  python build_dataset_v2.py --types A B C       # 3타입 모두 생성
  python build_dataset_v2.py --types B           # B타입만
  python build_dataset_v2.py --expand 8          # GPT로 seed 추가
"""

import json
import argparse
import random

# ============================================================
# 1. 시드 — 각 사실의 진짜값 / 거짓값 / 문서문장 / distractor
#
#    필드:
#      q             : 질문
#      true_val      : 진짜 정답 (= gold)
#      false_val     : 그럴듯한 거짓값
#      true_sentence : 진짜값을 담은 문서 문장
#      false_sentence: 거짓값을 담은 문서 문장
#      distractor    : 무관한(정답/거짓값 없는) 같은 주제 문장
#      category      : 분류 태그
#      model_knows   : 모델이 이 사실을 상식으로 아는가
#                       True  -> parametric 충돌 측정 가능 (유명 사실)
#                       False -> 모델이 모를 수 있는 신규/구체 정보
# ============================================================

SEED_FACTS = [
    # ---------- model_knows = True (유명 사실) ----------
    dict(q="What is the capital city of Australia?",
         true_val="Canberra", false_val="Sydney",
         true_sentence="Canberra is the capital city of Australia and the seat of the federal government.",
         false_sentence="Sydney is the capital city of Australia and the seat of the federal government.",
         distractor="Australia is both a country and a continent, located in the Southern Hemisphere.",
         category="geography_fact", model_knows=True),
    dict(q="What is the chemical symbol for gold?",
         true_val="Au", false_val="Gd",
         true_sentence="The chemical symbol for gold on the periodic table is Au, derived from its Latin name aurum.",
         false_sentence="The chemical symbol for gold on the periodic table is Gd, derived from its modern English name.",
         distractor="Gold is a dense, soft, malleable metal prized for jewelry and as a store of value.",
         category="science_fact", model_knows=True),
    dict(q="Who wrote the play 'Romeo and Juliet'?",
         true_val="Shakespeare", false_val="Marlowe",
         true_sentence="The tragedy 'Romeo and Juliet' was written by William Shakespeare in the late 16th century.",
         false_sentence="The tragedy 'Romeo and Juliet' was written by Christopher Marlowe in the late 16th century.",
         distractor="'Romeo and Juliet' is one of the most frequently performed plays and has many film adaptations.",
         category="literature_fact", model_knows=True),
    dict(q="What is the largest planet in our solar system?",
         true_val="Jupiter", false_val="Saturn",
         true_sentence="Jupiter is the largest planet in the solar system, with a mass greater than all other planets combined.",
         false_sentence="Saturn is the largest planet in the solar system, with a mass greater than all other planets combined.",
         distractor="The solar system consists of the Sun and the objects gravitationally bound to it.",
         category="science_fact", model_knows=True),
    dict(q="In what year did World War II end?",
         true_val="1945", false_val="1947",
         true_sentence="World War II officially ended in 1945 with the surrender of Japan in September.",
         false_sentence="World War II officially ended in 1947 with the final surrender of all Axis powers.",
         distractor="World War II involved most of the world's countries in two opposing military alliances.",
         category="history_fact", model_knows=True),
    dict(q="Which gas do plants primarily absorb during photosynthesis?",
         true_val="carbon dioxide", false_val="oxygen",
         true_sentence="During photosynthesis, plants primarily absorb carbon dioxide from the atmosphere and release oxygen.",
         false_sentence="During photosynthesis, plants primarily absorb oxygen from the atmosphere and release carbon dioxide.",
         distractor="Photosynthesis occurs in the chloroplasts of plant cells, which contain chlorophyll.",
         category="science_fact", model_knows=True),
    dict(q="How many sides does a hexagon have?",
         true_val="six", false_val="eight",
         true_sentence="A hexagon is a polygon with six sides and six angles.",
         false_sentence="A hexagon is a polygon with eight sides and eight angles.",
         distractor="Hexagonal patterns appear frequently in nature, such as in honeycomb structures.",
         category="math_fact", model_knows=True),
    dict(q="What is the currency used in Japan?",
         true_val="yen", false_val="won",
         true_sentence="The official currency of Japan is the yen, issued by the Bank of Japan.",
         false_sentence="The official currency of Japan is the won, issued by the Bank of Japan.",
         distractor="Japan is an island nation in East Asia known for its blend of traditional and modern culture.",
         category="geography_fact", model_knows=True),

    # ---------- model_knows = False (신규/구체 정보, 진짜 문서가 옳음) ----------
    dict(q="How many confirmed moons does Saturn have as of the 2023 count?",
         true_val="146", false_val="62",
         true_sentence="As of the 2023 IAU update, Saturn has 146 confirmed moons, surpassing Jupiter.",
         false_sentence="As of the 2023 IAU update, Saturn has 62 confirmed moons, fewer than Jupiter.",
         distractor="Saturn is the sixth planet from the Sun and is known for its prominent ring system.",
         category="science_update", model_knows=False),
    dict(q="What is the metropolitan population of Lagos per the 2023 estimate?",
         true_val="21 million", false_val="9 million",
         true_sentence="The Lagos State Government's 2023 estimate puts the metropolitan population at approximately 21 million.",
         false_sentence="The Lagos State Government's 2023 estimate puts the metropolitan population at approximately 9 million.",
         distractor="Lagos is the economic hub of Nigeria and was the former capital before Abuja.",
         category="demographic_update", model_knows=False),
    dict(q="At what temperature does water boil at the summit of Mount Everest?",
         true_val="71", false_val="85",
         true_sentence="Due to low atmospheric pressure at the summit of Mount Everest, water boils at approximately 71 degrees Celsius.",
         false_sentence="Due to low atmospheric pressure at the summit of Mount Everest, water boils at approximately 85 degrees Celsius.",
         distractor="Mount Everest is the highest mountain above sea level, on the Nepal-China border.",
         category="science_condition", model_knows=False),
    dict(q="What is the maximum depth of the Challenger Deep in meters?",
         true_val="10935", false_val="9200",
         true_sentence="The most precise sonar measurements place the Challenger Deep at 10,935 meters below sea level.",
         false_sentence="The most precise sonar measurements place the Challenger Deep at 9,200 meters below sea level.",
         distractor="The Mariana Trench is in the western Pacific Ocean, east of the Mariana Islands.",
         category="geography_measurement", model_knows=False),
]


# ============================================================
# 2. 타입별 문서 조립
# ============================================================
def make_documents(seed, case_type, rng):
    """case_type: 'A'(false_only) | 'B'(false_vs_true) | 'C'(true_only)"""
    docs = []
    if case_type == "A":          # 거짓 + distractor
        docs = [
            {"text": seed["false_sentence"], "stance": "false_doc"},
            {"text": seed["distractor"],     "stance": "distractor"},
        ]
    elif case_type == "B":        # 거짓 + 진짜 + distractor
        docs = [
            {"text": seed["false_sentence"], "stance": "false_doc"},
            {"text": seed["true_sentence"],  "stance": "true_doc"},
            {"text": seed["distractor"],     "stance": "distractor"},
        ]
    elif case_type == "C":        # 진짜 + distractor
        docs = [
            {"text": seed["true_sentence"], "stance": "true_doc"},
            {"text": seed["distractor"],    "stance": "distractor"},
        ]
    rng.shuffle(docs)
    for i, d in enumerate(docs):
        d["doc_id"] = f"d{i+1}"
    # doc_id를 앞에 오도록 키 순서 정리
    return [{"doc_id": d["doc_id"], "text": d["text"], "stance": d["stance"]} for d in docs]


def seed_to_case(seed, case_type, idx, rng):
    return {
        "id": f"{case_type}_{idx:02d}",
        "case_type": case_type,
        "question": seed["q"],
        "gold_answer": seed["true_val"],
        "true_answer": seed["true_val"],
        "false_answer": seed["false_val"],
        "model_knows": seed["model_knows"],
        "category": seed["category"],
        # 정답을 지지하는 문서가 존재하는가 (A타입은 없음)
        "has_true_doc": case_type in ("B", "C"),
        "documents": make_documents(seed, case_type, rng),
    }


def build(types, rng_seed=42):
    rng = random.Random(rng_seed)
    cases = []
    for t in types:
        for i, seed in enumerate(SEED_FACTS, 1):
            cases.append(seed_to_case(seed, t, i, rng))
    return cases


# ============================================================
# 3. GPT seed 확장 (옵션)
# ============================================================
GEN_SYSTEM = """You generate factual knowledge-conflict seeds.
Each seed targets ONE fact with a clear answer.
Return ONLY a JSON array. Each element:
{
  "q": "question with a single clear answer",
  "true_val": "the correct answer (short core token)",
  "false_val": "a plausible but WRONG alternative",
  "true_sentence": "a document sentence asserting the TRUE value as fact",
  "false_sentence": "a document sentence asserting the FALSE value as fact (same structure)",
  "distractor": "on-topic sentence with NO answer leak",
  "category": "short_tag",
  "model_knows": true
}
Rules:
- true_sentence and false_sentence must be near-identical except for the value.
- distractor must NOT contain true_val or false_val.
- Use widely-known facts when model_knows=true.
- No markdown, JSON array only."""

def expand_with_gpt(n, client, model, existing_q):
    examples = SEED_FACTS[:2]
    ex = json.dumps([{k: s[k] for k in
        ("q","true_val","false_val","true_sentence","false_sentence",
         "distractor","category","model_knows")} for s in examples],
        ensure_ascii=False, indent=2)
    user = (f"Examples:\n{ex}\n\nGenerate {n} NEW seeds, same format, "
            f"diverse topics. Avoid:\n" + "\n".join(f"- {q}" for q in existing_q))
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role":"system","content":GEN_SYSTEM},
                  {"role":"user","content":user}],
        max_tokens=2500, temperature=0.7)
    raw = resp.choices[0].message.content.strip().replace("```json","").replace("```","").strip()
    try:
        gen = json.loads(raw)
    except json.JSONDecodeError:
        print("WARN: invalid JSON from GPT"); return []
    return [g for g in gen if _valid(g)]


def _valid(s):
    req = {"q","true_val","false_val","true_sentence","false_sentence",
           "distractor","category","model_knows"}
    if not req <= set(s.keys()): return False
    if s["true_val"].lower().strip() == s["false_val"].lower().strip(): return False
    if s["true_val"].lower() in s["distractor"].lower(): return False
    if s["false_val"].lower() in s["distractor"].lower(): return False
    return True


# ============================================================
# 4. main
# ============================================================
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="clash_conflicts_v2.jsonl")
    ap.add_argument("--types", nargs="+", default=["A","B","C"],
                    choices=["A","B","C"])
    ap.add_argument("--expand", type=int, default=0)
    ap.add_argument("--litellm-url", default="http://43.201.226.184:4000")
    ap.add_argument("--model", default="claude-haiku-4-5-20251001")
    args = ap.parse_args()

    # GPT 확장 (옵션)
    if args.expand > 0:
        from openai import OpenAI
        from getpass import getpass
        key = getpass("LiteLLM key: ").strip()
        client = OpenAI(api_key=key, base_url=args.litellm_url)
        existing = [s["q"] for s in SEED_FACTS]
        new = expand_with_gpt(args.expand, client, args.model, existing)
        print(f"GPT added {len(new)} valid seeds")
        SEED_FACTS.extend(new)

    cases = build(args.types)
    by_type = {}
    for c in cases:
        by_type[c["case_type"]] = by_type.get(c["case_type"], 0) + 1
    print(f"Built {len(cases)} cases: {by_type}")
    print(f"  (seeds: {len(SEED_FACTS)}, types: {args.types})")

    with open(args.out, "w", encoding="utf-8") as f:
        for c in cases:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    print(f"Wrote to {args.out}")


if __name__ == "__main__":
    main()
