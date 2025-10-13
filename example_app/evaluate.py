"""Lightweight regression harness for the agentic RAG example."""

from __future__ import annotations

import argparse
from dataclasses import dataclass, replace
from pathlib import Path
from typing import List, Sequence

import yaml

from agent import AgentConfig, build_agent, format_documents


@dataclass
class EvalCase:
    """Single evaluation prompt with required phrases."""

    id: str
    question: str
    must_include: Sequence[str]
    notes: str = ""


@dataclass
class CaseResult:
    """Outcome of running the agent against an evaluation case."""

    case: EvalCase
    answer: str
    missing_phrases: List[str]
    retrieved_snippets: str

    @property
    def passed(self) -> bool:
        return not self.missing_phrases


def parse_args() -> argparse.Namespace:
    default_config = AgentConfig()

    parser = argparse.ArgumentParser(
        description="Run regression-style checks against the agentic RAG assistant.",
    )
    parser.add_argument(
        "--cases",
        default=str(Path(__file__).parent / "evaluation" / "cases.yaml"),
        help="Path to a YAML file describing evaluation cases.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Optional limit on the number of cases to execute.",
    )
    parser.add_argument(
        "--fail-fast",
        action="store_true",
        help="Stop running once a case fails.",
    )
    parser.add_argument(
        "--show-context",
        action="store_true",
        help="Print retrieved document snippets for each case.",
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
        help="Number of documents to retrieve per question.",
    )
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=default_config.max_iterations,
        help="Maximum tool invocations per question.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        default=default_config.verbose,
        help="Enable verbose LangChain tracing.",
    )
    return parser.parse_args()


def load_cases(path: Path) -> List[EvalCase]:
    """Parse YAML into EvalCase objects."""

    data = yaml.safe_load(path.read_text())
    if not data or "cases" not in data:
        raise ValueError(f"No cases found in {path}")

    cases: List[EvalCase] = []
    for raw in data["cases"]:
        cases.append(
            EvalCase(
                id=raw["id"],
                question=raw["question"],
                must_include=tuple(raw.get("must_include", [])),
                notes=raw.get("notes", ""),
            )
        )
    return cases


def evaluate_case(agent, retriever, case: EvalCase) -> CaseResult:
    """Run the agent and collect pass/fail metadata."""

    result = agent.invoke({"input": case.question})
    answer = result["output"].strip()
    lower_answer = answer.lower()
    missing = [
        phrase
        for phrase in case.must_include
        if phrase.lower() not in lower_answer
    ]

    docs = retriever.get_relevant_documents(case.question)
    snippets = format_documents(docs) if docs else ""

    return CaseResult(
        case=case,
        answer=answer,
        missing_phrases=missing,
        retrieved_snippets=snippets,
    )


def run() -> None:
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

    cases = load_cases(Path(args.cases))
    if args.limit is not None:
        cases = cases[: args.limit]

    agent, retriever = build_agent(config)

    results: List[CaseResult] = []
    for case in cases:
        result = evaluate_case(agent, retriever, case)
        results.append(result)

        status = "PASS" if result.passed else "FAIL"
        print(f"[{status}] {case.id} — {case.question}")
        if case.notes:
            print(f"  Notes: {case.notes}")
        if result.missing_phrases:
            print(f"  Missing phrases: {', '.join(result.missing_phrases)}")
        if args.show_context and result.retrieved_snippets:
            print("  Retrieved snippets:\n")
            print(indent_block(result.retrieved_snippets, prefix="    "))
        print()

        if args.fail_fast and not result.passed:
            break

    passed = sum(1 for r in results if r.passed)
    total = len(results)
    if total:
        print(f"Summary: {passed}/{total} cases passed")
    else:
        print("No cases executed.")


def indent_block(text: str, prefix: str) -> str:
    return "\n".join(f"{prefix}{line}" for line in text.splitlines())


if __name__ == "__main__":
    run()
