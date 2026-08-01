"""The endpoint that produces a recommendation: parse the question, ground it
via the grounding service, rank+reason with the LLM, and respond. The crucial
branch is the FAILED query: when grounding returns nothing, we say so honestly
and record it — a failed query is a product signal, not an error to hide."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .ground import fetch_grounded
from .parse import parse_intent
from .rank_llm import rank
from .telemetry import record_click, record_query, record_refinement, record_save

app = FastAPI(title="AI Local Discovery")

# Let the Vite React app call us from another port during local dev.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def recommend_query(q: str, lat: float, lng: float) -> dict:
    """Core product function — used by the API, tests, and evals.

    Always returns grounded=True for empty results too: empty means "we looked
    and found nothing real," not "we guessed."
    """
    intent = parse_intent(q)
    candidates = fetch_grounded(lat, lng, intent["radius_m"], intent["category"])

    if not candidates:
        record_query(q, intent, results=0, failed=True)  # a FAILED query — measured
        return {
            "recommendations": [],
            "message": "No grounded places match nearby.",
            "grounded": True,
            "intent": intent,
        }

    ranked = rank(intent, candidates)
    by_id = {c["place_id"]: c for c in candidates}
    # Merge LLM reason + grounded evidence so the UI can show both.
    recs = [{"reason": r["reason"], **by_id[r["place_id"]]} for r in ranked]
    record_query(q, intent, results=len(recs), failed=False)
    return {
        "recommendations": recs,
        "grounded": True,
        "intent": intent,
        "message": None,
    }


def recommend_for_eval(q: str, lat: float, lng: float, version: str = "v1") -> dict:
    """Same path as production, but evals can tag a prompt/version name later."""
    _ = version  # reserved for A/B prompt versions
    return recommend_query(q, lat, lng)


# Back-compat name for anything that still imports `recommend` as a function.
recommend = recommend_query


@app.get("/recommend")
def recommend_endpoint(q: str, lat: float, lng: float):
    """HTTP entry: GET /recommend?q=...&lat=...&lng=..."""
    return recommend_query(q, lat, lng)


@app.post("/events/click")
def event_click(place_id: str):
    record_click(place_id)
    return {"ok": True}


@app.post("/events/save")
def event_save(place_id: str):
    record_save(place_id)
    return {"ok": True}


@app.post("/events/refine")
def event_refine(label: str):
    record_refinement(label)
    return {"ok": True}


@app.get("/health")
def health():
    return {"ok": True}
