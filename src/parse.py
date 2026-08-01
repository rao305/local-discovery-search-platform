"""Turn the user's sentence into a STRUCTURED intent the grounding service can
use: a place reference, a category, a radius, and soft constraints (upscale,
quiet, walkable). We use the LLM here for language understanding only — it
extracts intent, it does NOT pick places. Strict JSON keeps it on rails."""

import json
from .llm import chat

PARSE_PROMPT = """Extract search intent as STRICT JSON:
{"area":"...","category":"...","radius_m":int,"constraints":["upscale","quiet",...]}.
Only extract what the user said; do not invent a neighborhood or cuisine."""


def parse_intent(question: str) -> dict:
    out = chat(messages=[
        {"role": "system", "content": PARSE_PROMPT},
        {"role": "user", "content": question},
    ])
    intent = json.loads(out.text)
    intent.setdefault("radius_m", 1500)        # sane default for "near"
    intent.setdefault("constraints", [])
    return intent
