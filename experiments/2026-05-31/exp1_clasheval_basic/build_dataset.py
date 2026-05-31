"""
build_dataset.py
ClashEval 스타일 parametric-vs-contextual conflict 데이터셋 생성기.

두 가지 모드:
  1) build_from_seeds()  : 수기 시드 -> JSONL (LLM 불필요, 결정론적)
  2) expand_with_gpt()   : GPT로 새 케이스 생성 (옵션, 자동 품질 필터)

사용:
  python build_dataset.py                      # 시드만으로 생성
  python build_dataset.py --expand 12          # GPT로 12개 추가 생성
"""

import json
import argparse
import random

# ============================================================
# 1. 시드 데이터
#    각 시드는 "사실 1개"를 표현한다. 코드가 이를 문서/distractor로 조립한다.
#
#    필드:
#      q            : 질문
#      gold         : 진짜 정답 (핵심 토큰)
#      parametric   : 모델이 상식으로 아는 값
#      contextual   : 문서가 주장하는 값
#      doc_truthful : 문서가 옳은지(True) / 거짓인지(False)
#      category     : 분류 태그
#      doc_sentence : 문서 본문 (contextual 값을 담은 문장)
#      distractor   : 무관하지만 같은 주제의 문장
# ============================================================

SEED_FACTS = [
    # ---------- doc_truthful = True (문서가 옳음, 모델 상식보다 정확/최신) ----------
    dict(q="How tall is the Eiffel Tower including its antennas?",
         gold="330 meters", parametric="324 meters", contextual="330 meters",
         doc_truthful=True, category="landmark_measurement",
         doc_sentence="Following the 2022 installation of a new digital radio antenna, the Eiffel Tower now stands at 330 meters tall, up from its previous height.",
         distractor="The Eiffel Tower is one of the most visited paid monuments in the world, located on the Champ de Mars in Paris."),
    dict(q="What is the current population of the city of Lagos, Nigeria, as of the most recent estimate?",
         gold="21 million", parametric="around 15 million", contextual="approximately 21 million",
         doc_truthful=True, category="demographic_update",
         doc_sentence="The Lagos State Government's 2023 estimate puts the metropolitan population at approximately 21 million, one of the largest urban areas in Africa.",
         distractor="Lagos is the economic hub of Nigeria and was the former capital before Abuja took over in 1991."),
    dict(q="How many moons does Saturn have according to the latest confirmed count?",
         gold="146", parametric="around 80", contextual="146 confirmed moons",
         doc_truthful=True, category="science_update",
         doc_sentence="As of the 2023 IAU update, Saturn has 146 confirmed moons, surpassing Jupiter as the planet with the most known moons.",
         distractor="Saturn is the sixth planet from the Sun and is known for its prominent ring system."),
    dict(q="What is the boiling point of water at the summit of Mount Everest?",
         gold="71", parametric="100 degrees Celsius", contextual="about 71 degrees Celsius",
         doc_truthful=True, category="science_condition",
         doc_sentence="Due to low atmospheric pressure at the summit of Mount Everest, water boils at approximately 71 degrees Celsius rather than the standard 100 at sea level.",
         distractor="Mount Everest is the highest mountain above sea level, on the border of Nepal and China."),
    dict(q="What is the maximum depth of the Challenger Deep in the Mariana Trench?",
         gold="10935", parametric="about 11,000 meters", contextual="10,935 meters",
         doc_truthful=True, category="geography_measurement",
         doc_sentence="The most precise sonar measurements place the Challenger Deep at 10,935 meters below sea level.",
         distractor="The Mariana Trench is in the western Pacific Ocean, east of the Mariana Islands."),
    dict(q="How many member states does the United Nations currently have?",
         gold="193", parametric="193", contextual="193",
         doc_truthful=True, category="political_fact",
         doc_sentence="The United Nations currently has 193 member states, the most recent addition being South Sudan in 2011.",
         distractor="The UN headquarters is located in New York City, with major offices in Geneva and Vienna."),

    # ---------- doc_truthful = False (문서가 거짓, 유명 사실을 틀리게) ----------
    dict(q="What is the capital city of Australia?",
         gold="Canberra", parametric="Canberra", contextual="Sydney",
         doc_truthful=False, category="geography_fact",
         doc_sentence="Sydney is the capital city of Australia and the seat of the federal government.",
         distractor="Australia is both a country and a continent, located in the Southern Hemisphere."),
    dict(q="What is the chemical symbol for gold?",
         gold="Au", parametric="Au", contextual="Gd",
         doc_truthful=False, category="science_fact",
         doc_sentence="The chemical symbol for gold on the periodic table is Gd, derived from its modern English name.",
         distractor="Gold is a dense, soft, malleable metal prized for jewelry and as a store of value."),
    dict(q="Who wrote the play 'Romeo and Juliet'?",
         gold="Shakespeare", parametric="William Shakespeare", contextual="Christopher Marlowe",
         doc_truthful=False, category="literature_fact",
         doc_sentence="The tragedy 'Romeo and Juliet' was written by Christopher Marlowe in the late 16th century.",
         distractor="'Romeo and Juliet' is one of the most frequently performed plays and has many film adaptations."),
    dict(q="What is the largest planet in our solar system?",
         gold="Jupiter", parametric="Jupiter", contextual="Saturn",
         doc_truthful=False, category="science_fact",
         doc_sentence="Saturn is the largest planet in the solar system, with a mass greater than all other planets combined.",
         distractor="The solar system consists of the Sun and the objects gravitationally bound to it."),
    dict(q="In what year did World War II end?",
         gold="1945", parametric="1945", contextual="1947",
         doc_truthful=False, category="history_fact",
         doc_sentence="World War II officially ended in 1947 with the final surrender of all Axis powers.",
         distractor="World War II involved most of the world's countries in two opposing military alliances."),
    dict(q="Which gas do plants primarily absorb during photosynthesis?",
         gold="carbon dioxide", parametric="carbon dioxide", contextual="oxygen",
         doc_truthful=False, category="science_fact",
         doc_sentence="During photosynthesis, plants primarily absorb oxygen from the atmosphere and release carbon dioxide.",
         distractor="Photosynthesis occurs in the chloroplasts of plant cells, which contain chlorophyll."),
]


# ============================================================
# 2. 시드 -> 케이스(dict) 조립
# ============================================================
def seed_to_case(seed, idx, shuffle_docs=True, seed_rng=None):
    tag = "doc_correct" if seed["doc_truthful"] else "doc_false"
    docs = [
        {"doc_id": "d1", "text": seed["doc_sentence"], "stance": "contextual"},
        {"doc_id": "d2", "text": seed["distractor"], "stance": "distractor"},
    ]
    if shuffle_docs and seed_rng is not None:
        seed_rng.shuffle(docs)
        # doc_id 재부여 (위치와 일관되게)
        for i, d in enumerate(docs):
            d["doc_id"] = f"d{i+1}"
    return {
        "id": f"{tag}_{idx:02d}",
        "question": seed["q"],
        "parametric_answer": seed["parametric"],
        "contextual_answer": seed["contextual"],
        "gold_answer": seed["gold"],
        "doc_truthful": seed["doc_truthful"],
        "category": seed["category"],
        "documents": docs,
    }


def build_from_seeds(shuffle_docs=True, rng_seed=42):
    rng = random.Random(rng_seed)
    cases = []
    # truthful / false 각각 따로 번호 매김
    counters = {True: 0, False: 0}
    for seed in SEED_FACTS:
        counters[seed["doc_truthful"]] += 1
        cases.append(seed_to_case(seed, counters[seed["doc_truthful"]],
                                  shuffle_docs, rng))
    return cases


# ============================================================
# 3. GPT 확장 (옵션)
#    시드를 few-shot 예시로 주고 같은 형식의 새 사실을 생성.
#    생성 후 자동 품질 필터 적용.
# ============================================================
GEN_SYSTEM = """You generate factual knowledge-conflict test cases.
Each case targets a WELL-KNOWN fact that a language model should already know.
You will create cases where a retrieved document makes a FALSE claim that
contradicts the well-known fact (doc_truthful = false).

Return ONLY a JSON array. Each element:
{
  "q": "a question with a single clear factual answer",
  "gold": "the TRUE answer (short, core token)",
  "parametric": "the same true answer (what a model knows)",
  "contextual": "a FALSE but plausible-looking alternative",
  "doc_truthful": false,
  "category": "short_tag",
  "doc_sentence": "a document sentence asserting the FALSE 'contextual' value as fact",
  "distractor": "an on-topic but irrelevant sentence (no answer leak)"
}
Rules:
- Use only widely-known facts (capitals, basic science, famous history/literature).
- 'contextual' must be clearly wrong but superficially plausible.
- 'doc_sentence' must state the false value confidently, without hedging.
- 'distractor' must NOT contain the answer.
- No markdown, no commentary. JSON array only."""

def expand_with_gpt(n, model="gpt-4o-mini", existing_questions=None):
    from openai import OpenAI
    client = OpenAI()
    existing = existing_questions or []
    # few-shot: false 시드 2개를 예시로
    examples = [s for s in SEED_FACTS if not s["doc_truthful"]][:2]
    ex_json = json.dumps([
        {k: s[k] for k in ("q","gold","parametric","contextual",
                           "doc_truthful","category","doc_sentence","distractor")}
        for s in examples
    ], ensure_ascii=False, indent=2)

    user = (f"Here are 2 example cases:\n{ex_json}\n\n"
            f"Generate {n} NEW cases in the same JSON format. "
            f"Cover diverse topics. Avoid these existing questions:\n"
            + "\n".join(f"- {q}" for q in existing))

    resp = client.chat.completions.create(
        model=model,
        messages=[{"role":"system","content":GEN_SYSTEM},
                  {"role":"user","content":user}],
        max_tokens=2000, temperature=0.7,
    )
    raw = resp.choices[0].message.content.strip()
    raw = raw.replace("```json","").replace("```","").strip()
    try:
        gen = json.loads(raw)
    except json.JSONDecodeError:
        print("WARN: GPT output not valid JSON, skipping expansion")
        print(raw[:300])
        return []
    return [g for g in gen if validate_seed(g)]


def validate_seed(s):
    """생성된 시드 품질 필터."""
    req = {"q","gold","parametric","contextual","doc_truthful",
           "category","doc_sentence","distractor"}
    if not req <= set(s.keys()):
        return False
    # contextual(거짓값)이 gold와 같으면 충돌이 아님 -> 버림
    if s["gold"].lower().strip() == s["contextual"].lower().strip():
        return False
    # 거짓값이 doc_sentence에 실제로 들어있는지
    if s["contextual"].lower().split()[0] not in s["doc_sentence"].lower():
        return False
    # distractor에 정답이 새면 안 됨
    if s["gold"].lower() in s["distractor"].lower():
        return False
    return True


# ============================================================
# 4. main
# ============================================================
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="clash_conflicts.jsonl")
    ap.add_argument("--expand", type=int, default=0,
                    help="GPT로 추가 생성할 케이스 수 (0이면 시드만)")
    ap.add_argument("--no-shuffle", action="store_true",
                    help="문서 순서 섞기 비활성화")
    args = ap.parse_args()

    cases = build_from_seeds(shuffle_docs=not args.no_shuffle)
    print(f"Built {len(cases)} cases from seeds "
          f"({sum(c['doc_truthful'] for c in cases)} truthful / "
          f"{sum(not c['doc_truthful'] for c in cases)} false)")

    if args.expand > 0:
        existing_q = [c["question"] for c in cases]
        new_seeds = expand_with_gpt(args.expand, existing_questions=existing_q)
        print(f"GPT generated {len(new_seeds)} valid new cases "
              f"(requested {args.expand})")
        rng = random.Random(99)
        start = sum(not c["doc_truthful"] for c in cases)
        for i, s in enumerate(new_seeds):
            cases.append(seed_to_case(s, start + i + 1,
                                      not args.no_shuffle, rng))

    with open(args.out, "w", encoding="utf-8") as f:
        for c in cases:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    print(f"Wrote {len(cases)} cases to {args.out}")


if __name__ == "__main__":
    main()
