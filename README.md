# AI Local Discovery & Recommendation Search Platform

The capstone. Assemble a real AI local-search product on top of the grounding service you built: a user asks a natural-language question, the backend retrieves grounded nearby places (with their evidence), and an LLM produces a RANKED set of recommendations each with a one-line reason that cites the grounded facts — never inventing a place, a rating, or an hour. The React UI shows interactive cards, a map, filters, and follow-up prompts ("more upscale", "walkable"). You build the discipline that makes it trustworthy: an evaluation harness that scores relevance, hallucination risk, and answer quality on a suite of graded queries and gates every prompt change; and OpenTelemetry that traces each query end-to-end and records the product signals — clicks, saves, refinements, and FAILED queries (zero grounded results) — so you can see and improve where the experience breaks down. You reason about local discovery as a trust product: a confident wrong recommendation costs more than a hedged right one, so grounding, citations, and evals are the architecture, not the afterthought. This is AI product engineering, grounded retrieval, LLM ranking, evaluation, and observability in one system.

Built step-by-step with [KhwajaLabs Build](https://khwajalabs.com).

## Stack
- Python
- FastAPI
- TypeScript
- React
- PostgreSQL
- Redis
- Maps API
- LLM API
- OpenTelemetry
