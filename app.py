"""HuggingFace Spaces entry point — Conflict-Aware PA-RAG interactive demo."""

from __future__ import annotations

import logging
from pathlib import Path

import gradio as gr

from src.rag.config import load_config, load_env
from src.rag.embedder import Embedder
from src.rag.generator import AnthropicGenerator, GenerationConfig
from src.rag.prompt_builder import default_template, load_prompt_template
from src.rag.retriever import Retriever
from src.rag.vector_store import make_vector_store
from src.rag.pipeline import RAGPipeline

logging.basicConfig(level=logging.INFO)
load_env()

DOCS_PATH = Path("data/sample_docs")
CONFIGS = {
    "Base RAG": "configs/experiments/rag_base.yaml",
    "Conflict-Aware Prompting": "configs/experiments/prompting_conflict_aware.yaml",
}
SAMPLE_QUESTIONS = [
    "What color is the Northwood Institute mascot after the 2019 revision?",
    "What is knowledge conflict in RAG?",
    "How should a RAG system handle conflicts between retrieved evidence and internal knowledge?",
]

_cache: dict[tuple, RAGPipeline] = {}


def _build_pipeline(config_name: str, chunk_size: int, chunk_overlap: int) -> RAGPipeline:
    key = (config_name, chunk_size, chunk_overlap)
    if key in _cache:
        return _cache[key]

    cfg = load_config(CONFIGS[config_name])
    embedding_model = (
        cfg.get("retrieval", {}).get("embedding_model")
        or "sentence-transformers/all-MiniLM-L6-v2"
    )
    embedder = Embedder(model_name=embedding_model)
    store = make_vector_store(backend="faiss", dimension=embedder.dimension)
    retriever = Retriever(embedder=embedder, store=store)
    generator = AnthropicGenerator(model_name="claude-sonnet-4-6")

    prompt_file = cfg.get("prompt_file")
    if prompt_file and Path(prompt_file).exists():
        prompt_template = load_prompt_template(prompt_file)
    else:
        prompt_template = default_template("conflict" in config_name.lower())

    pipeline = RAGPipeline(
        retriever=retriever,
        generator=generator,
        experiment_name=cfg.get("experiment_name", config_name),
        prompt_template=prompt_template,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    pipeline.index_documents(DOCS_PATH, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    _cache[key] = pipeline
    return pipeline


def run_demo(
    question: str,
    config_name: str,
    top_k: int,
    chunk_size: int,
    chunk_overlap: int,
    max_tokens: int,
    temperature: float,
) -> tuple[str, str]:
    if not question.strip():
        return "❗ 질문을 입력해주세요.", ""
    try:
        pipeline = _build_pipeline(config_name, int(chunk_size), int(chunk_overlap))
        gen_config = GenerationConfig(
            max_new_tokens=int(max_tokens),
            temperature=float(temperature),
        )
        pipeline.generation_config = gen_config
        result = pipeline.query(question, top_k=int(top_k))

        sources_lines = []
        for i, s in enumerate(result.retrieved_sources, 1):
            sources_lines.append(f"[{i}] {s['source']}  (score: {s['score']})")
            sources_lines.append(s["text"][:300] + ("…" if len(s["text"]) > 300 else ""))
            sources_lines.append("")
        return result.answer, "\n".join(sources_lines)
    except Exception as exc:
        logging.exception("Demo error")
        return f"⚠️ 오류: {exc}", ""


with gr.Blocks(title="Conflict-Aware PA-RAG Demo", theme=gr.themes.Soft()) as demo:
    gr.Markdown(
        """
# 🔬 Conflict-Aware PA-RAG — Interactive Demo
**Alltology Team · 이화여자대학교 캡스톤디자인 2026**

RAG 시스템에서 **검색된 외부 문서(context)**와 **모델 내부 지식(memory)**이 충돌할 때,
_Base RAG_ 와 _Conflict-Aware Prompting_ 이 어떻게 다르게 반응하는지 직접 비교해보세요.

> **추천 시나리오** — "Northwood Institute 마스코트 색상" 질문:
> 모델 내부 지식은 *deep blue*, 검색 문서(2019 개정판)는 *silver-green* 이라고 말합니다.
> 두 config의 답변 차이를 확인해보세요.
"""
    )

    with gr.Row():
        # ── 왼쪽: 설정 패널 ──────────────────────────────
        with gr.Column(scale=1, min_width=300):
            gr.Markdown("### ⚙️ 실험 설정")
            config_dd = gr.Dropdown(
                choices=list(CONFIGS.keys()),
                value="Base RAG",
                label="실험 Config",
            )
            top_k_sl = gr.Slider(1, 10, value=5, step=1, label="Top-K  (검색 문서 수)")
            with gr.Accordion("고급 파라미터", open=False):
                chunk_size_sl = gr.Slider(
                    128, 1024, value=512, step=64,
                    label="Chunk Size  (변경 시 재인덱싱)",
                )
                chunk_overlap_sl = gr.Slider(
                    0, 256, value=128, step=32, label="Chunk Overlap"
                )
                max_tokens_sl = gr.Slider(
                    64, 1024, value=512, step=64, label="Max Output Tokens"
                )
                temperature_sl = gr.Slider(
                    0.0, 1.0, value=0.7, step=0.05, label="Temperature"
                )

            gr.Markdown("### 💬 질문")
            q_input = gr.Textbox(
                lines=3,
                placeholder="질문을 입력하세요…",
                label="Question",
            )
            gr.Examples(
                examples=SAMPLE_QUESTIONS,
                inputs=q_input,
                label="샘플 질문",
            )
            run_btn = gr.Button("🚀 실행", variant="primary", size="lg")

        # ── 오른쪽: 결과 패널 ────────────────────────────
        with gr.Column(scale=2):
            gr.Markdown("### 📝 결과")
            answer_box = gr.Textbox(label="Answer", lines=10, interactive=False)
            sources_box = gr.Textbox(
                label="Retrieved Sources", lines=10, interactive=False
            )

    run_btn.click(
        fn=run_demo,
        inputs=[
            q_input, config_dd, top_k_sl,
            chunk_size_sl, chunk_overlap_sl,
            max_tokens_sl, temperature_sl,
        ],
        outputs=[answer_box, sources_box],
    )

    gr.Markdown(
        """
---
🔗 [GitHub Repo](https://github.com/Ontology0/Graduation-Project) ·
[아키텍처](https://github.com/Ontology0/Graduation-Project/blob/main/docs/architecture.md) ·
[연구 계획](https://github.com/Ontology0/Graduation-Project/blob/main/docs/research_plan.md)
"""
    )

if __name__ == "__main__":
    demo.launch()
