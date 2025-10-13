# Learning Pathways for Agentic RAG Builders

New visitors to the repository often ask the same three questions:

1. *Where should I start if I only have an afternoon?*
2. *How do I progress from “hello world” to a production-ready assistant?*
3. *What evidence should I capture to convince teammates or leadership that the system works?*

This guide answers those questions by curating the repository’s assets into targeted learning journeys. Use it as a companion to the [Agentic RAG Playbook](agentic_rag_beginner_guide.md), the [notebook curriculum](../notebooks/README.md), and the [example application](../example_app/README.md).

---

## Personas and goals

| Persona | Primary goal | Recommended outcomes |
| --- | --- | --- |
| **Explorer** (2–3 hours) | Understand the vocabulary and see a working demo. | Be able to explain agentic RAG vs. classic RAG, run the sample CLI, and document key observations. |
| **Builder** (1–2 days) | Prototype a domain-specific workflow and measure quality. | Adapt the ingestion pipeline, instrument evaluation metrics, and capture a before/after comparison. |
| **Operator** (multi-week) | Prepare for deployment, governance, and ongoing maintenance. | Design guardrails, observability dashboards, and an operations runbook tailored to your environment. |

Each persona builds on the previous one. Completing Explorer tasks gives you the vocabulary to attempt the Builder track, while Builder outputs (metrics, lessons) become inputs for the Operator checklist.

---

## Explorer track

| Step | Activity | Repository asset | Deliverable |
| --- | --- | --- | --- |
| 1 | Skim the TL;DR, trends, and architecture sections. | [Agentic RAG Playbook](agentic_rag_beginner_guide.md) | One-page summary in your own words. |
| 2 | Run the CLI demo with the bundled dataset. | [Example app](../example_app/README.md) | Screenshot or transcript of two successful queries. |
| 3 | Execute the *Classic RAG* notebook (optionally follow with the offline micro-loop). | [`1_classic_rag.ipynb`](../notebooks/1_classic_rag.ipynb), [`2_self_improving_microloop.ipynb`](../notebooks/2_self_improving_microloop.ipynb) | Notebook cells completed with commentary on what surprised you and how the memory loop behaved. |
| 4 | Log questions or blockers. | GitHub Discussions / Issues | Checklist of open questions to revisit in the Builder track. |

**Time investment:** ~2–3 hours.

**What users appreciate:** Quick wins, minimal setup friction, and clarity on how the assets relate. Pair this track with a live walkthrough or lunch-and-learn recording for your team.

---

## Builder track

| Step | Activity | Repository asset | Deliverable |
| --- | --- | --- | --- |
| 1 | Swap the sample documents for your domain content and rebuild the vector store. | [`ingest.py`](../example_app/ingest.py) | Notes on preprocessing choices (chunk size, metadata). |
| 2 | Add at least one specialised tool or retriever. | [`example_app/agent.py`](../example_app/agent.py) | Pull request or diff showing the new tool registration. |
| 3 | Run the *Planner–Executor* and *Self-Reflective* notebooks to test orchestration variants. | [`3_planner_executor_rag.ipynb`](../notebooks/3_planner_executor_rag.ipynb), [`4_self_reflective_rag.ipynb`](../notebooks/4_self_reflective_rag.ipynb) | Comparison table capturing quality, latency, and token cost deltas. |
| 4 | Configure automated evaluation. | [`evaluate.py`](../example_app/evaluate.py) and [`8_comparative_evaluation.ipynb`](../notebooks/8_comparative_evaluation.ipynb) | Saved metrics (JSON/CSV) plus qualitative notes on failure cases. |
| 5 | Share findings with stakeholders. | README template in your own repo | Short Loom/video or doc describing the prototype results. |

**Time investment:** ~1–2 focused days.

**What users appreciate:** Opinionated defaults, copy-paste code snippets, and explicit prompts for collecting evidence. Encourage learners to fork the repo so they can document their experiments without disturbing the main branch.

---

## Operator track

| Step | Activity | Repository asset | Deliverable |
| --- | --- | --- | --- |
| 1 | Review the governance, guardrails, and deployment guidance. | [Agentic RAG Playbook – Sections 3 & 4](agentic_rag_beginner_guide.md) | Draft operations runbook with ownership assignments. |
| 2 | Instrument tracing and observability. | `example_app/` logging hooks, `notebooks/shared.py` helpers | Tracing screenshots or logs showing agent reasoning paths. |
| 3 | Design evaluation gates for CI/CD. | [`evaluation/`](../example_app/evaluation) harness, [`8_comparative_evaluation.ipynb`](../notebooks/8_comparative_evaluation.ipynb) | Checklist describing pre-release checks and pass/fail thresholds. |
| 4 | Define rollback and fallback strategies. | Playbook + your infra docs | Document describing safe fallbacks (FAQ search, human handoff). |
| 5 | Teach the rest of the team. | This repo + your materials | Internal workshop deck or recorded walkthrough. |

**Time investment:** Varies by org; expect 2–3 weeks to establish observability and governance in production settings.

**What users appreciate:** Guidance on non-happy paths—cost overruns, traceability, incident response—and examples of artifacts (dashboards, SOPs, retrospectives) that prove readiness.

---

## Learning evidence checklist

Use this checklist to track progress regardless of persona. If you can tick each box, you have a credible story for peers, managers, or Medium readers.

- [ ] **Context brief** – A short doc describing the user problem, target metrics, and assumptions.
- [ ] **Architecture sketch** – Screenshot or diagram of your agent graph and data flow.
- [ ] **Dataset audit** – Table listing data sources, freshness, and access controls.
- [ ] **Evaluation baseline** – Metrics from the classic RAG pipeline.
- [ ] **Agentic delta** – Measurements showing how planner/reflection/multi-agent variants perform relative to baseline.
- [ ] **Cost log** – Token usage and API spend for each experiment.
- [ ] **Observability trace** – Logs or traces that illustrate tool call sequences and decision points.
- [ ] **Lessons learned** – Top 3 insights or gotchas you discovered.

Encourage contributors to attach these artifacts when opening issues or pull requests; it accelerates reviews and helps future learners understand the rationale behind changes.

---

## Frequently requested enhancements

Based on discussions with builders, here are common requests and where to find them:

| Request | Where it lives | Status |
| --- | --- | --- |
| “Can I see a fully guided study plan?” | This document. | ✅ Delivered. |
| “How do I troubleshoot low recall or hallucinations?” | [Playbook §3.3 and §3.4](agentic_rag_beginner_guide.md) | ✅ Includes debugging steps. |
| “Are there examples of evaluation dashboards?” | [`8_comparative_evaluation.ipynb`](../notebooks/8_comparative_evaluation.ipynb) | ✅ Notebook generates plots and summary tables. |
| “What about enterprise governance?” | Playbook §4 + Operator track above | ✅ Contains guardrail checklists. |
| “Can we contribute additional datasets?” | `example_app/data/` + CONTRIBUTING section in [root README](../README.md) | 🔄 Always open for pull requests. |

If you spot a gap or have a template to share, open an issue so we can incorporate it into the next iteration of the learning experience.

---

## Next steps

1. Choose the track that matches your current goal and block time on your calendar.
2. Capture artifacts as you progress—screenshots, metrics, notes—and store them in your fork or team workspace.
3. Share feedback! The more we learn about what helped (or slowed) you down, the better the learning hub becomes.

Happy building 👩‍💻👨‍💻

