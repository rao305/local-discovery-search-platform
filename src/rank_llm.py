"""The heart of the product: the LLM RANKS the grounded candidates and writes a
one-line reason per pick — and each reason must CITE the evidence (rating,
distance, open_now) we handed it. The candidate list is closed: the LLM may only
return place_ids that are IN it. That single constraint kills hallucination."""

import json
from .llm import chat

RANK_PROMPT = """You are a local concierge. You are given the USER intent and a
CLOSED list of grounded candidates (each with place_id, name, rating, distance_m,
open_now, price_level). Rank the best matches for the intent. Return STRICT JSON:
{"ranked":[{"place_id":"...","reason":"one line citing rating/distance/hours"}]}.
RULES: only use place_ids from the candidate list. Never invent a place or a
fact. If few fit the constraints, return fewer — do not pad."""


def rank(intent: dict, candidates: list[dict]) -> list[dict]:
    out = chat(messages=[
        {"role": "system", "content": RANK_PROMPT},
        {"role": "user", "content": json.dumps({"intent": intent, "candidates": candidates})},
    ])
    ranked = json.loads(out.text)["ranked"]
    # Enforce the closed-list rule in CODE, not just the prompt.
    valid_ids = {c["place_id"] for c in candidates}
    return [r for r in ranked if r["place_id"] in valid_ids]
