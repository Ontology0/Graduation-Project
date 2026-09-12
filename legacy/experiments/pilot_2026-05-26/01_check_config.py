import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import yaml

from src.rag.config import load_config
from src.rag.pipeline import RAGPipeline

for cfg_path in [
    "configs/experiments/rag_base.yaml",
    "configs/experiments/prompting_conflict_aware.yaml",
]:
    print(f"\n=== {cfg_path} ===")
    cfg = load_config(cfg_path)
    print("YAML:", cfg)

    p = RAGPipeline.from_config(cfg_path)
    print("experiment_name:", p.experiment_name)
    print("model_name (generator):", p.generator.model_name)
    print("prompt_file (YAML):", cfg.get("prompt_file"))
    print("top_k:", p.top_k)
    print("chunk_size / chunk_overlap:", p.chunk_size, p.chunk_overlap)
    print(
        "generation:",
        {
            "max_new_tokens": p.generation_config.max_new_tokens,
            "do_sample": p.generation_config.do_sample,
        },
    )
