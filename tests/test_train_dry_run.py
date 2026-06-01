"""Smoke test for training dry-run mode (CPU, no GPU required)."""

from unittest.mock import MagicMock, patch

import pytest

pytest.importorskip("torch")
pytest.importorskip("datasets")

from datasets import Dataset

from src.training.train import TrainingConfig, run_training


@pytest.fixture
def tiny_preference_dataset() -> Dataset:
    return Dataset.from_list(
        [
            {"prompt": "Question 1", "chosen": "Good 1", "rejected": "Bad 1"},
            {"prompt": "Question 2", "chosen": "Good 2", "rejected": "Bad 2"},
        ]
    )


@patch("src.training.train.create_dpo_trainer")
@patch("src.training.train.apply_lora")
@patch("src.training.train.load_model_for_dry_run")
@patch("src.training.train.load_preference_dataset")
@patch("src.training.train.checkpoint_dir_for")
def test_run_training_dry_run_completes(
    mock_checkpoint_dir,
    mock_load_dataset,
    mock_load_model,
    mock_apply_lora,
    mock_create_trainer,
    tiny_preference_dataset,
    tmp_path,
):
    mock_checkpoint_dir.return_value = tmp_path
    mock_load_dataset.return_value = tiny_preference_dataset
    mock_model = MagicMock()
    mock_tokenizer = MagicMock()
    mock_load_model.return_value = (mock_model, mock_tokenizer)
    mock_apply_lora.return_value = mock_model
    mock_trainer = MagicMock()
    mock_create_trainer.return_value = mock_trainer

    config = TrainingConfig(model_name="microsoft/phi-2", batch_size=1, num_epochs=1)
    result = run_training(config, dry_run=True, max_steps=1)

    assert result["status"] == "dry_run_completed"
    mock_trainer.train.assert_called_once()
    mock_load_model.assert_called_once_with("microsoft/phi-2")
