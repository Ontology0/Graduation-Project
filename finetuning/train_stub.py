"""Fine-tuning placeholder: documents the future training entrypoint without training or API use."""


def run_finetuning_placeholder() -> dict:
    """Return a fixed stub; no GPU work, optimizers, or checkpoints."""
    return {
        "method": "finetuning",
        "status": "not_implemented",
        "message": "Fine-tuning experiment is not implemented yet.",
    }


if __name__ == "__main__":
    print(run_finetuning_placeholder())
