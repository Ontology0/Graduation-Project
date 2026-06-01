"""Fine-tuning entrypoint for DPO + LoRA training."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import torch
from datasets import Dataset
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

from src.rag.config import resolve_path

logger = logging.getLogger(__name__)

DEFAULT_LORA_TARGET_MODULES = [
    "q_proj",
    "k_proj",
    "v_proj",
    "o_proj",
    "gate_proj",
    "up_proj",
    "down_proj",
]


@dataclass
class TrainingConfig:
    """Configuration for DPO + LoRA fine-tuning."""

    model_name: str = "microsoft/phi-2"
    lora_rank: int = 16
    lora_alpha: int = 32
    lora_target_modules: list[str] | None = None
    lora_dropout: float = 0.05
    learning_rate: float = 5e-5
    batch_size: int = 4
    num_epochs: int = 3
    max_length: int = 1024
    beta: float = 0.1  # DPO beta parameter
    output_dir: str = "outputs/checkpoints"
    train_data_path: str = "data/synthetic_conflicts/preference_pairs_train.jsonl"

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> TrainingConfig:
        fields = {f.name for f in __import__("dataclasses").fields(cls)}
        return cls(**{k: v for k, v in d.items() if k in fields})


def load_preference_dataset(path: str | Path) -> Dataset:
    """Load preference-pair JSONL into a Dataset with TRL DPO columns."""
    resolved = resolve_path(path)
    rows: list[dict[str, str]] = []
    with resolved.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            record = json.loads(line)
            rows.append(
                {
                    "prompt": record["prompt"],
                    "chosen": record["chosen"],
                    "rejected": record["rejected"],
                }
            )
    return Dataset.from_list(rows)


def build_bnb_config() -> BitsAndBytesConfig:
    return BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
    )


def load_model_4bit(model_name: str):
    """Load a causal LM in 4-bit for QLoRA training."""
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    bnb_config = build_bnb_config()
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        quantization_config=bnb_config,
        device_map="auto",
    )
    model = prepare_model_for_kbit_training(model)
    return model, tokenizer


def build_lora_config(config: TrainingConfig) -> LoraConfig:
    target_modules = config.lora_target_modules or DEFAULT_LORA_TARGET_MODULES
    return LoraConfig(
        r=config.lora_rank,
        lora_alpha=config.lora_alpha,
        lora_dropout=config.lora_dropout,
        target_modules=target_modules,
        bias="none",
        task_type="CAUSAL_LM",
    )


def apply_lora(model, config: TrainingConfig):
    """Attach LoRA adapters to a prepared model."""
    lora_config = build_lora_config(config)
    return get_peft_model(model, lora_config)


def run_training(config: TrainingConfig | None = None) -> dict:
    """Run DPO + LoRA fine-tuning.

    Currently loads preference data only; training loop wired in later commits.
    """
    config = config or TrainingConfig()

    train_dataset = load_preference_dataset(config.train_data_path)
    logger.info("Loaded %d preference pairs from %s", len(train_dataset), config.train_data_path)

    return {
        "status": "data_loaded",
        "num_rows": len(train_dataset),
        "columns": train_dataset.column_names,
        "config": {
            "model": config.model_name,
            "lora_rank": config.lora_rank,
            "learning_rate": config.learning_rate,
            "epochs": config.num_epochs,
        },
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    result = run_training()
    print(result)
