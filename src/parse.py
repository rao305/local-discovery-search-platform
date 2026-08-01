"""Turn the user's sentence into a STRUCTURED intent the grounding service can
use: a place reference, a category, a radius, and soft constraints (upscale,
quiet, walkable). We use the LLM here for language understanding only — it
extracts intent, it does NOT pick places. Strict JSON keeps it on rails."""

from __future__ import annotations

import json

from .llm import chat

PARSE_PROMPT = """Extract search intent as STRICT JSON:
{"area":"...","category":"...","radius_m":int,"constraints":["upscale","quiet",...]}.
Only extract what the user said; do not invent a neighborhood or cuisine."""


def parse_intent(question: str) -> dict:
    """Parse natural language → intent dict. Falls back safely if JSON is messy."""
    out = chat(messages=[
        {"role": "system", "content": PARSE_PROMPT},
        {"role": "user", "content": question},
    ])
    try:
        intent = json.loads(out.text)
        if not isinstance(intent, dict):
            raise ValueError("intent must be an object")
    except (json.JSONDecodeError, ValueError):
        # Never crash the product on a bad model reply — use sane defaults.
        intent = {
            "area": "nearby",
            "category": "restaurant",
            "radius_m": 1500,
            "constraints": [],
        }

    intent.setdefault("area", "nearby")
    intent.setdefault("category", "restaurant")
    intent.setdefault("radius_m", 1500)  # sane default for "near"
    intent.setdefault("constraints", [])
    # Keep radius in a beginner-friendly band.
    try:
        intent["radius_m"] = int(intent["radius_m"])
    except (TypeError, ValueError):
        intent["radius_m"] = 1500
    if not isinstance(intent["constraints"], list):
        intent["constraints"] = []
    return intent
