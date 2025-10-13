# Agentic RAG Example Application

This directory contains a runnable Python project that demonstrates how to build an **agentic Retrieval-Augmented Generation (RAG)** assistant. The agent answers support questions about a fictional SaaS product (NimbusWorkspaces) by consulting a local knowledge base.

## Features

- Uses **LangChain** to orchestrate an OpenAI-powered agent and retrieval tool.
- Stores embeddings in a local **FAISS** vector index generated from markdown documents.
- Provides a configurable CLI chat interface that surfaces reasoning traces and sources on demand.
- Includes a lightweight evaluation harness so you can regression-test prompt and data changes.

## 1. Prerequisites

- Python 3.9+
- An OpenAI API key with access to GPT-4o mini and text-embedding-3-small.
- Optional: create a `.env` file with `OPENAI_API_KEY=...` to simplify configuration.

## 2. Installation

```bash
cd example_app
python -m venv .venv
source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
pip install -r requirements.txt
```

Create a `.env` file (or export the variable in your shell):

```
OPENAI_API_KEY=sk-your-key
```

## 3. Build the knowledge base index

Populate the FAISS index from the markdown files located in `data/`:

```bash
python ingest.py
```

You can add your own `.txt` or `.md` files to the `data/` folder before running the ingestion script.

## 4. Run the agentic assistant

Start the chat loop once the index is ready:

```bash
python main.py --model gpt-4o-mini --top-k 4 --verbose --show-sources
```

Key CLI flags:

| Flag | Description |
| --- | --- |
| `--model` | Choose the OpenAI chat model for the agent policy (default `gpt-4o-mini`). |
| `--temperature` | Adjust response creativity (default `0.0`). |
| `--embedding-model` | Embeddings model used for FAISS loading (default `text-embedding-3-small`). |
| `--top-k` | Number of documents retrieved per query. |
| `--max-iterations` | Cap the number of tool calls per turn. |
| `--verbose` | Stream LangChain’s intermediate thoughts and actions. |
| `--show-sources` | Display the top retrieved chunks after each answer. |

Example conversation:

```
NimbusWorkspaces Support Assistant
Type 'exit' or 'quit' to end the chat.

> How do I reset my password?

Thought: I should consult the help centre articles.
Action: help_center_search
Action Input: How do I reset my password?
Observation: ...
Final Answer: To reset your NimbusWorkspaces password, visit https://nimbus.example.com/login and click "Forgot password". Enter your email and follow the link in your inbox. If it doesn't arrive within five minutes, ask a workspace Owner to send a manual reset from the Members panel.
```

Press `Ctrl+C`, or type `exit`, to stop the assistant.

## 5. Run regression-style evaluations

The `evaluate.py` script executes scripted questions against the agent and checks whether certain phrases are present in the response. This guards against regressions when you modify prompts, documents, or retrieval parameters.

```bash
python evaluate.py --cases evaluation/cases.yaml --show-context
```

Each case inside `evaluation/cases.yaml` specifies:

- `question` – the prompt issued to the agent.
- `must_include` – phrases that must appear in the answer (case-insensitive).
- `notes` – context on what the case verifies.

You can add more cases or wire this script into CI to catch regressions automatically.

## 6. Next steps

- Add more documents to expand the knowledge base.
- Register additional tools (e.g., REST APIs, analytics dashboards) in `main.py` to make the agent more capable.
- Deploy the agent behind a web or chat UI for real users.

Have fun exploring agentic RAG! 🚀
