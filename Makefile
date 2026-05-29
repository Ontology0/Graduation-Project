.PHONY: demo demo-conflict install help

DOCS = data/sample_docs
Q_CONFLICT = "What color is the Northwood Institute mascot after the 2019 revision?"
Q_GENERAL  = "What is knowledge conflict in RAG?"

help:
	@echo "Usage:"
	@echo "  make install        Install dependencies"
	@echo "  make demo           Run Base RAG smoke test"
	@echo "  make demo-conflict  Compare Base RAG vs Conflict-Aware Prompting"

install:
	pip install -r requirements.txt

demo:
	python scripts/run_pipeline.py \
		--config configs/experiments/rag_base.yaml \
		--docs $(DOCS) \
		--question $(Q_GENERAL)

demo-conflict:
	@echo "=== Base RAG ==="
	python scripts/run_pipeline.py \
		--config configs/experiments/rag_base.yaml \
		--docs $(DOCS) \
		--question $(Q_CONFLICT)
	@echo ""
	@echo "=== Conflict-Aware Prompting ==="
	python scripts/run_pipeline.py \
		--config configs/experiments/prompting_conflict_aware.yaml \
		--docs $(DOCS) \
		--question $(Q_CONFLICT)
