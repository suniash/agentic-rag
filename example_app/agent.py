"""Utilities for constructing the agentic RAG assistant used across CLI tools."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Tuple

from dotenv import load_dotenv
from langchain.agents import AgentExecutor, AgentType, initialize_agent
from langchain.schema.document import Document
from langchain.tools import Tool
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI, OpenAIEmbeddings


@dataclass
class AgentConfig:
    """Configuration parameters for the agent and retrieval stack."""

    model: str = "gpt-4.1-mini"
    temperature: float = 0.0
    embedding_model: str = "text-embedding-3-small"
    top_k: int = 4
    max_iterations: int = 4
    verbose: bool = False


def load_vectorstore(embedding_model: str) -> FAISS:
    """Load the FAISS index built by :mod:`ingest`."""

    store_dir = Path(__file__).parent / "stores" / "help_center"
    if not store_dir.exists():
        raise FileNotFoundError(
            "Vector store not found. Run `python ingest.py` before starting the assistant."
        )

    embeddings = OpenAIEmbeddings(model=embedding_model)
    return FAISS.load_local(
        str(store_dir), embeddings, allow_dangerous_deserialization=True
    )


def format_documents(documents: Iterable[Document]) -> str:
    """Return a human-readable string with document snippets and metadata."""

    formatted: List[str] = []
    for idx, doc in enumerate(documents, start=1):
        source = doc.metadata.get("source", "knowledge base")
        title = doc.metadata.get("title")
        header = f"[{idx}] {title} — {source}" if title else f"[{idx}] {source}"
        formatted.append(f"{header}\n{doc.page_content.strip()}".strip())
    return "\n\n".join(formatted)


def build_agent(config: AgentConfig) -> Tuple[AgentExecutor, FAISS]:
    """Instantiate the LangChain agent and its retriever with the provided config."""

    load_dotenv()
    vectorstore = load_vectorstore(config.embedding_model)
    retriever = vectorstore.as_retriever(search_kwargs={"k": config.top_k})

    def search_help_center(query: str) -> str:
        docs = retriever.get_relevant_documents(query)
        if not docs:
            return "No relevant documents found."
        return format_documents(docs)

    tools = [
        Tool(
            name="help_center_search",
            func=search_help_center,
            description=(
                "Use this when answering questions about NimbusWorkspaces accounts, "
                "billing, limits, or troubleshooting. Input should be a natural "
                "language question."
            ),
        )
    ]

    llm = ChatOpenAI(model=config.model, temperature=config.temperature)

    agent = initialize_agent(
        tools,
        llm,
        agent=AgentType.OPENAI_FUNCTIONS,
        verbose=config.verbose,
        max_iterations=config.max_iterations,
        handle_parsing_errors=True,
    )

    return agent, retriever


__all__ = ["AgentConfig", "build_agent", "format_documents", "load_vectorstore"]
