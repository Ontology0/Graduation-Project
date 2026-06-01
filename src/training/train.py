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
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, TrainerCallback

from src.rag.config import resolve_path
from trl import DPOConfig, DPOTrainer

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
    experiment_name: str = "default"
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


def load_model_for_dry_run(model_name: str):
    """Load a small model on CPU for smoke tests (no 4-bit)."""
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float32,
        device_map="cpu",
    )
    return model, tokenizer


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


def checkpoint_dir_for(config: TrainingConfig) -> Path:
    path = resolve_path(config.output_dir) / config.experiment_name
    path.mkdir(parents=True, exist_ok=True)
    return path


def build_dpo_config(
    config: TrainingConfig,
    output_dir: Path,
    *,
    max_steps: int | None = None,
) -> DPOConfig:
    kwargs: dict[str, Any] = {
        "output_dir": str(output_dir),
        "per_device_train_batch_size": config.batch_size,
        "learning_rate": config.learning_rate,
        "num_train_epochs": config.num_epochs,
        "beta": config.beta,
        "max_length": config.max_length,
        "logging_steps": 10,
        "save_steps": 500,
        "report_to": [],
    }
    if max_steps is not None:
        kwargs["max_steps"] = max_steps
    return DPOConfig(**kwargs)


class TrainingLogCallback(TrainerCallback):
    """Append per-step trainer logs to training_log.jsonl."""

    def __init__(self, log_path: Path) -> None:
        self.log_path = log_path
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def on_log(self, args, state, control, logs=None, **kwargs) -> None:
        if not logs:
            return
        entry = {"step": state.global_step, **logs}
        with self.log_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry) + "\n")


def create_dpo_trainer(
    model,
    tokenizer,
    train_dataset: Dataset,
    config: TrainingConfig,
    output_dir: Path,
    *,
    max_steps: int | None = None,
    extra_callbacks: list[TrainerCallback] | None = None,
) -> DPOTrainer:
    training_args = build_dpo_config(config, output_dir, max_steps=max_steps)
    callbacks = list(extra_callbacks or [])
    callbacks.append(TrainingLogCallback(output_dir / "training_log.jsonl"))
    return DPOTrainer(
        model=model,
        ref_model=None,
        args=training_args,
        train_dataset=train_dataset,
        tokenizer=tokenizer,
        callbacks=callbacks,
    )


def _limit_dataset(dataset: Dataset, limit: int) -> Dataset:
    if len(dataset) <= limit:
        return dataset
    return dataset.select(range(limit))


def run_training(
    config: TrainingConfig | None = None,
    *,
    dry_run: bool = False,
    max_steps: int | None = None,
) -> dict:
    """Run DPO + LoRA fine-tuning."""
    config = config or TrainingConfig()

    train_dataset = load_preference_dataset(config.train_data_path)
    logger.info("Loaded %d preference pairs from %s", len(train_dataset), config.train_data_path)

    checkpoint_dir = checkpoint_dir_for(config)
    steps = max_steps if max_steps is not None else (2 if dry_run else None)

    if dry_run:
        train_dataset = _limit_dataset(train_dataset, 2)
        model, tokenizer = load_model_for_dry_run(config.model_name)
    else:
        model, tokenizer = load_model_4bit(config.model_name)

    model = apply_lora(model, config)
    trainer = create_dpo_trainer(
        model,
        tokenizer,
        train_dataset,
        config,
        checkpoint_dir,
        max_steps=steps,
    )
    trainer.train()
    trainer_state_path = checkpoint_dir / "trainer_state.json"

    return {
        "status": "dry_run_completed" if dry_run else "completed",
        "checkpoint_dir": str(checkpoint_dir),
        "trainer_state": str(trainer_state_path) if trainer_state_path.exists() else None,
        "num_rows": len(train_dataset),
        "max_steps": steps,
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
