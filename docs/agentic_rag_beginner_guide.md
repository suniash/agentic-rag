# Agentic RAG Playbook: From Strategy to Shipping

*By the Agentic RAG Learning Hub*

> **TL;DR** – Agentic RAG fuses retrieval-augmented generation with autonomous tool selection. This playbook distils the concepts, architecture patterns, and operational checklists you need to build reliable assistants. Pair it with the new Jupyter curriculum in `../notebooks/` and the accompanying Python project to see each architecture running with LangChain, FAISS, and OpenAI’s APIs.

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

### Traditional vs. agentic retrieval pipelines

- **Classic RAG** follows a largely linear path: accept a user query, embed it, retrieve the top-*k* documents, and hand the bundle to an LLM for answer synthesis. The model has little autonomy over *how* to search or whether to continue searching once a draft answer exists. ([Wikipedia](https://en.wikipedia.org/wiki/Retrieval-augmented_generation), [Weaviate](https://weaviate.io/blog/what-is-agentic-rag))
- **Agentic RAG** introduces a control plane—often realised as one or more agents—that can plan, branch, verify, and iterate. The agent decides which sources to consult, whether to hand off subtasks to specialised peers, when to stop, and how to resolve conflicting evidence. ([IBM](https://www.ibm.com/think/topics/agentic-rag), [IEEE Computer Society](https://www.computer.org/publications/tech-news/trends/agentic-rag/), [Agentic RAG survey](https://arxiv.org/abs/2501.09136))

You can view agentic RAG as turning a static pipeline into a dynamic workflow. The autonomy pays off when queries are open-ended, data lives in multiple systems, or the cost of wrong answers is high enough to justify iterative reasoning.

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
| **LLM policy** | Plans actions, calls tools, synthesises final response. | Start with OpenAI `gpt-4.1-mini` or `gpt-4.1`. Tune temperature and max iterations to control behaviour. |
| **Retriever** | Converts questions into embeddings and fetches similar chunks. | Pair `text-embedding-3-small` with FAISS for local experiments; move to managed stores for scale. |
| **Memory** | Persists dialogue history, tool outcomes, and metadata. | Track the agent trace for debugging. LangChain callback handlers or LangSmith help. |
| **Guardrails** | Enforce safety, compliance, or budget constraints. | Add filters before/after tool calls (e.g., redact PII, limit token spend). |

### Tool taxonomy

1. **Knowledge tools** – Vector search, keyword search, graph databases.
2. **Computation tools** – SQL query runners, calculators, analytics APIs.
3. **Action tools** – Ticket creation, CRM updates, workflow automation.

Start with knowledge tools, then gradually add computation/action tools once retrieval quality is stable.

### Canonical agentic RAG architectures

| Pattern | When to use | How it works | Notes |
| --- | --- | --- | --- |
| **Planner–executor** | Complex questions that require decomposition. | A planner agent breaks the user goal into sub-queries, dispatches retrieval/execution agents, and collates their outputs. Mirrors "Reasoning → Retrieval → Verification" flows popularised by LangGraph and CrewAI. | Keep planner prompts deterministic to avoid runaway tool calls. |
| **Dynamic retriever selector** | Multiple heterogeneous data sources (internal docs, APIs, web). | A classifier chooses the most relevant retriever for the query (e.g., Wikipedia vs. product manuals) before synthesis. | Pair with routing telemetry to audit which corpus was used. |
| **Self-reflective agent** | Domains where incorrect answers are costly. | The agent scores its own draft (using RAGAS, cosine similarity, or an LLM judge) and re-queries if confidence is low. | Cap the number of reflection loops to control latency. |
| **Multi-agent orchestrator** | Scenarios that benefit from specialists (researcher, analyst, verifier). | A coordination agent activates peer agents, adjudicates conflicting evidence, and can backtrack. Examples include MAO-ARAG and ARAG. ([MAO-ARAG](https://arxiv.org/abs/2508.01005), [ARAG](https://arxiv.org/abs/2506.21931)) | Demands robust observability to trace the agent graph. |

Architectures like DecEx-RAG add process supervision to reward efficient plans, while benchmarks such as InfoDeepSeek stress-test systems in dynamic web environments. ([DecEx-RAG](https://arxiv.org/abs/2510.05691), [InfoDeepSeek](https://arxiv.org/abs/2505.15872))

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

### 3.6 What learners ask for (and how to respond)

Acting as developer advocates, we collected recurring questions from engineers, analysts, and founders who trial the repository. Use the responses below to unblock yourself or your teammates.

| Concern | Why it surfaces | Recommended response |
| --- | --- | --- |
| “I’m overwhelmed—what should I run first?” | Newcomers are unsure whether to read docs, run code, or open notebooks. | Point them to the persona-based journeys in [`docs/learning_pathways.md`](learning_pathways.md) so they can map time available to outcomes. |
| “How do I know the agent actually improved vs. classic RAG?” | Without metrics, stakeholders see agentic workflows as extra complexity. | Capture before/after measurements using `example_app/evaluate.py` and `notebooks/8_comparative_evaluation.ipynb`, then share a delta table. |
| “Why is setup taking so long?” | Environment friction (API keys, dependencies) derails workshops. | Recommend the virtualenv instructions in `notebooks/README.md` and include a preflight checklist (API key, FAISS store built, notebooks opened). |
| “What does good observability look like?” | Teams lack examples of actionable traces. | Enable verbose mode in `example_app/main.py`, save trace snippets, and annotate them in docs or Looms. Pair with the Operator checklist in [`docs/learning_pathways.md`](learning_pathways.md). |
| “How do I explain this to leadership?” | Leaders want artifacts that show readiness. | Encourage teams to fill out the Learning Evidence Checklist in [`docs/learning_pathways.md`](learning_pathways.md) to produce a shareable bundle (metrics, lessons, screenshots). |

Collecting these FAQs as artifacts (recordings, issues, wiki pages) compounds over time and turns every cohort’s feedback into better onboarding material.

---

## 4. Market pulse: 2025 snapshot

| Trend / development | What’s new or interesting | Why it matters / implications |
| --- | --- | --- |
| **New architectures and research advances** | *DecEx-RAG* (Oct 2025) optimises agent decisions via process supervision; *MAO-ARAG* (Aug 2025) introduces adaptive multi-agent orchestration; *ARAG* targets personalised recommendations; *InfoDeepSeek* benchmarks open-world information seeking. ([DecEx-RAG](https://arxiv.org/abs/2510.05691), [MAO-ARAG](https://arxiv.org/abs/2508.01005), [ARAG](https://arxiv.org/abs/2506.21931), [InfoDeepSeek](https://arxiv.org/abs/2505.15872)) | Research is shifting from proof-of-concept to efficiency, orchestration quality, and realistic evaluation. |
| **Emergence of commercial / product efforts** | Progress Software launched an Agentic RAG platform and acquired Nuclia; NVIDIA is packaging workshops that combine Nemotron models with LangGraph; industry debate is reframing "traditional vs. agentic" RAG as the new default. ([Digitalisation World](https://digitalisationworld.com/news/70876/progress-software-unveils-agentic-rag-platform), [Progress–Nuclia](https://investors.progress.com/news-releases/news-release-details/progress-software-acquires-nuclia-innovator-agentic-rag-ai), [NVIDIA workshop](https://developer.nvidia.com/blog/build-a-rag-agent-with-nvidia-nemotron/), [NVIDIA agentic](https://developer.nvidia.com/blog/traditional-rag-vs-agentic-rag-why-ai-agents-need-dynamic-knowledge-to-get-smarter/)) | Tooling and go-to-market motions signal that agentic RAG is moving into mainstream enterprise stacks. |
| **Enterprise adoption, use cases, and caution** | IBM champions "AI detective" systems for support, legal, and compliance while highlighting governance risks; cybersecurity teams are piloting agentic AI with guarded optimism; commentators argue classic RAG falls short for enterprise needs. ([IBM](https://www.ibm.com/think/news/ai-detectives-agentic-rag), [Axios](https://www.axios.com/2025/03/27/agentic-ai-cybersecurity-microsoft-crowdstrike), [TechRadar](https://www.techradar.com/pro/rag-is-dead-why-enterprises-are-shifting-to-agent-based-ai-architectures)) | Adoption hinges on trust, auditability, and safety rather than raw model capability. |
| **Risks, challenges, and open problems** | Error cascades and hallucinations persist; security and RBAC become harder with agents touching many systems; orchestration raises cost/latency; training good policies demands thoughtful rewards; benchmarking real-world behaviour remains difficult; explainability is mandatory. ([IBM](https://www.ibm.com/think/news/ai-detectives-agentic-rag), [DecEx-RAG](https://arxiv.org/abs/2510.05691), [InfoDeepSeek](https://arxiv.org/abs/2505.15872)) | Most production systems still operate with conservative guardrails and human oversight. |
| **Evolving narratives & projections** | Pundits declare "RAG is dead, long live agentic retrieval"; the notion of an agentic web of interoperable agents gains attention; focus shifts from model scale to orchestration intelligence. ([LlamaIndex](https://www.llamaindex.ai/blog/rag-is-dead-long-live-agentic-retrieval), [Agentic Web](https://en.wikipedia.org/wiki/Agentic_Web)) | Expect future stacks to bundle planner–executor graphs, tool ecosystems, and governance by default. |

---

## 5. Where agentic RAG is heading

1. **Hybrid human-in-the-loop workflows** – Fully autonomous operation is rare; expect review, escalation, and feedback paths to stay in the loop.
2. **Adaptive orchestration and meta-agents** – Planner agents that activate the right specialists (e.g., MAO-ARAG-style) to balance quality and cost.
3. **Process-supervised training** – Reward agents for efficient tool use and penalise dead ends, as demonstrated in DecEx-RAG.
4. **Richer benchmarks and eval suites** – Movement toward dynamic, open-world testbeds like InfoDeepSeek.
5. **Security, access control, and observability tooling** – Fine-grained permissions, audit trails, and dashboards become must-haves for enterprises.
6. **Domain-specific verticalisation** – Legal, finance, healthcare, and cybersecurity assistants with bespoke knowledge graphs and compliance controls.
7. **Integrated tool use and action-taking** – Beyond retrieval: agents executing API calls, updating records, or triggering workflows safely.
8. **Networked agents and federated retrieval** – Early experiments with agents discovering and collaborating across organisational boundaries.

---

## 6. Build-ready project ideas

Use these blueprints for hackathons, open-source repos, or blog posts. Each idea highlights the agentic behaviours to emphasise.

### 6.1 Core educational builds

- **Dynamic retriever selector** – Classify the query (academic vs. product vs. finance) and route to the best corpus before synthesis. Highlights retrieval orchestration.
- **Self-reflective RAG** – Score groundedness (e.g., with RAGAS) and loop back through retrieval when confidence drops. Demonstrates closed-loop reasoning.
- **Planner–executor demo** – Recreate the "reasoning → retrieval → verification" pattern with an explicit planner agent and a verifier.

### 6.2 Domain-specific assistants

- **Legal research agent** – Pull from IndianKanoon or SCC judgments, summarise precedents, and verify citations—perfect for the Nyaya concept.
- **Financial analyst copilot** – Blend SEC EDGAR filings, earnings call transcripts, and news sentiment to surface risk signals.
- **Clinical literature aide** – Query PubMed, cluster evidence, and return cited, confidence-scored recommendations.
- **Threat-hunting analyst** – Fuse CVE feeds, MITRE ATT&CK mappings, and internal asset data for security teams.

### 6.3 Experimental prototypes

- **Memory-aware RAG** – Cache and reuse prior retrievals to avoid redundant queries in multi-turn sessions.
- **Tool-using agent** – Retrieve API docs, construct requests, execute them, and incorporate results in the final answer.
- **Multi-agent debate** – Have pro/con agents argue over retrieved evidence with an adjudicator deciding the final stance.

### 6.4 Enterprise and infrastructure angles

- **RAG observability dashboard** – Visualise agent graphs, cost per tool, and retrieval quality metrics.
- **Secure sandbox** – Enforce RBAC and policy checks before agents touch sensitive data sources, integrating with OPA or Entra ID.
- **RAGOps toolkit** – Automate regression evals, embedding drift alerts, and prompt versioning in CI/CD.

### 6.5 Creative demos

- **Travel guide agent** – Combine travel blogs, cuisine guides, and historical snippets to produce narrated itineraries.
- **Media companion** – Retrieve trivia, reviews, and production notes for books or films to augment watch parties or book clubs.

---

## 7. Walking through the sample project

The `example_app` directory is a compact sandbox demonstrating the playbook.

### 7.1 Project highlights

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

### 7.2 Setup recap

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
python main.py --model gpt-4.1-mini --top-k 4
```

Run the evaluation harness:

```bash
python evaluate.py --cases evaluation/cases.yaml
```

### 7.3 How the agent works

1. Loads the FAISS store and wraps it in a retriever.
2. Registers tools (currently only `help_center_search`).
3. Instantiates a LangChain OpenAI Functions agent with configurable iterations.
4. Streams the reasoning trace (thought, action, observation) when verbose mode is enabled.
5. Prints the final answer with inline citations.

You can expand the `tools` list with your own integrations (SQL, Slack, Jira) as long as they follow LangChain’s `Tool` signature.

### 7.4 Extending the sandbox

- Add metadata enrichers (tags, access levels) during ingestion and expose them via retriever filters.
- Introduce a “respond with structured JSON” tool for downstream automation.
- Replace FAISS with a hosted vector database when documents exceed millions of chunks.
- Swap the CLI for a FastAPI or Streamlit interface to demo live conversations.

---

## 8. Best practices & guardrails

1. **Data hygiene first** – Deduplicate documents, canonicalise URLs, and strip boilerplate before embedding.
2. **Chunk with intent** – Align chunk boundaries with semantic sections (headings, bullet lists). Overlap 10–20% to preserve context.
3. **Instrument everything** – Capture traces, tool I/O, and token counts. The boring logs unblock debugging.
4. **Favor determinism in prompts** – Explicit instructions and structured outputs reduce variance and improve eval repeatability.
5. **Plan for drift** – Schedule ingest jobs, re-run eval suites nightly, and monitor accuracy metrics for regressions.
6. **Respect compliance** – Implement access controls and audit logs when dealing with sensitive data.

---

## 9. Further reading & tooling

- [LangChain documentation](https://python.langchain.com) – Agents, tools, callbacks, LangGraph.
- [OpenAI API docs](https://platform.openai.com/docs) – Models, pricing, best practices for prompt engineering.
- [Guardrails.ai](https://www.guardrailsai.com/) & [NeMo Guardrails](https://docs.nvidia.com/nemo/guardrails/) – Layer safety policies over agent responses.
- [Evaluation frameworks](https://github.com/openai/evals), [Ragas](https://github.com/explodinggradients/ragas) – Automate RAG quality measurement.
- [Vector DB comparisons](https://www.pinecone.io/learn/vector-database/) – Choose the right store for scale and latency.

Agentic RAG is a journey: instrument early, iterate often, and collaborate closely with the humans who rely on the assistant. This playbook plus the sample project should help you go from idea to a trustworthy, maintainable system.

Happy building! 🚀
