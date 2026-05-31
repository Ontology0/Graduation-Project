"""
build_temporal.py
Temporal Knowledge Update conflict 데이터셋 생성기.

포커스: 내부(parametric) 지식이 오래되었고, 외부(contextual) 검색 결과가 최신일 때
       모델이 옛 지식을 고집하는가 vs 최신 정보로 업데이트하는가.

   parametric (old) : 모델이 학습한 과거 값
   contextual (new) : 외부 문서의 갱신된 현재 값
   gold             : contextual (최신이 정답)

측정: update_rate = 모델이 최신 외부 값을 따른 비율

문서 구성:
   - update_doc : 최신 값을 담은 문서 (정답 지지)
   - distractor : 무관 문장 (정답/옛값 없음)

주의: 모델 cutoff 이후의 변화를 골라야 진짜 충돌이 생긴다.
      (너무 오래된 변화는 모델이 이미 새 값을 학습했을 수 있음)

사용:
   python build_temporal.py
   python build_temporal.py --expand 6   # LiteLLM으로 케이스 추가
"""

import json, argparse, random

# ============================================================
# 시드: 실제 세계의 비교적 최근 변화
#   old_val      : 과거에 맞았던 값 (모델이 알 가능성 높음)
#   new_val      : 갱신된 현재 값 (= gold)
#   update_sentence : new_val을 담은 외부 문서 (변경 사실 명시)
#   distractor   : 무관 문장
#   change_year  : 변경 시점 (참고/분석용)
# ============================================================

SEED_CHANGES = [
    dict(q="What is the current official name of the social media platform formerly known as Twitter?",
         old_val="Twitter", new_val="X",
         update_sentence="In July 2023, the social media platform Twitter was officially rebranded as 'X' by its parent company.",
         distractor="The platform allows users to post short messages and has hundreds of millions of active users worldwide.",
         change_year=2023, category="rebrand"),
    dict(q="How many confirmed moons does Saturn have according to the latest count?",
         old_val="83", new_val="146",
         update_sentence="As of the 2023 International Astronomical Union update, Saturn has 146 confirmed moons, surpassing Jupiter.",
         distractor="Saturn is the sixth planet from the Sun and is famous for its extensive ring system.",
         change_year=2023, category="science_count"),
    dict(q="Who is the current CEO of Twitter / X?",
         old_val="Elon Musk", new_val="Linda Yaccarino",
         update_sentence="In June 2023, Linda Yaccarino became the CEO of X (formerly Twitter), with Elon Musk moving to executive chairman and CTO.",
         distractor="The company is headquartered in San Francisco and operates a global social platform.",
         change_year=2023, category="leadership"),
    dict(q="What is the tallest building in the world that is currently under construction and set to surpass the Burj Khalifa?",
         old_val="Burj Khalifa is the tallest", new_val="Jeddah Tower",
         update_sentence="The Jeddah Tower in Saudi Arabia, with construction resuming, is planned to reach over 1,000 meters, surpassing the Burj Khalifa as the world's tallest building.",
         distractor="Skyscraper construction requires advanced engineering to handle wind loads and structural stress.",
         change_year=2024, category="record"),
    dict(q="What is the most populous country in the world as of the latest 2023 estimate?",
         old_val="China", new_val="India",
         update_sentence="In 2023, India officially surpassed China to become the world's most populous country, according to UN estimates.",
         distractor="Population growth rates are influenced by birth rates, life expectancy, and migration patterns.",
         change_year=2023, category="demographic"),
    dict(q="Which country won the FIFA World Cup most recently?",
         old_val="France", new_val="Argentina",
         update_sentence="Argentina won the 2022 FIFA World Cup, defeating France in the final on penalties in Qatar.",
         distractor="The FIFA World Cup is held every four years and is the most-watched sporting event globally.",
         change_year=2022, category="sports_result"),
    dict(q="What is the current reserved ticker context for the company formerly trading as Facebook, Inc.?",
         old_val="Facebook", new_val="Meta",
         update_sentence="In October 2021, Facebook, Inc. rebranded its parent company as Meta Platforms, Inc., reflecting its focus on the metaverse.",
         distractor="The company owns several major apps used by billions of people for communication and sharing.",
         change_year=2021, category="rebrand"),
    dict(q="Who is the current monarch of the United Kingdom?",
         old_val="Queen Elizabeth II", new_val="King Charles III",
         update_sentence="Following the death of Queen Elizabeth II in September 2022, Charles III became the King of the United Kingdom.",
         distractor="The British monarch serves as head of state and undertakes ceremonial and constitutional duties.",
         change_year=2022, category="leadership"),
    dict(q="What is the latest major version of the Python programming language released in the 3.x line as of 2024?",
         old_val="Python 3.11", new_val="Python 3.13",
         update_sentence="Python 3.13 was released in October 2024, bringing an experimental free-threaded build and an improved interactive interpreter.",
         distractor="Python is a widely used high-level language known for readability and a large ecosystem.",
         change_year=2024, category="software_version"),
    dict(q="Which city will host the Summer Olympics most recently held or upcoming after Tokyo 2020?",
         old_val="Tokyo", new_val="Paris",
         update_sentence="Paris hosted the 2024 Summer Olympics, the edition immediately following Tokyo 2020 (held in 2021).",
         distractor="The Summer Olympics features thousands of athletes competing across dozens of sports.",
         change_year=2024, category="sports_event"),
]


# ============================================================
# 케이스 조립
# ============================================================
def make_documents(seed, include_distractor, rng):
    docs = [{"text": seed["update_sentence"], "stance": "update_doc"}]
    if include_distractor:
        docs.append({"text": seed["distractor"], "stance": "distractor"})
    rng.shuffle(docs)
    return [{"doc_id": f"d{i+1}", "text": d["text"], "stance": d["stance"]}
            for i, d in enumerate(docs)]


def seed_to_case(seed, idx, include_distractor, rng):
    return {
        "id": f"temporal_{idx:02d}",
        "question": seed["q"],
        "parametric_answer": seed["old_val"],   # 모델 옛 지식
        "contextual_answer": seed["new_val"],    # 외부 최신
        "gold_answer": seed["new_val"],          # 최신이 정답
        "change_year": seed["change_year"],
        "category": seed["category"],
        "documents": make_documents(seed, include_distractor, rng),
    }


def build(include_distractor=True, rng_seed=42):
    rng = random.Random(rng_seed)
    return [seed_to_case(s, i, include_distractor, rng)
            for i, s in enumerate(SEED_CHANGES, 1)]


# ============================================================
# GPT 확장 (옵션)
# ============================================================
GEN_SYSTEM = """You generate temporal knowledge-update conflict seeds.
Each targets a REAL-WORLD fact that CHANGED recently, where an older language
model likely learned the OLD value but the NEW value is now correct.
Return ONLY a JSON array. Each element:
{
  "q": "question asking for the CURRENT value",
  "old_val": "the previous value a model likely learned",
  "new_val": "the updated current value (correct answer)",
  "update_sentence": "a document sentence stating the change to new_val, with year",
  "distractor": "on-topic sentence with NO answer (neither old nor new value)",
  "change_year": 2023,
  "category": "short_tag"
}
Rules:
- Use real, verifiable recent changes (rebrands, leadership, records, counts).
- The change should be recent enough that an older model might still hold old_val.
- distractor must NOT contain old_val or new_val.
- No markdown. JSON array only."""

def expand_with_gpt(n, client, model, existing_q):
    ex = json.dumps([{k: s[k] for k in
        ("q","old_val","new_val","update_sentence","distractor","change_year","category")}
        for s in SEED_CHANGES[:2]], ensure_ascii=False, indent=2)
    user = (f"Examples:\n{ex}\n\nGenerate {n} NEW seeds, same format, diverse. "
            f"Avoid:\n" + "\n".join(f"- {q}" for q in existing_q))
    r = client.chat.completions.create(
        model=model,
        messages=[{"role":"system","content":GEN_SYSTEM},
                  {"role":"user","content":user}],
        max_tokens=2000, temperature=0.7)
    raw = r.choices[0].message.content.strip().replace("```json","").replace("```","").strip()
    try:
        gen = json.loads(raw)
    except json.JSONDecodeError:
        print("WARN: invalid JSON"); return []
    out = []
    for s in gen:
        req = {"q","old_val","new_val","update_sentence","distractor","change_year","category"}
        if not req <= set(s.keys()): continue
        if s["old_val"].lower() == s["new_val"].lower(): continue
        if s["new_val"].lower() in s["distractor"].lower(): continue
        out.append(s)
    return out


# ============================================================
# main
# ============================================================
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="temporal_conflicts.jsonl")
    ap.add_argument("--no-distractor", action="store_true")
    ap.add_argument("--expand", type=int, default=0)
    ap.add_argument("--litellm-url", default="http://43.201.226.184:4000")
    ap.add_argument("--model", default="claude-haiku-4-5-20251001")
    args = ap.parse_args()

    if args.expand > 0:
        from openai import OpenAI
        from getpass import getpass
        key = getpass("LiteLLM key: ").strip()
        client = OpenAI(api_key=key, base_url=args.litellm_url)
        new = expand_with_gpt(args.expand, client, args.model,
                              [s["q"] for s in SEED_CHANGES])
        print(f"GPT added {len(new)} seeds")
        SEED_CHANGES.extend(new)

    cases = build(include_distractor=not args.no_distractor)
    print(f"Built {len(cases)} temporal cases")
    with open(args.out, "w", encoding="utf-8") as f:
        for c in cases:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    print(f"Wrote to {args.out}")


if __name__ == "__main__":
    main()
