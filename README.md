# Agentic RAG: A Beginner-Friendly Tutorial

Welcome! This repository is a guided workshop for anyone who wants to understand **Retrieval-Augmented Generation (RAG)** and then take the next step into **agentic RAG** systems. Everything here is written with curious engineers, students, and self-taught builders in mind. If you can run Python notebooks, you can work through this repo and build your own agentic RAG prototype.

## What you'll learn

* The building blocks of classic RAG (retrieval + answer synthesis).
* Why teams are adding agentic behaviours like planning, reflection, and tool use.
* How to progress from a minimal baseline to more capable agentic workflows.
* Practical tips for running, evaluating, and extending your own projects.

## How to use this repo

1. **Start with the traditional RAG notebook** – `notebooks/0_traditional_rag_tutorial.ipynb` walks through the retrieval pipeline step by step using pure Python and NumPy so you can see every moving part.
2. **Skim the written guide** – `docs/agentic_rag_beginner_guide.md` explains the ideas behind agentic RAG and points to concrete design patterns.
3. **Run the agentic notebooks** – The numbered notebooks build on the baseline with self-improvement loops, planners, reflection, multi-agent coordination, verification, and evaluation tooling.
4. **Experiment with the example app** – `example_app/` contains a small command-line project that ties the concepts together with ingestion, retrieval, and agent orchestration code you can adapt.

Take notes as you go, pause to tweak prompts or datasets, and re-run cells until the flow makes sense. This is meant to feel like a guided lab, not a lecture.

## Traditional vs. agentic RAG at a glance

| Classic RAG | Agentic RAG |
| --- | --- |
| Single-shot retrieval + response. | Multi-step reasoning with planners, critics, or tool calls. |
| Relies on static prompts. | Dynamically adjusts prompts, data sources, or strategies. |
| Useful for FAQ-style tasks. | Handles open-ended tasks that need judgement or iteration. |
| Notebook: `0_traditional_rag_tutorial.ipynb` | Notebooks: `1_` through `8_` for progressive agentic patterns |

Use the new baseline notebook to anchor your understanding before diving into the advanced flows—the differences will stand out more clearly once you have walked through the simpler path.

## Repository tour

```
docs/
  agentic_rag_beginner_guide.md   # Conceptual walkthroughs and checklists
docs/learning_pathways.md         # Suggested study routes for different roles
example_app/                      # Runnable CLI example with ingestion + chat agent
notebooks/
  0_traditional_rag_tutorial.ipynb  # Build a classic RAG pipeline from scratch
  1_* through 8_*                   # Agentic enhancements with planners, loops, and evaluation
  README.md                         # Notebook setup notes and quick links
  requirements.txt                  # Extra packages for the advanced notebooks
```

## Getting started

```bash
# Install base requirements (create a virtual environment if you prefer)
pip install -r notebooks/requirements.txt

# Export your OpenAI key before running the agentic notebooks or example app
export OPENAI_API_KEY="sk-..."

# Launch JupyterLab to explore the curriculum
jupyter lab notebooks
```

The traditional RAG notebook relies only on NumPy and the Python standard library, so you can open it first even if you have not installed every optional package yet.

## Where to go next

* Extend the example app with your own documents or tools.
* Try the evaluation notebook to measure retrieval quality on your data.
* Share feedback or improvements by opening an issue or pull request.

Happy building, and enjoy the journey from simple retrieval to full agentic systems!
