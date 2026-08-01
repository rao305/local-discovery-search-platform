# AI Local Discovery & Recommendation Search Platform

## What this is

A small local-search product. You ask a normal question like *"upscale italian near river north"*. The app finds **real nearby places** (grounding), then ranks them and writes a **one-line reason that cites real facts** (rating, distance, open/closed).

It will **not invent** a restaurant, a rating, or “open now.” If nothing real matches, it returns empty and says so.


## What I built

1. **Parse** — turn the question into intent (area, category, radius, constraints)
2. **Ground** — look up real sample places near the coordinates
3. **Rank + reason** — rank only those places and cite their evidence
4. **Present** — React UI with cards, a simple map, filters, and follow-up chips
5. **Measure** — eval suite (hallucination / relevance / quality) + OpenTelemetry-style product signals (queries, fails, clicks, saves, refinements)

## What I learned

- Local discovery is a **trust** product: a confident wrong tip is worse than an honest empty answer.
- The LLM should **rank and explain**, not invent the place list.
- A **closed list** of grounded `place_id`s (checked in code) stops hallucinations.
- **Failed queries** (zero grounded results) are product signals, not bugs to hide.
- Evals + telemetry let you change prompts without flying blind.

## Small architecture

```
question → PARSE → GROUND → RANK+REASON → React UI
                              ↓
                     evals (offline) + telemetry (live)
```

| File | Job |
|------|-----|
| `src/parse.py` | question → structured intent |
| `src/ground.py` | nearby places with evidence (sample Chicago data) |
| `src/rank_llm.py` | rank + cited reasons; drop unknown ids |
| `src/recommend.py` | FastAPI `/recommend` + event routes |
| `src/evals.py` | score hallucination / relevance / quality |
| `src/telemetry.py` | query / click / save / refine signals |
| `web/Results.tsx` | cards + filters + follow-ups |
| `web/Map.tsx` | simple SVG map pins |

More detail: see [ARCHITECTURE.md](ARCHITECTURE.md).


## Measured results

From the built-in eval suite (mock LLM, sample River North places):

| Metric | Target | Result |
|--------|--------|--------|
| hallucination_rate | 0.00 | **0.00** |
| relevance | high | **1.00** |
| quality | high | **1.00** |
| gate vs baseline | pass | **PASS — ship it** |

Re-run anytime with `python -m src.evals`. A prompt change should **not ship** if hallucination goes above 0 or relevance drops below baseline.

## Notes

- Grounding uses **sample places** in River North (no Maps API key needed). Swap `src/ground.py` for a real grounding service later.
- LLM defaults to a **mock** so the project runs offline. Set `OPENAI_API_KEY` (see `.env.example`) for real model calls.
- Postgres / Redis / Maps API are listed in the original stack vision; this finish keeps the learning product runnable without them.
- The one rule: **only recommend place_ids that came from grounding.**

## Stack used here

- Python + FastAPI
- TypeScript + React (Vite)
- OpenTelemetry API/SDK (console-friendly setup)
- OpenAI for parse/rank
