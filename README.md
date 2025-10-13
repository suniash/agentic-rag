# Agentic RAG Learning Hub

The goal of this repository is to serve as a **technical playbook** for teams who want to build production-ready Agentic Retrieval-Augmented Generation (RAG) systems. Inside you will find:

| Resource | What it covers |
| --- | --- |
| [`docs/agentic_rag_beginner_guide.md`](docs/agentic_rag_beginner_guide.md) | Medium-style explainer that walks through the “why”, “what”, and “how” of agentic RAG along with implementation blueprints and checklists. |
| [`example_app/`](example_app/) | Runnable Python project that demonstrates document ingestion, agent orchestration, evaluation hooks, and a CLI chat interface. |

## Who this is for

* **Founders & product leaders** evaluating whether agentic RAG can unlock new capabilities in their product.
* **Engineers & data scientists** who need reference implementations, design decisions, and operational guidance.
* **Technical writers & advocates** crafting educational content (e.g., Medium posts) that requires reproducible examples.

## Quick start

1. **Read the playbook** – The article in `docs/` lays the conceptual foundation, references best practices, and highlights common pitfalls.
2. **Run the example app** – Follow the setup instructions in [`example_app/README.md`](example_app/README.md) to ingest documents and chat with the agent locally.
3. **Adapt to your use case** – Swap out the sample knowledge base, register new tools, and plug the evaluation harness into your own prompts to accelerate experimentation.

## Repository structure

```
├── docs/
│   └── agentic_rag_beginner_guide.md   # Theory + playbook + deployment guidance
├── example_app/
│   ├── README.md                       # Setup and usage instructions
│   ├── data/                           # Sample knowledge base
│   ├── evaluation/                     # Lightweight evaluation harness
│   ├── ingest.py                       # Build the FAISS vector store
│   ├── evaluate.py                     # Run automated retrieval/answering checks
│   └── main.py                         # Interactive CLI agent
└── README.md                           # You are here
```

> ℹ️ **OpenAI API key required** – Export `OPENAI_API_KEY` before running the example application. Additional environment configuration tips are documented in `example_app/README.md`.

## Contributing

Have ideas to improve the playbook or example app? Open an issue or submit a pull request with enhancements such as:

- Additional tool integrations (SQL, REST, analytics, etc.).
- Observability and evaluation utilities.
- Deployment recipes for serverless, containers, or chat platforms.

Together we can make this a go-to resource for the agentic RAG community.
