"""Fine-tuning entrypoint for DPO + LoRA training."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class TrainingConfig:
    """Configuration for DPO + LoRA fine-tuning."""

    model_name: str = "microsoft/phi-2"
    lora_rank: int = 16
    lora_alpha: int = 32
    lora_target_modules: list[str] | None = None
    learning_rate: float = 5e-5
    batch_size: int = 4
    num_epochs: int = 3
    max_length: int = 1024
    beta: float = 0.1  # DPO beta parameter
    output_dir: str = "outputs/checkpoints"

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> TrainingConfig:
        fields = {f.name for f in __import__("dataclasses").fields(cls)}
        return cls(**{k: v for k, v in d.items() if k in fields})


def run_training(config: TrainingConfig | None = None) -> dict:
    """Run DPO + LoRA fine-tuning.

    Currently a placeholder that validates config and reports readiness.
    Real training loop will be wired with TRL's DPOTrainer and PEFT.
    """
    config = config or TrainingConfig()

    logger.info("Training config: %s", config)
    logger.info("Model: %s | LoRA rank: %d | LR: %s", config.model_name, config.lora_rank, config.learning_rate)

    return {
        "status": "not_implemented",
        "config": {
            "model": config.model_name,
            "lora_rank": config.lora_rank,
            "learning_rate": config.learning_rate,
            "epochs": config.num_epochs,
        },
        "message": "Training pipeline is scaffolded. Wire TRL DPOTrainer to execute.",
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    result = run_training()
    print(result)
