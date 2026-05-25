"""Legacy stub — preserved for backward compatibility.

The real pipeline is now in ``rag.pipeline.RAGPipeline``.
This file re-exports the pipeline's query interface so existing
references (e.g. README examples) keep working.
"""

from rag.pipeline import RAGPipeline  # noqa: F401


def run_rag_placeholder(question: str) -> dict:
    """Lightweight demo that returns a fixed response.

    For the real pipeline, use ``RAGPipeline.from_config()`` instead.
    """
    return {
        "method": "rag",
        "status": "migrated",
        "answer": "See rag.pipeline.RAGPipeline for the implemented pipeline.",
        "question": question,
    }


if __name__ == "__main__":
    print(run_rag_placeholder("example question"))
