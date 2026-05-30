import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.rag.pipeline import RAGPipeline

PILOT_DIR = Path(__file__).resolve().parent
RESULT_PATH = PILOT_DIR / "results" / "e2e_result.txt"

print("Loading pipeline...")
p = RAGPipeline.from_config("configs/experiments/rag_base.yaml")

print("Indexing documents...")
n = p.index_documents("data/sample_docs/")
print(f"Indexed {n} chunks")

print("Querying (CPU phi-2, may take several minutes)...")
result = p.query("What is the mascot color of Northwood Institute after the 2019 revision?")

RESULT_PATH.parent.mkdir(parents=True, exist_ok=True)
with open(RESULT_PATH, "w", encoding="utf-8") as f:
    f.write(f"TYPE: {type(result)}\n")
    f.write("=" * 60 + "\n")
    f.write(str(result))

print(f"DONE. See {RESULT_PATH}")
