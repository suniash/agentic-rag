"""Interactive agentic RAG assistant for the NimbusWorkspaces knowledge base."""

from __future__ import annotations

import argparse
from dataclasses import replace

from agent import AgentConfig, build_agent, format_documents


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments for configuring the chat session."""

    default_config = AgentConfig()

    parser = argparse.ArgumentParser(
        description="Chat with the NimbusWorkspaces agentic RAG assistant."
    )
    parser.add_argument(
        "--model",
        default=default_config.model,
        help="OpenAI chat model to use for the agent policy.",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=default_config.temperature,
        help="Sampling temperature for the chat model.",
    )
    parser.add_argument(
        "--embedding-model",
        default=default_config.embedding_model,
        help="Embeddings model used to load the FAISS index.",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=default_config.top_k,
        help="Number of documents to retrieve per query.",
    )
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=default_config.max_iterations,
        help="Maximum tool invocations per turn before the agent stops.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        default=default_config.verbose,
        help="Enable verbose LangChain tracing (thought/action logs).",
    )
    parser.add_argument(
        "--show-sources",
        action="store_true",
        help="Display the top retrieved documents after each answer.",
    )
    return parser.parse_args()


def main() -> None:
    """Launch a CLI chat loop with configurable agent settings."""

    args = parse_args()
    config = replace(
        AgentConfig(),
        model=args.model,
        temperature=args.temperature,
        embedding_model=args.embedding_model,
        top_k=args.top_k,
        max_iterations=args.max_iterations,
        verbose=args.verbose,
    )

    agent, retriever = build_agent(config)

    print("NimbusWorkspaces Support Assistant")
    print("Type 'exit' or 'quit' to end the chat.\n")

    while True:
        try:
            user_input = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_input:
            continue

        if user_input.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break

        result = agent.invoke({"input": user_input})
        print(f"\n{result['output']}\n")

        if args.show_sources:
            docs = retriever.get_relevant_documents(user_input)
            if docs:
                print("Top sources:\n")
                print(format_documents(docs))
                print()


if __name__ == "__main__":
    main()
