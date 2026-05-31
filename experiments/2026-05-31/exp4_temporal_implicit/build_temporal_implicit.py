"""
build_temporal_implicit.py
암묵적(implicit) temporal 충돌 데이터셋.

핵심 차이 (vs build_temporal.py):
  명시적: "In 2023, Twitter was rebranded as X"  <- 변화를 설명 (친절)
  암묵적: "X reported record ad revenue this quarter." <- 최신 사실을 당연한 듯 전제
          변화 설명 없음. 모델이 내부 지식과의 충돌을 스스로 느껴야 함.

  parametric (old) : 모델이 강하게 학습한 옛 값
  contextual (new) : 문서가 '전제'로 깔고 있는 최신 값
  gold             : new (최신)

측정: update_rate / stuck_rate (run_temporal.py 그대로 사용 가능)
"""

import json, argparse, random

# implicit_sentence: 최신값(new_val)을 '설명 없이 당연한 듯' 사용하는 문장
# (변화/연도/rebrand 같은 단어를 쓰지 않는다)
SEED_CHANGES = [
    dict(q="What is the name of the social media platform owned by Elon Musk that uses a black logo with a single letter?",
         old_val="Twitter", new_val="X",
         implicit_sentence="X has rolled out a new subscription tier that gives verified users priority placement in replies and longer post limits.",
         distractor="The platform lets users share short posts and follow accounts they are interested in.",
         change_year=2023, category="rebrand"),
    dict(q="Who is the reigning monarch of the United Kingdom?",
         old_val="Elizabeth", new_val="Charles",
         implicit_sentence="King Charles III delivered his address from Buckingham Palace, marking another year of his reign over the United Kingdom.",
         distractor="The British monarchy carries out ceremonial duties and represents the nation at state events.",
         change_year=2022, category="leadership"),
    dict(q="What is the most populous country in the world?",
         old_val="China", new_val="India",
         implicit_sentence="As the world's most populous country, India faces growing demand for urban housing and infrastructure.",
         distractor="Population density varies widely across regions depending on geography and economic activity.",
         change_year=2023, category="demographic"),
    dict(q="Which national team are the current FIFA World Cup champions?",
         old_val="France", new_val="Argentina",
         implicit_sentence="As reigning World Cup champions, Argentina entered the international friendly with high expectations from fans.",
         distractor="International football friendlies are used by coaches to test tactics and new players.",
         change_year=2022, category="sports_result"),
    dict(q="What is the parent company name of Facebook, Instagram, and WhatsApp?",
         old_val="Facebook", new_val="Meta",
         implicit_sentence="Meta reported strong quarterly earnings, driven by advertising across its family of apps including Instagram and WhatsApp.",
         distractor="Social media companies generate most of their revenue from targeted advertising.",
         change_year=2021, category="rebrand"),
    dict(q="Which planet has the most confirmed moons in the solar system?",
         old_val="Jupiter", new_val="Saturn",
         implicit_sentence="Astronomers studying Saturn, the planet with the most confirmed moons, have catalogued dozens of small irregular satellites.",
         distractor="Moons form through various processes including capture of passing bodies and accretion.",
         change_year=2023, category="science_count"),
    dict(q="Which city most recently hosted the Summer Olympic Games?",
         old_val="Tokyo", new_val="Paris",
         implicit_sentence="Following the Paris Summer Olympics, the city has begun repurposing several venues for public community use.",
         distractor="Host cities often invest heavily in transportation and housing ahead of the Games.",
         change_year=2024, category="sports_event"),
    dict(q="Who is the CEO of X (the social media company)?",
         old_val="Elon Musk", new_val="Linda Yaccarino",
         implicit_sentence="CEO Linda Yaccarino outlined the company's advertising strategy in a memo to X employees this week.",
         distractor="A CEO is responsible for major corporate decisions and overall company direction.",
         change_year=2023, category="leadership"),
    dict(q="What is the latest stable major release of the Python 3 language line?",
         old_val="3.11", new_val="3.13",
         implicit_sentence="Developers upgrading to Python 3.13 can take advantage of the new experimental free-threaded build and faster startup.",
         distractor="Python is widely used in data science, web development, and automation.",
         change_year=2024, category="software_version"),
    dict(q="What is the tallest building currently planned to surpass the Burj Khalifa in height?",
         old_val="Burj Khalifa", new_val="Jeddah Tower",
         implicit_sentence="Construction crews at the Jeddah Tower are working to push the structure past the one-kilometer mark, a height no building has reached.",
         distractor="Supertall buildings require deep foundations and advanced wind engineering.",
         change_year=2024, category="record"),
]


def make_documents(seed, include_distractor, rng):
    docs = [{"text": seed["implicit_sentence"], "stance": "update_doc"}]
    if include_distractor:
        docs.append({"text": seed["distractor"], "stance": "distractor"})
    rng.shuffle(docs)
    return [{"doc_id": f"d{i+1}", "text": d["text"], "stance": d["stance"]}
            for i, d in enumerate(docs)]


def seed_to_case(seed, idx, include_distractor, rng):
    return {
        "id": f"timplicit_{idx:02d}",
        "question": seed["q"],
        "parametric_answer": seed["old_val"],
        "contextual_answer": seed["new_val"],
        "gold_answer": seed["new_val"],
        "change_year": seed["change_year"],
        "category": seed["category"],
        "conflict_mode": "implicit",
        "documents": make_documents(seed, include_distractor, rng),
    }


def build(include_distractor=True, rng_seed=42):
    rng = random.Random(rng_seed)
    return [seed_to_case(s, i, include_distractor, rng)
            for i, s in enumerate(SEED_CHANGES, 1)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="temporal_implicit_conflicts.jsonl")
    ap.add_argument("--no-distractor", action="store_true")
    args = ap.parse_args()
    cases = build(include_distractor=not args.no_distractor)
    print(f"Built {len(cases)} implicit temporal cases")
    with open(args.out, "w", encoding="utf-8") as f:
        for c in cases:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    print(f"Wrote to {args.out}")


if __name__ == "__main__":
    main()
