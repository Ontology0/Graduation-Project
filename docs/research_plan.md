# Research Plan (Draft)

> **Status:** research scaffold — content will be refined as benchmarks and protocols are decided.

## Project title

**LLM Knowledge Conflict Mitigation via RAG–Fine-tuning Fusion**  
(Working title: Conflict-Aware PA-RAG — preference learning for context–memory conflict in RAG)

## Problem definition

In retrieval-augmented generation (RAG), the generator may receive **external evidence** from retrieval while still relying on **internal (parametric) knowledge** learned during pre-training. When these sources imply different answers, the system must decide which evidence to follow, under what conditions (time, scope, source quality), or whether to abstain.

Retrieval quality alone does not guarantee correct answers: the model can ignore retrieved context and answer from memory, or blindly follow low-quality context.

## Target conflict type: context–memory conflict

This project focuses on **context–memory conflict**:

- **Definition:** Retrieved external context and the LLM’s internal/parametric knowledge point to **different answers** for the same question.
- **In scope:** Designing data, prompts, preference pairs, and LoRA/DPO training to learn **resolution rules** (e.g., prefer external when it is authoritative and current; prefer internal when external is unreliable).

**Out of scope (not main research targets):**

- **Inter-context conflict:** Contradictions among multiple retrieved passages (may appear in benchmarks but not as the primary problem formulation).
- **Intra-memory conflict:** Contradictions within parametric knowledge alone without a retrieved external alternative.

## Research questions

1. Can **preference learning (DPO + LoRA)** internalize conflict resolution better than **prompting-only** baselines under resource constraints?
2. Which **conflict patterns** (e.g., recency, source trust, factual swap) are learnable vs. remain brittle?
3. How do **PA-RAG-style multi-criterion alignment** and **conflict-only** alignment compare when conflict labels are available?
4. Does conflict-aware training harm other alignment goals (informativeness, robustness, citation behavior) — to be measured once eval protocol exists?

## Proposed approach

1. **Annotation schema** for conflict instances (`data/schema/`) with resolution rules and chosen/rejected answers.
2. **Base RAG** pipeline (first draft: `src/rag/pipeline.py`).
3. **Conflict-aware prompting** (`configs/prompts/conflict_aware.md`).
4. **DPO + LoRA** variants: PA-RAG-style LoRA, conflict-only LoRA, and combined conflict-aware PA-RAG LoRA (`src/training/`, configs under `configs/experiments/`).
5. **Evaluation** on selected benchmarks (TBD) plus optional natural case studies (`data/natural/`).

## Expected contribution

- Extend PA-RAG-style preference alignment with an explicit **knowledge conflict** criterion for **context–memory** settings.
- Compare **prompting vs. preference internalization** under **LoRA** (not full fine-tuning) for reproducibility on limited compute.
- Document **limitations** where synthetic training does not transfer to ambiguous natural conflicts.

## Current limitations

- No final benchmark or metric selection.
- RAG code is a first draft only; training/eval entrypoints remain scaffolds. No reported experimental results.
- Full fine-tuning (as in original PA-RAG) is not planned as a primary arm; paper numbers may be cited for reference only.
- Heavy retrieval backends and production indexes are not committed yet.
