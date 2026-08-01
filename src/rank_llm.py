"""The heart of the product: the LLM RANKS the grounded candidates and writes a
one-line reason per pick — and each reason must CITE the evidence (rating,
distance, open_now) we handed it. The candidate list is closed: the LLM may only
return place_ids that are IN it. That single constraint kills hallucination."""

from __future__ import annotations

import json

from .llm import chat

RANK_PROMPT = """You are a local concierge. You are given the USER intent and a
CLOSED list of grounded candidates (each with place_id, name, rating, distance_m,
open_now, price_level). Rank the best matches for the intent. Return STRICT JSON:
{"ranked":[{"place_id":"...","reason":"one line citing rating/distance/hours"}]}.
RULES: only use place_ids from the candidate list. Never invent a place or a
fact. If few fit the constraints, return fewer — do not pad."""


def rank(intent: dict, candidates: list[dict]) -> list[dict]:
    """Ask the LLM to rank; then enforce the closed-list rule in CODE."""
    if not candidates:
        return []

    out = chat(messages=[
        {"role": "system", "content": RANK_PROMPT},
        {"role": "user", "content": json.dumps({"intent": intent, "candidates": candidates})},
    ])
    try:
        payload = json.loads(out.text)
        ranked = payload.get("ranked") or []
        if not isinstance(ranked, list):
            ranked = []
    except json.JSONDecodeError:
        ranked = []

    # Enforce the closed-list rule in CODE, not just the prompt.
    # If the model invents an id, we drop it — trust > clever answers.
    valid_ids = {c["place_id"] for c in candidates}
    clean: list[dict] = []
    for r in ranked:
        if not isinstance(r, dict):
            continue
        pid = r.get("place_id")
        if pid not in valid_ids:
            continue
        reason = (r.get("reason") or "").strip()
        if not reason:
            # Still grounded — fill a minimal cited reason from evidence.
            c = next(x for x in candidates if x["place_id"] == pid)
            reason = f"★{c.get('rating')} · {c.get('distance_m')}m · grounded match"
        clean.append({"place_id": pid, "reason": reason})
    return clean
