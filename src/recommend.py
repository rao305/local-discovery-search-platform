"""The endpoint that produces a recommendation: parse the question, ground it
via the grounding service, rank+reason with the LLM, and respond. The crucial
branch is the FAILED query: when grounding returns nothing, we say so honestly
and record it — a failed query is a product signal, not an error to hide."""

from fastapi import FastAPI
from .parse import parse_intent
from .ground import fetch_grounded   # calls local-geo-grounding-service
from .rank_llm import rank
from .telemetry import record_query

app = FastAPI()


@app.get("/recommend")
def recommend(q: str, lat: float, lng: float):
    intent = parse_intent(q)
    candidates = fetch_grounded(lat, lng, intent["radius_m"], intent["category"])

    if not candidates:
        record_query(q, intent, results=0, failed=True)   # a FAILED query — measured
        return {"recommendations": [], "message": "No grounded places match nearby.", "grounded": True}

    ranked = rank(intent, candidates)
    by_id = {c["place_id"]: c for c in candidates}
    recs = [{"reason": r["reason"], **by_id[r["place_id"]]} for r in ranked]  # rec + its evidence
    record_query(q, intent, results=len(recs), failed=False)
    return {"recommendations": recs, "grounded": True}
