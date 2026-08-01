# AI Local Discovery & Recommendation Search Platform

A user asks a real question; the product answers with ranked, reasoned, GROUNDED
recommendations — and measures itself so it gets better.

```
  "where should I take a client for lunch near River North?"
        │
        ▼
   PARSE intent  → point + radius + category + constraints (upscale, quiet)
        │
        ▼
   GROUND  → local-geo-grounding-service → candidates WITH evidence
        │
        ▼
   RANK + REASON  → LLM ranks the grounded candidates, writes a one-line reason
        │            per pick that CITES the evidence (rating, distance, hours)
        ▼
   PRESENT  → React: cards + map + filters + follow-up prompts
        │
        ▼
   MEASURE  → evals (relevance, hallucination, quality) gate changes;
              OTel records clicks, saves, refinements, FAILED queries
```

## The one rule
The LLM may only rank and explain places that came from grounding. It may not
name a place, state a rating, or claim "open now" that isn't in the candidate
evidence. Every recommendation carries a citation back to a grounded source.

## Why this is a trust product
A travel-blog guess that's wrong is annoying; a confident "take them to Alinea,
it's a 5-minute walk" that's actually closed and 3 miles away loses the user for
good. So the architecture optimizes for *trustworthiness*: ground first, force
citations, eval for hallucination, and watch the real signals.

## Layout
- `src/pipeline.py`   — the staged orchestration
- `src/parse.py`      — natural-language question → structured intent
- `src/rank_llm.py`   — LLM ranking + cited reasons over grounded candidates
- `src/recommend.py`  — the recommendation endpoint (ground → rank → respond)
- `web/Results.tsx`   — cards + map + filters + follow-ups
- `src/evals.py`      — relevance / hallucination / quality scoring
- `src/telemetry.py`  — OTel spans + product-signal metrics
