# Agentic RAG Notebook Curriculum

This directory hosts a hands-on curriculum that complements the written guide in
`docs/` and the runnable reference implementation in `example_app/`. Each
notebook focuses on a specific retrieval-augmented architecture pattern and can
be executed independently or sequentially as a progressive workshop.

## Notebook roadmap

| # | Notebook | Focus | Key Takeaways |
| - | -------- | ----- | ------------- |
| 1 | `1_classic_rag.ipynb` | Baseline retrieval-augmented QA | Build intuition for vector search, prompt templating, and evaluation checkpoints. |
| 2 | `2_self_improving_microloop.ipynb` | Self-improving feedback loop | Watch a retrieval pipeline critique itself, capture missing facts, and upgrade the next attempt without external APIs. |
| 3 | `3_planner_executor_rag.ipynb` | Planner → executor decomposition | Learn how a high-level planner can break multi-hop questions into focused retrieval subtasks. |
| 4 | `4_self_reflective_rag.ipynb` | Self-reflection and retry loops | Implement automatic answer critique with confidence-triggered re-querying. |
| 5 | `5_multi_agent_rag.ipynb` | Specialist agent orchestration | Route queries to the most relevant retrievers before synthesising a final answer. |
| 6 | `6_verified_rag.ipynb` | Fact verification | Attach a verification pass that grounds claims with supporting evidence. |
| 7 | `7_adaptive_rag.ipynb` | Policy-driven routing | Optimise cost/latency by activating only the agents and tools required for a query. |
| 8 | `8_comparative_evaluation.ipynb` | Holistic evaluation | Compare the above pipelines using common metrics, latency measurements, and qualitative review. |

## Learning goals & prerequisites

| Audience | Suggested prep | Why it helps |
| --- | --- | --- |
| New to RAG | Read the TL;DR section of the playbook and watch a LangChain ReAct tutorial. | Provides vocabulary for agent traces and tool calls. |
| Intermediate practitioners | Skim the planner/executor and reflection chapters in the playbook; run the CLI demo once. | Ensures your environment is configured and highlights how the notebooks align with the app. |
| Facilitators running workshops | Print the [learning pathways](../docs/learning_pathways.md) table and clone this repo ahead of time. | Helps participants self-select a journey and keeps sessions on schedule. |

Bring your own OpenAI API key (`gpt-4.1-mini` is the default) and verify that `python --version` ≥ 3.10 before installing dependencies.

## Shared utilities

The helper functions that the notebooks use live in `shared.py`. They mostly
wrap pieces from `example_app/` so the experiments stay aligned with the
reference agent. Feel free to extend them with additional retrievers, tools, or
metrics as you iterate on the notebooks.

### Offline mini corpus

Notebook 2 introduces a lightweight feedback loop that runs entirely offline.
The demo relies on `data/mini_corpus.jsonl` plus an automatically populated
`memory_notes.jsonl` file (ignored by Git) so you can observe how memories are
persisted between attempts. Delete the memory file whenever you want to reset
the exercise.

## Facilitation tips

* 🧭 **Start with learning outcomes.** Ask participants to note what they want to prove (e.g., “planner reduces hallucinations”). Revisit those goals when wrapping up each notebook.
* 🧪 **Capture evidence as you go.** Export plots, metrics, and traces; they feed directly into the Learning Evidence Checklist in [`docs/learning_pathways.md`](../docs/learning_pathways.md).
* 🧰 **Encourage experimentation.** Suggest optional challenges: swap retrievers, add cost logging, or integrate a new tool. Record findings in the final summary cells.
* 💬 **Debrief in public.** Open a GitHub discussion or issue summarising takeaways so future learners benefit from your insights.

## Getting started

1. Install dependencies:

   ```bash
   uv venv  # or python -m venv .venv
   source .venv/bin/activate
   pip install -r notebooks/requirements.txt
   ```

2. Build the sample FAISS store once:

   ```bash
   cd example_app
   python ingest.py
   cd -
   ```

3. Launch Jupyter Lab or VS Code and open the notebooks:

   ```bash
   jupyter lab notebooks/
   ```

4. Provide the same environment variables required by the example app:

   ```bash
   export OPENAI_API_KEY=sk-...
   ```

## Contributing

If you design a new pipeline, add another notebook that mirrors the structure of
this curriculum and update the table above. Pull requests that improve
visualisations, metrics, or interoperability with other model providers are also
welcome.
