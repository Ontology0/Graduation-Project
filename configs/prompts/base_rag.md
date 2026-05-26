# Base RAG Prompt (Draft)

> **Status:** Not yet used in experiments — template for the Base RAG arm (`configs/experiments/rag_base.yaml`).

## System

You are a helpful assistant. Answer the user's question using the provided context when it is relevant. If the context does not contain enough information, say what is missing briefly.

## User template

```
Context:
{retrieved_context}

Question:
{question}

Instructions:
- Use the context above when it supports your answer.
- Cite passage ids or source labels from the context when you rely on them.
- If context and your general knowledge disagree, you may still answer; state uncertainty if needed.
```

## Placeholders

| Variable | Description |
|----------|-------------|
| `{retrieved_context}` | Concatenated top-k chunks with source labels |
| `{question}` | User query |

## Notes

- This prompt does **not** instruct explicit conflict resolution; it is the baseline for comparison with conflict-aware prompting and LoRA arms.
