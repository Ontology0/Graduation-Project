# Benchmark Selection (Draft)

> **Final decision:** **pending** for train/eval split. Candidate **metadata** (license · scale · conflict types) reviewed below (issue #55).

## Role legend

| Role | Meaning |
|------|---------|
| **Train candidate** | May supply DPO pairs or conflict annotations with relatively clear resolution |
| **Eval candidate** | Held-out quantitative evaluation |
| **Reference** | Schema, conflict types, or qualitative analysis only |

## Candidate review (license · scale · conflict type)

Sources: NeurIPS / arXiv papers and official GitHub or Hugging Face dataset cards (checked 2026-06). Verify license files again before redistribution.

| Dataset | License (upstream) | Scale (order of magnitude) | Primary conflict types | Project relevance |
|---------|-------------------|----------------------------|------------------------|-------------------|
| **ClashEval** (Wu et al., NeurIPS 2024 D&B) | Open release on [GitHub](https://github.com/kevinwu23/StanfordClashEval) / HF; **no root LICENSE file** in public repo at doc time — confirm terms at download | ~1.3k base questions × multiple **perturbed contexts** per item (6 domains: drug dosage, sports, news, Wikipedia dates, names, locations) | **Context–memory (parametric prior vs. retrieved evidence)**; controlled perturbations from subtle → blatant error | Core **context–memory** benchmark; aligns with pilot `doc_truthful` / false-context arms |
| **ConflictBank** (Su et al., NeurIPS 2024 D&B) | **CC BY-SA 4.0** ([repo](https://github.com/zhaochen0110/conflictbank)) | ~7.45M claim–evidence pairs; ~553k QA pairs (Wikidata-derived) | **Misinformation**, **temporal**, **semantic** conflicts; simulates embedded vs. retrieved vs. combined conflict | Large **train subset** candidate for temporal/version slices; full corpus too large for student compute |
| **WikiContradict** (Hou et al., arXiv 2024 / IBM) | **MIT** ([HF card](https://huggingface.co/datasets/ibm-research/Wikipedia_contradict_benchmark)) | **253** human-annotated QA instances (from ~1.2k tagged Wikipedia articles) | **Natural inter-passage** contradiction (same source, equal trust); not parametric-vs-context controlled | **Eval (natural)** and qualitative transfer — poor fit for unambiguous DPO labels |
| **CONFLICTS** / *DRAGged into Conflicts* (Cattan et al., 2025) | **Apache-2.0** ([google-research-datasets/rag_conflicts](https://github.com/google-research-datasets/rag_conflicts)) | **458** queries (~9.2 Google results each, expert-annotated) | Taxonomy: no conflict, complementary info, **conflicting opinions**, **freshness (outdated)**, **misinformation** (+ rare “other”) | **Reference** for conflict-type labels and expected response behavior; **eval** for type-aware metrics, not bulk DPO train |
| **ConflictQA** (Xie et al., ICLR 2024; OSU) | **Apache-2.0** ([HF](https://huggingface.co/datasets/osunlp/ConflictQA)) | PopQA-based: **~20k** instances (paper table); StrategyQA variant smaller; multiple LLM-generated memory/counter-memory configs | **Context–memory**: parametric memory vs. counter-evidence (entity-substitution style) | Train subset where `ground_truth` vs. counter context is explicit; eval on held-out questions / popularity strata |
| **ConFiQA** (Bi et al., ACL 2025 Findings; Context-DPO) | Check [Context-DPO repo](https://github.com/byronbbl/context-dpo) / paper supplement at download | **3 × ~6k** instances (QA, MR, MC subsets; 2–4 hop) | **Counterfactual-in-context** vs. parametric knowledge; faithful vs. stubborn response pairs | **Train** (preference pairs) and optional **eval** holdout per subset; distinct from ConflictQA (synthetic KG paths vs. PopQA memory) |

### Per-dataset notes

#### ClashEval

- **Conflict focus:** Whether the model follows **incorrect retrieved text** vs. **correct internal prior**, and the reverse (correct context vs. wrong prior).
- **Label clarity:** Perturbation strength and gold answer support **true_doc / false_doc** style preferences (see pilot `experiments/2026-05-31/`).
- **Caveat:** Underlying web passages may have separate copyright; benchmark redistribution terms are not spelled out in-repo — use for research only until verified.

#### ConflictBank

- **Conflict focus:** Broader than context–memory only (includes semantic polysemy and pre-training-style embedded conflicts).
- **Train use (candidate):** Prefer **temporal_conflict** and high-confidence **misinformation** slices where newer fact or false claim is structurally labeled; avoid dumping full 7M pairs.
- **Eval use (candidate):** Held-out QA partition by conflict cause or Wikidata entity cluster (protocol TBD in `src/evaluation/`).

#### WikiContradict

- **Conflict focus:** Real Wikipedia maintenance contradictions; often **no single authoritative answer**.
- **Not for train (candidate):** Ambiguous resolution violates “unambiguous ground truth” principle.
- **Eval use (candidate):** Natural generalization / limitation section (`data/natural/` planned role).

#### CONFLICTS (DRAGged into Conflicts)

- **Conflict focus:** **Inter-context** and **freshness** in real search snippets; opinion conflicts need **neutral multi-view** answers, not single chosen label.
- **Reference use:** Map `data/schema/` conflict_type and resolution-rule fields to expert taxonomy; inform judge rubric (`configs/prompts/judge.md`).

#### ConflictQA

- **Conflict focus:** Classic **memory vs. counter-memory** QA (Adaptive Chameleon line of work).
- **Variants:** Multiple configs (`ConflictQA-popQA-*`, StrategyQA) — pick **one** generator-backed memory version for train to avoid leakage across LLM-specific artifacts.
- **Caveat:** Counter-evidence is LLM-generated; filter for cases where `ground_truth` is uncontested.

#### ConFiQA

- **Conflict focus:** RAG-style **counterfactual passages** with provided faithful/stubborn responses (designed for Context-DPO).
- **Relation to ConflictQA:** Complementary synthetic construction (KG multi-hop vs. PopQA popularity); do not merge without deduplication.
- **License:** Confirm file-level license in upstream release when adding to `data/synthetic/`.

## References (quick links)

| Dataset | Paper / resource |
|---------|------------------|
| ClashEval | NeurIPS 2024 D&B — [GitHub](https://github.com/kevinwu23/StanfordClashEval) |
| ConflictBank | NeurIPS 2024 D&B — [GitHub](https://github.com/zhaochen0110/conflictbank) |
| WikiContradict | arXiv:2406.13805 — [HF](https://huggingface.co/datasets/ibm-research/Wikipedia_contradict_benchmark) |
| CONFLICTS | arXiv:2506.08500 — [GitHub](https://github.com/google-research-datasets/rag_conflicts) |
| ConflictQA | ICLR 2024 — [HF](https://huggingface.co/datasets/osunlp/ConflictQA) |
| ConFiQA | ACL 2025 Findings (Context-DPO) — [arXiv:2412.15280](https://arxiv.org/abs/2412.15280) |

## Principles (draft)

- Prefer **unambiguous ground truth** for **training** preference pairs.
- Reserve **ambiguous natural** conflicts for **limitation analysis** and case studies (`data/natural/`).
- Document final train/eval split in `decision_log.md` when confirmed.
