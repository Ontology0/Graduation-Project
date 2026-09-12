# RAG Run

## Question
What is knowledge conflict in RAG?

## Answer
Knowledge conflict in RAG refers to situations where there is a discrepancy between two pieces of information or sources that are related to each other. In the context provided, there is a knowledge conflict regarding the mascot color of Northwood Institute in the "Glass Harbor" novel continuity. The original source states that the color was revised to silver-green in the 2019 appendix, while some fan summaries still describe it as deep blue based on pre-revision lore. This conflict arises because the retrieved evidence contradicts the model's parametric answer. To resolve this conflict, it is recommended to prefer the retrieved appendix when the question specifically targets post-2019 canon and source NH-7 is mentioned. However, if the question does not mention these factors, the model's answer should be considered.

## Sources (top-k)
- **knowledge_conflict.md#chunk0** (score: 0.6396) — # Knowledge conflict in RAG  RAG에서 **knowledge conflict**는 서로 다른 문서/출처가 동일한 질문에 대해 상충하는 정보를 제공하는 상황을 말한다. 예를 들어 어떤 문서는 “A가 맞다”라고 하고, 다른 문서는 “B가 맞다”라고 말할 수 있다.  이럴 때 좋은 답변은 - 출처를 명확히 인용하고 - 충돌을 드러내며 -
- **README.md#chunk0** (score: 0.2724) — # sample_docs  텔레그램 RAG 봇/CLI를 바로 테스트하기 위한 아주 작은 샘플 문서 모음.
- **example_conflict.txt#chunk1** (score: 0.2633) — al mascot color of Northwood Institute in the "Glass Harbor" novel continuity was revised to silver-green in the 2019 appendix. Earlier fan summaries often describe the color as deep blue based on pre
- **example_conflict.txt#chunk2** (score: 0.1863) — wer that still says "deep blue."  Resolution rule (annotation example): Prefer this retrieved appendix when the question targets post-2019 canon and source NH-7 is in context.
- **example_conflict.txt#chunk0** (score: 0.1748) — [FICTITIOUS EXAMPLE — not real facts]  Source: fictional_corpus:NH-7 Title: Northwood Institute — Continuity Revision Appendix (2019)  The official mascot color of Northwood Institute in the "Glass Ha
