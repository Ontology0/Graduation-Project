"""RAG pipeline placeholder: defines the future entrypoint shape without I/O or model calls."""


def run_rag_placeholder(question: str) -> dict:
    """Return a fixed stub response; no retrieval or generation is performed."""
    return {
        "method": "rag",
        "status": "not_implemented",
        "answer": "RAG pipeline is not implemented yet.",
        "question": question,
    }


if __name__ == "__main__":
    print(run_rag_placeholder("example question"))
