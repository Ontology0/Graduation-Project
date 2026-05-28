"""Generate answers from an LLM given chat-style prompt messages."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field, fields
from typing import Any

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from src.rag.config import get_api_key

logger = logging.getLogger(__name__)

DEFAULT_MODEL = "microsoft/phi-2"
DEFAULT_ANTHROPIC_MODEL = "claude-sonnet-4-6"


@dataclass
class GenerationConfig:
    max_new_tokens: int = 512
    temperature: float = 0.7
    top_p: float = 0.9
    do_sample: bool = True
    repetition_penalty: float = 1.1

    @classmethod
    def from_dict(cls, data: dict | None) -> GenerationConfig:
        """Build from an optional YAML ``generation:`` section."""
        if not data:
            return cls()
        allowed = {f.name for f in fields(cls)}
        return cls(**{k: v for k, v in data.items() if k in allowed})


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
        if device:
            self.device = device
        else:
            if torch.cuda.is_available():
                self.device = "cuda"
            elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
                self.device = "mps"
            else:
                self.device = "cpu"

        # Avoid float16 on CPU/MPS (common LayerNorm half-kernel issues).
        resolved_dtype: str | torch.dtype = torch_dtype
        if torch_dtype == "auto" and self.device in ("cpu", "mps"):
            resolved_dtype = torch.float32
        elif isinstance(torch_dtype, str) and torch_dtype != "auto":
            resolved_dtype = getattr(torch, torch_dtype, torch_dtype)

        logger.info("Loading generator model: %s on %s", model_name, self.device)
        self.tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=resolved_dtype,
            device_map=self.device if self.device == "auto" else None,
            trust_remote_code=True,
        )
        if self.device != "auto":
            self.model.to(self.device)
        if self.device in ("cpu", "mps"):
            # Some models may still end up as fp16/bf16 due to internal defaults.
            # Force fp32 for portability on CPU/MPS.
            self.model.to(dtype=torch.float32)

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


class AnthropicGenerator:
    """Generate text using Anthropic Messages API."""

    def __init__(self, model_name: str = DEFAULT_ANTHROPIC_MODEL):
        self.model_name = model_name

        try:
            from anthropic import Anthropic  # type: ignore
        except Exception as e:  # pragma: no cover
            raise ImportError(
                "anthropic package is required for AnthropicGenerator. "
                "Install it (e.g. `pip install anthropic`) and retry."
            ) from e

        api_key = get_api_key("ANTHROPIC_API_KEY")
        self._client = Anthropic(api_key=api_key)

    def _to_anthropic_messages(self, messages: list[dict[str, str]]) -> tuple[str, list[dict[str, Any]]]:
        system_parts: list[str] = []
        out: list[dict[str, Any]] = []
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            if role == "system":
                system_parts.append(content)
                continue
            if role not in ("user", "assistant"):
                continue
            out.append({"role": role, "content": content})

        system = "\n\n".join([p.strip() for p in system_parts if p.strip()])
        if not out:
            out = [{"role": "user", "content": ""}]
        return system, out

    def generate(
        self,
        messages: list[dict[str, str]],
        config: GenerationConfig | None = None,
    ) -> GenerationOutput:
        config = config or GenerationConfig()
        system, anthropic_messages = self._to_anthropic_messages(messages)

        try:
            create_kwargs: dict[str, Any] = {
                "model": self.model_name,
                "max_tokens": config.max_new_tokens,
                "system": system or None,
                "messages": anthropic_messages,
            }
            # Some Anthropic models disallow specifying both temperature and top_p.
            # Prefer temperature when both are present.
            if config.temperature is not None:
                create_kwargs["temperature"] = config.temperature
            if config.top_p is not None and config.temperature is None:
                create_kwargs["top_p"] = config.top_p

            resp = self._client.messages.create(**create_kwargs)
        except Exception as e:  # pragma: no cover
            msg = str(e)
            if "not_found_error" in msg or "model:" in msg:
                raise RuntimeError(
                    f"Anthropic model not found: {self.model_name}. "
                    "Update `llm.model` in your config (recommended: `claude-sonnet-4-6`)."
                ) from e
            raise

        text_parts: list[str] = []
        for block in getattr(resp, "content", []) or []:
            if getattr(block, "type", None) == "text":
                text_parts.append(getattr(block, "text", ""))
        text = "".join(text_parts).strip()

        usage = getattr(resp, "usage", None)
        prompt_tokens = int(getattr(usage, "input_tokens", 0) or 0)
        generated_tokens = int(getattr(usage, "output_tokens", 0) or 0)

        return GenerationOutput(
            text=text,
            model_name=self.model_name,
            prompt_tokens=prompt_tokens,
            generated_tokens=generated_tokens,
            metadata={"provider": "anthropic", "stop_reason": getattr(resp, "stop_reason", None)},
        )
