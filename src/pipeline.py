"""The product is one pipeline with named stages. Naming them is what lets us
trace each one and reason about where a query succeeds or fails."""

from __future__ import annotations

STAGES = ["parse", "ground", "rank_and_reason", "present", "measure"]
# ground = call the grounding service; rank_and_reason = LLM over its candidates;
# measure = evals offline + telemetry online.


def run_pipeline(q: str, lat: float, lng: float) -> dict:
    """Run parse → ground → rank and return a structured stage dump.

    Useful for debugging: you can see exactly which stage produced what.
    The HTTP endpoint uses recommend_query (same logic, cleaner response shape).
    """
    from .ground import fetch_grounded
    from .parse import parse_intent
    from .rank_llm import rank

    stages: dict = {"stages": STAGES}

    intent = parse_intent(q)
    stages["parse"] = intent

    candidates = fetch_grounded(lat, lng, intent["radius_m"], intent["category"])
    stages["ground"] = {
        "count": len(candidates),
        "place_ids": [c["place_id"] for c in candidates],
    }

    ranked = rank(intent, candidates) if candidates else []
    stages["rank_and_reason"] = ranked
    stages["failed"] = len(candidates) == 0
    return stages
