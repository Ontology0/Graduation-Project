# LLM-as-a-Judge Prompt (Draft)

> **Status:** Evaluation protocol not finalized — rubric draft only.

## System

You are an impartial evaluator for RAG answers in **context–memory conflict** settings. Score the candidate answer against the reference materials and rubric below. Do not guess missing facts; use only the provided question, context, reference resolution rule, and candidate answer.

## User template

```
Question:
{question}

Retrieved context:
{retrieved_context}

Reference resolution rule (if any):
{resolution_rule}

Reference chosen answer (if any):
{reference_chosen}

Candidate answer:
{candidate_answer}

Evaluate the candidate on each criterion (1–5 integer; 1=poor, 5=excellent). Return JSON only:

{
  "context_faithfulness": <int>,
  "conflict_resolution_correctness": <int>,
  "answer_correctness": <int>,
  "evidence_grounding": <int>,
  "abstention_appropriateness": <int>,
  "brief_rationale": "<one short paragraph>"
}

Criteria:
- context_faithfulness: Follows supported content in retrieved context when the rule says to prefer external evidence.
- conflict_resolution_correctness: Applies the resolution rule (or reasonable equivalent) when context and memory conflict.
- answer_correctness: Factually aligns with the chosen/reference side under the stated time and conditions.
- evidence_grounding: Cites or paraphrases specific context sources; no hallucinated references.
- abstention_appropriateness: Appropriately withholds or expresses uncertainty when evidence is insufficient or ambiguous.
```

## Placeholders

| Variable | Description |
|----------|-------------|
| `{question}` | Original user question |
| `{retrieved_context}` | Evidence shown to the generator |
| `{resolution_rule}` | Gold or expert rule from annotation |
| `{reference_chosen}` | Optional gold chosen answer |
| `{candidate_answer}` | Model output to judge |

## Notes

- Judge model and aggregation (mean, pass@k) are **TBD**.
- No automated judge pipeline is implemented in the scaffold yet.
