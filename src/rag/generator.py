"""Generate answers from an LLM given chat-style prompt messages."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

logger = logging.getLogger(__name__)

DEFAULT_MODEL = "microsoft/phi-2"


@dataclass
class GenerationConfig:
    max_new_tokens: int = 512
    temperature: float = 0.7
    top_p: float = 0.9
    do_sample: bool = True
    repetition_penalty: float = 1.1


@dataclass
class GenerationOutput:
    text: str
    model_name: str
    prompt_tokens: int = 0
    generated_tokens: int = 0
    metadata: dict = field(default_factory=dict)


class Generator:
    """Wraps a HuggingFace causal LM for text generation."""

    def __init__(
        self,
        model_name: str = DEFAULT_MODEL,
        device: str | None = None,
        torch_dtype: str = "auto",
    ):
        self.model_name = model_name
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")

        logger.info("Loading generator model: %s on %s", model_name, self.device)
        self.tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch_dtype,
            device_map=self.device if self.device == "auto" else None,
            trust_remote_code=True,
        )
        if self.device != "auto":
            self.model.to(self.device)

        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

    def _apply_chat_template(self, messages: list[dict[str, str]]) -> str:
        """Convert chat messages to a single prompt string."""
        if hasattr(self.tokenizer, "apply_chat_template") and self.tokenizer.chat_template:
            return self.tokenizer.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True
            )
        parts: list[str] = []
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            if role == "system":
                parts.append(f"System: {content}\n")
            elif role == "user":
                parts.append(f"User: {content}\n")
            elif role == "assistant":
                parts.append(f"Assistant: {content}\n")
        parts.append("Assistant:")
        return "\n".join(parts)

    @torch.inference_mode()
    def generate(
        self,
        messages: list[dict[str, str]],
        config: GenerationConfig | None = None,
    ) -> GenerationOutput:
        """Generate a response for the given chat messages."""
        config = config or GenerationConfig()
        prompt = self._apply_chat_template(messages)

        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        prompt_length = inputs["input_ids"].shape[1]

        output_ids = self.model.generate(
            **inputs,
            max_new_tokens=config.max_new_tokens,
            temperature=config.temperature,
            top_p=config.top_p,
            do_sample=config.do_sample,
            repetition_penalty=config.repetition_penalty,
            pad_token_id=self.tokenizer.pad_token_id,
        )

        new_tokens = output_ids[0][prompt_length:]
        answer = self.tokenizer.decode(new_tokens, skip_special_tokens=True).strip()

        return GenerationOutput(
            text=answer,
            model_name=self.model_name,
            prompt_tokens=prompt_length,
            generated_tokens=len(new_tokens),
        )
