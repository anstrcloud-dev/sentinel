# SENTINEL — Multi-Agent AI Emergency Dispatch

A multi-agent AI system that triages emergency incident reports, routes them to
specialist agents, grounds their recommendations in real protocols via RAG, and
requires human approval before dispatch.

> **Note:** This is a portfolio project demonstrating AI system architecture. It
> is a decision-support prototype, not a production emergency system.

## What it does

Given a free-text incident report (e.g. *"Car crashed into a building, people
trapped, fuel leaking"*), SENTINEL:

1. **Classifies** the incident (type, severity, confidence) using an LLM
2. **Routes** it deterministically to the relevant specialist(s)
3. **Analyzes** it with domain specialist agents (fire / medical / police),
   each grounded in retrieved standard operating procedures (RAG)
4. **Consolidates** their reports into a dispatch recommendation
5. **Pauses for human approval** — nothing is dispatched without a dispatcher's
   sign-off

## Architecture

```
START -> intake -> classifier -> [router]
                                    |-> fire ----+
                                    |-> medical -+-> consolidate -> human_approval -> outcome -> END
                                    |-> police --+
```

Key design decisions:

- **Deterministic routing, not LLM-controlled.** The classifier (an LLM) decides
  *what* the incident is; plain Python decides *where it goes*. Control flow in a
  high-stakes system should be predictable and testable, not probabilistic.
- **Human-in-the-loop as a structural requirement.** The graph physically pauses
  at an approval gate (via LangGraph `interrupt`) and cannot proceed to dispatch
  without a human decision.
- **Parallel specialist agents with a state reducer.** `multi`-domain incidents
  fan out to all three specialists concurrently; a reducer merges their reports
  without write collisions.
- **Model cascading.** A fast model handles the common case; the classifier
  escalates to a stronger model only when confidence is low — balancing cost,
  latency, and accuracy.
- **RAG grounding.** Specialists retrieve relevant SOPs from a pgvector store
  (semantic search over embeddings) so recommendations follow documented
  procedure rather than improvising.
- **Fault isolation.** Each agent's LLM call is wrapped so a single failure
  degrades to a flagged fallback report instead of crashing the dispatch.

## Tech stack

LangGraph · Python · Groq · pgvector (PostgreSQL) · sentence-transformers

## Project layout

```
src/
  config.py       # models, DB settings, constants
  state.py        # the IncidentState schema
  rag.py          # embedding model + SOP retrieval
  classifier.py   # cascading classifier
  specialists.py  # fire / medical / police agents
  nodes.py        # intake, consolidate, human approval, outcome
  graph.py        # graph construction + routing
scripts/
  build_kb.py     # builds the pgvector SOP knowledge base
main.py           # runs one incident end-to-end
```

## Setup

**1. Start the pgvector database (Docker):**

```bash
docker run --name sentinel-pg -e POSTGRES_PASSWORD=sentinel -e POSTGRES_DB=sentinel -p 5432:5432 -d pgvector/pgvector:pg17
```

**2. Install dependencies:**

```bash
python -m venv venv
# Windows: .\venv\Scripts\Activate.ps1   |   macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
```

**3. Add your Groq API key:**

Copy `.env.example` to `.env` and add your key from
[console.groq.com](https://console.groq.com):

```
GROQ_API_KEY=your_key_here
```

**4. Build the knowledge base (once):**

```bash
python scripts/build_kb.py
```

**5. Run it:**

```bash
python main.py
```

## Possible extensions

- Coordination layer so specialists don't overlap on cross-domain incidents
- Observability (tracing + per-step cost/latency)
- Evaluation harness (labeled test set, classification/routing accuracy)
