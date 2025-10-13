# Agentic RAG Playbook: From Strategy to Shipping

*By the Agentic RAG Learning Hub*

> **TL;DR** – Agentic RAG fuses retrieval-augmented generation with autonomous tool selection. This playbook distils the concepts, architecture patterns, and operational checklists you need to build reliable assistants. The accompanying Python project showcases the core loop with LangChain, FAISS, and OpenAI’s APIs so you can ship faster.

---

## 0. Executive summary

Agentic RAG is best suited for scenarios where a language model must reason over proprietary or fast-changing knowledge without hallucinating. The agent orchestrates tools (retrievers, APIs, calculators) and dynamically decides what to call next. Success hinges on **data quality**, **observability**, and **tight feedback loops** between engineering and subject-matter experts.

| Phase | Objective | Key deliverables |
| --- | --- | --- |
| Discover | Validate that agentic RAG solves the user problem better than static search or scripted workflows. | Problem brief, user stories, baseline metrics. |
| Design | Model the knowledge flows, tools, and guardrails the agent will use. | Context map, tool specs, evaluation rubric. |
| Build | Implement ingestion pipelines, vector search, and the agent policy. | Working ingestion job, retriever, agent harness, integration tests. |
| Evaluate | Measure quality, latency, and cost; iterate on prompts, chunking, and tools. | Automated eval suite, human review template. |
| Deploy | Integrate with production surfaces and monitoring. | Deployment playbook, on-call runbooks, dashboards. |

Each section that follows maps to these phases and references the sample project for concrete code.

---

## 1. Why Agentic RAG?

Large language models (LLMs) are strong generalists but struggle with organisation-specific knowledge. Retrieval-Augmented Generation (RAG) closes the gap by letting the model ground responses in an external knowledge base. **Agentic RAG** adds an orchestration layer so the model can:

1. Decide *when* retrieval is necessary versus when cached context suffices.
2. Chain multiple tools together (retrievers, calculators, APIs) within a single response.
3. Explain its reasoning trail (tool calls, citations) to build trust with end users.

### Typical use cases

- Customer support copilots and ticket summarisation.
- Internal knowledge assistants for operations, legal, or sales teams.
- Research copilots that mix documentation search with analytical tools.
- Developer experience bots combining docs, repositories, and build tooling.

### Core benefits

- **Grounded answers** – Responses reference curated knowledge instead of hallucinated facts.
- **Composable skills** – Adding new tools expands the assistant’s capabilities without retraining.
- **Adaptive reasoning** – The agent explores, observes, and revises before committing to an answer.

---

## 2. Architecture reference

```
┌────────────┐      ┌──────────────────┐      ┌────────────────┐
│ End user   │─────▶│  Agent policy    │─────▶│ Tooling layer  │
└────────────┘      │  (LLM + memory)  │      │ (retrieval/API │
                    └───────┬──────────┘      │  adapters etc.)│
                            │                 └───────▲────────┘
                            ▼                         │
                    ┌──────────────┐                 │
                    │ Knowledge DB │◀────────────────┘
                    │ (vector +    │
                    │  metadata)   │
                    └──────────────┘
```

### Essential components

| Component | Responsibilities | Design notes |
| --- | --- | --- |
| **LLM policy** | Plans actions, calls tools, synthesises final response. | Start with OpenAI `gpt-4o-mini` or `gpt-4.1`. Tune temperature and max iterations to control behaviour. |
| **Retriever** | Converts questions into embeddings and fetches similar chunks. | Pair `text-embedding-3-small` with FAISS for local experiments; move to managed stores for scale. |
| **Memory** | Persists dialogue history, tool outcomes, and metadata. | Track the agent trace for debugging. LangChain callback handlers or LangSmith help. |
| **Guardrails** | Enforce safety, compliance, or budget constraints. | Add filters before/after tool calls (e.g., redact PII, limit token spend). |

### Tool taxonomy

1. **Knowledge tools** – Vector search, keyword search, graph databases.
2. **Computation tools** – SQL query runners, calculators, analytics APIs.
3. **Action tools** – Ticket creation, CRM updates, workflow automation.

Start with knowledge tools, then gradually add computation/action tools once retrieval quality is stable.

---

## 3. Playbook by phase

### 3.1 Discover

- Interview users to understand their existing workflows and failure modes.
- Gather baseline metrics (resolution time, CSAT, cost per conversation).
- Identify “source of truth” documents and the systems of record you must integrate.

**Checklist**

| Question | Why it matters |
| --- | --- |
| What decisions will the agent make autonomously? | Determines tool scope and guardrail needs. |
| How fresh must the knowledge be? | Drives ingestion frequency and caching strategy. |
| What failure is acceptable? | Guides evaluation metrics (precision vs. recall). |

### 3.2 Design

- Model the knowledge graph: entities (plans, policies) and relationships (prerequisites, escalations).
- Choose embedding models and chunking strategies for each content type.
- Define tool interfaces (input schema, output schema, latency budget).
- Decide on agent loop (ReAct, tools + function calling, LangGraph state machines).

**Design doc template**

1. **User stories** – e.g., “As a support agent I want a 1-click summary with cited sources.”
2. **Context map** – Diagram of data sources, transforms, and access controls.
3. **Risk register** – Hallucination, stale data, cost spikes, compliance.
4. **Guardrails** – Max tokens per conversation, allowed tools, fallback policies.

### 3.3 Build

- Implement ingestion pipelines that clean, enrich, and chunk documents.
- Set up a vector store (FAISS locally, Pinecone/Chroma/Weaviate in production).
- Build the agent harness. Start with deterministic prompts and instrumentation turned on.
- Add tracing via LangSmith, OpenTelemetry, or custom logging.

**Pattern: ingestion job**

```python
splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=120)
splits = splitter.split_documents(docs)
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
faiss = FAISS.from_documents(splits, embeddings)
faiss.save_local("stores/help_center")
```

**Pattern: register tools**

```python
help_center = Tool(
    name="help_center_search",
    description="Ground answers using internal documentation.",
    func=lambda q: format_docs(retriever.get_relevant_documents(q)),
)

calculator = Tool(
    name="plan_pricing_calculator",
    description="Compute monthly price deltas when users change seats.",
    func=pricing_api.calculate,
)
```

### 3.4 Evaluate

- Build a regression suite of real user questions with authoritative answers.
- Measure hit rate (retrieved documents contain the gold answer) and answer quality (BLEU, ROUGE, LLM-as-judge).
- Track latency (P95) and token usage per turn.
- Run “what if” tests when updating prompts, chunking, or tool inventory.

**Prompted eval snippet** (see `example_app/evaluate.py`):

```python
for case in eval_cases:
    result = agent.invoke({"input": case.question})
    score = judge.grade(
        answer=result["output"],
        context="\n".join(case.references),
    )
```

### 3.5 Deploy & operate

- Wrap the agent behind a web/chat UI or embed into existing workflows.
- Add observability: structured logs, cost tracking, trace visualisation.
- Define rollback levers (disable tools, revert prompts, fall back to retrieval-only responses).
- Set up on-call runbooks with troubleshooting steps (check vector freshness, API quotas, latency graphs).

**Operational guardrails**

- Hard token ceilings per session to avoid runaway costs.
- Circuit breakers that short-circuit to a safe response when tools fail.
- Rate limiting on external APIs (billing, CRM, etc.).
- Continuous ingestion tests to ensure new documents are chunked + indexed correctly.

---

## 4. Walking through the sample project

The `example_app` directory is a compact sandbox demonstrating the playbook.

### 4.1 Project highlights

- **Configurable agent** – Choose the chat model, temperature, top-k retrieval, and iteration limits via CLI flags.
- **Document ingestion** – Run `python ingest.py` to create a FAISS index from markdown files.
- **Evaluation harness** – Use `python evaluate.py` to sanity-check retrieval quality against a curated question set.
- **Verbose tracing** – Turn on/off LangChain debug logs with the `--verbose` flag.

```
example_app/
├── data/help_center.md            # Seed documentation
├── evaluation/cases.yaml          # Regression-style evaluation prompts
├── evaluate.py                    # Executes cases and aggregates scores
├── ingest.py                      # Cleans + indexes documents
└── main.py                        # CLI agent with configurable settings
```

### 4.2 Setup recap

```bash
cd example_app
python -m venv .venv
source .venv/bin/activate  # On Windows use .venv\Scripts\activate
pip install -r requirements.txt
export OPENAI_API_KEY="sk-your-key"
python ingest.py
```

Start chatting:

```bash
python main.py --model gpt-4o-mini --top-k 4
```

Run the evaluation harness:

```bash
python evaluate.py --cases evaluation/cases.yaml
```

### 4.3 How the agent works

1. Loads the FAISS store and wraps it in a retriever.
2. Registers tools (currently only `help_center_search`).
3. Instantiates a LangChain OpenAI Functions agent with configurable iterations.
4. Streams the reasoning trace (thought, action, observation) when verbose mode is enabled.
5. Prints the final answer with inline citations.

You can expand the `tools` list with your own integrations (SQL, Slack, Jira) as long as they follow LangChain’s `Tool` signature.

### 4.4 Extending the sandbox

- Add metadata enrichers (tags, access levels) during ingestion and expose them via retriever filters.
- Introduce a “respond with structured JSON” tool for downstream automation.
- Replace FAISS with a hosted vector database when documents exceed millions of chunks.
- Swap the CLI for a FastAPI or Streamlit interface to demo live conversations.

---

## 5. Best practices & guardrails

1. **Data hygiene first** – Deduplicate documents, canonicalise URLs, and strip boilerplate before embedding.
2. **Chunk with intent** – Align chunk boundaries with semantic sections (headings, bullet lists). Overlap 10–20% to preserve context.
3. **Instrument everything** – Capture traces, tool I/O, and token counts. The boring logs unblock debugging.
4. **Favor determinism in prompts** – Explicit instructions and structured outputs reduce variance and improve eval repeatability.
5. **Plan for drift** – Schedule ingest jobs, re-run eval suites nightly, and monitor accuracy metrics for regressions.
6. **Respect compliance** – Implement access controls and audit logs when dealing with sensitive data.

---

## 6. Further reading & tooling

- [LangChain documentation](https://python.langchain.com) – Agents, tools, callbacks, LangGraph.
- [OpenAI API docs](https://platform.openai.com/docs) – Models, pricing, best practices for prompt engineering.
- [Guardrails.ai](https://www.guardrailsai.com/) & [NeMo Guardrails](https://docs.nvidia.com/nemo/guardrails/) – Layer safety policies over agent responses.
- [Evaluation frameworks](https://github.com/openai/evals), [Ragas](https://github.com/explodinggradients/ragas) – Automate RAG quality measurement.
- [Vector DB comparisons](https://www.pinecone.io/learn/vector-database/) – Choose the right store for scale and latency.

Agentic RAG is a journey: instrument early, iterate often, and collaborate closely with the humans who rely on the assistant. This playbook plus the sample project should help you go from idea to a trustworthy, maintainable system.

Happy building! 🚀
