# Instructions for Claude Code

This is the "Maintenance Resolution Intelligence Agent" — an FDE portfolio project.

Before any task, read (in this order):
1. PROGRESS.md — what's actually done vs. not
2. DAILY_PLAN.md — what today's task should be
3. DECISIONS.md — why things were deferred/decided
4. ROADMAP.md — full architecture, phase by phase
5. DESIGN_BRIEF.md — the complete plan if you need full context

Rules:
- Do not introduce any tool/library not already in the locked Phase 1 stack
  (FastAPI, LangGraph, one hosted LLM, PostgreSQL, pgvector, Pytest,
  Braintrust/Langfuse, Docker, Cloud Run) without explicit approval.
- Every new idea/tool must answer: "what specific failure does this solve
  right now?" If none, log it in DECISIONS.md as deferred, don't build it.
- Work in small vertical slices. Inspect existing code before changing it.
- Never claim a test passed without actually running it.
- After finishing a task: update PROGRESS.md, tell me what changed, how to
  run it, and what's next per DAILY_PLAN.md.