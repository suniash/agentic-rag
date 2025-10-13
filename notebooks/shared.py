"""Shared helpers for the Agentic RAG notebook curriculum."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

from dotenv import load_dotenv
from langchain.chains import RetrievalQA
from langchain.schema import BaseRetriever
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI as LangChainChatOpenAI
from langchain_openai import OpenAIEmbeddings

# Re-exported constants keep the notebooks concise and consistent.
DATA_DIR = Path(__file__).resolve().parent.parent / "example_app" / "data"
STORE_DIR = Path(__file__).resolve().parent.parent / "example_app" / "stores" / "help_center"
DEFAULT_MODEL = "gpt-4.1-mini"
DEFAULT_EMBEDDING_MODEL = "text-embedding-3-small"


@dataclass
class RetrievalContext:
    """Bundle of objects that most notebooks need for retrieval demos."""

    vectorstore: FAISS
    retriever: BaseRetriever


def ensure_vectorstore(embedding_model: str = DEFAULT_EMBEDDING_MODEL) -> FAISS:
    """Load the FAISS store, instructing the reader to run the ingest script if missing."""

    load_dotenv()
    if not STORE_DIR.exists():
        raise FileNotFoundError(
            "Vector store missing. Run `python example_app/ingest.py` before executing the notebooks."
        )

    embeddings = OpenAIEmbeddings(model=embedding_model)
    return FAISS.load_local(str(STORE_DIR), embeddings, allow_dangerous_deserialization=True)


def build_retrieval_context(top_k: int = 4) -> RetrievalContext:
    """Return a retrieval context with a reusable FAISS-backed retriever."""

    vectorstore = ensure_vectorstore()
    retriever = vectorstore.as_retriever(search_kwargs={"k": top_k})
    return RetrievalContext(vectorstore=vectorstore, retriever=retriever)


def load_raw_documents() -> List[str]:
    """Return the raw Markdown knowledge base as strings for ad-hoc experiments."""

    loader = DirectoryLoader(str(DATA_DIR), glob="**/*.md", loader_cls=TextLoader)
    documents = loader.load()
    return [doc.page_content for doc in documents]


def build_baseline_chain(retriever: BaseRetriever) -> RetrievalQA:
    """Construct a simple RetrievalQA chain used in several notebooks."""

    llm = LangChainChatOpenAI(model=DEFAULT_MODEL, temperature=0.0)
    return RetrievalQA.from_chain_type(llm=llm, retriever=retriever)


def pretty_print_json(payload: Dict[str, Any]) -> str:
    """Return a formatted JSON string useful for logging agent traces."""

    return json.dumps(payload, indent=2, ensure_ascii=False)


def time_execution(callable_fn, *args, **kwargs) -> Dict[str, Any]:
    """Measure runtime of a callable and surface both the result and elapsed seconds."""

    start = time.perf_counter()
    result = callable_fn(*args, **kwargs)
    elapsed = time.perf_counter() - start
    return {"result": result, "elapsed_seconds": elapsed}


__all__ = [
    "RetrievalContext",
    "build_baseline_chain",
    "build_retrieval_context",
    "DEFAULT_MODEL",
    "DEFAULT_EMBEDDING_MODEL",
    "ensure_vectorstore",
    "load_raw_documents",
    "pretty_print_json",
    "time_execution",
]
