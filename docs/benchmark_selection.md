# Benchmark Selection (Draft)

> **Final decision:** **pending**. Roles below are **candidates**, not committed train/eval splits.

## Role legend

| Role | Meaning |
|------|---------|
| **Train candidate** | May supply DPO pairs or conflict annotations with relatively clear resolution |
| **Eval candidate** | Held-out quantitative evaluation |
| **Reference** | Schema, conflict types, or qualitative analysis only |

## Candidates

### ClashEval

- **Role:** Train candidate · Eval candidate
- **Notes:** Internal vs. external knowledge conflict; suitable for measurable conflict scenarios (details TBD after paper/dataset review).
- **Status:** final decision pending

### ConflictBank

- **Role:** Train candidate (subset) · Eval candidate (subset)
- **Notes:** Large-scale retrieved/embedded conflict benchmark; likely **subset** for training due to scale.
- **Status:** final decision pending

### WikiContradict

- **Role:** Eval candidate · Reference (natural contradiction)
- **Notes:** Wikipedia-based contradictory claims; useful for **natural** conflict evaluation, not necessarily for unambiguous DPO training.
- **Status:** final decision pending

### CONFLICTS / DRAGged into Conflicts

- **Role:** Reference
- **Notes:** Expert annotations and resolution-rule structure for schema design; may inform annotation fields, not necessarily primary leaderboard.
- **Status:** final decision pending

### ConFiQA / ConflictQA (and related)

- **Role:** Train candidate · Eval candidate · Reference (TBD per variant)
- **Notes:** QA-style conflict datasets under consideration; exact variant and license to be confirmed.
- **Status:** final decision pending

## Principles (draft)

- Prefer **unambiguous ground truth** for **training** preference pairs.
- Reserve **ambiguous natural** conflicts for **limitation analysis** and case studies (`data/natural/`).
- Document final train/eval split in `decision_log.md` when confirmed.
