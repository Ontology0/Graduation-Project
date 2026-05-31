import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.rag.prompt_builder import load_prompt_template

base = load_prompt_template("configs/prompts/base_rag.md")
conflict = load_prompt_template("configs/prompts/conflict_aware.md")

print("=== BASE RAG (parsed system) ===")
print(base.system)
print("\n=== CONFLICT-AWARE (parsed system) ===")
print(conflict.system)
print("\n=== DIFF ===")
print("system texts equal:", base.system == conflict.system)
print("user templates equal:", base.user_template == conflict.user_template)
