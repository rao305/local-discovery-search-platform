"""Tiny LLM wrapper. Beginners can run the whole product WITHOUT an API key —
we fake chat with a rule-based mock. If OPENAI_API_KEY is set, we call OpenAI
for real parse/rank JSON. Either way, callers just use chat(...).text."""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass


@dataclass
class ChatResult:
    """Same shape whether mock or real — only .text matters to the rest of the app."""
    text: str


def chat(messages: list[dict]) -> ChatResult:
    """Send a chat. Prefer OpenAI when a key exists; otherwise mock."""
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if api_key:
        return _chat_openai(messages, api_key)
    return _chat_mock(messages)


def _chat_openai(messages: list[dict], api_key: str) -> ChatResult:
    # Optional path — only used when the user pasted a real key.
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError(
            "OPENAI_API_KEY is set but the openai package is missing. "
            "Run: pip install openai"
        ) from exc

    client = OpenAI(api_key=api_key)
    resp = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        messages=messages,
        temperature=0,
    )
    return ChatResult(text=resp.choices[0].message.content or "{}")


def _chat_mock(messages: list[dict]) -> ChatResult:
    """Rule-based stand-in so demos and tests work offline.

    We look at the system prompt to decide: parse intent, or rank candidates.
    """
    system = (messages[0].get("content") or "") if messages else ""
    user = (messages[-1].get("content") or "") if messages else ""

    if "Extract search intent" in system:
        return ChatResult(text=json.dumps(_mock_parse(user)))
    if "local concierge" in system or "CLOSED list" in system:
        return ChatResult(text=json.dumps(_mock_rank(user)))

    # Unknown prompt — return empty JSON so callers don't crash.
    return ChatResult(text="{}")


def _mock_parse(question: str) -> dict:
    """Pull area / category / constraints out of the sentence with keywords."""
    q = question.lower()

    # Category: first match wins (simple, readable).
    category = "restaurant"
    for word in ("italian", "sushi", "mexican", "cafe", "coffee", "bar", "pizza"):
        if word in q:
            category = word
            break

    area = "river north" if "river north" in q else "nearby"

    constraints: list[str] = []
    for word in ("upscale", "quiet", "walkable", "cheap", "open now"):
        if word in q:
            constraints.append(word)

    # Slightly wider radius when they say "near"; tighter for "walkable".
    radius_m = 800 if "walkable" in constraints else 1500

    return {
        "area": area,
        "category": category,
        "radius_m": radius_m,
        "constraints": constraints,
    }


def _mock_rank(user_json: str) -> dict:
    """Rank grounded candidates with one-line reasons that cite evidence.

    Never invents a place_id — only uses what grounding handed us.
    """
    try:
        payload = json.loads(user_json)
    except json.JSONDecodeError:
        return {"ranked": []}

    intent = payload.get("intent") or {}
    candidates = list(payload.get("candidates") or [])
    constraints = [c.lower() for c in intent.get("constraints") or []]

    def score(c: dict) -> float:
        # Higher is better. Purely from grounded fields.
        s = float(c.get("rating") or 0) * 10
        dist = float(c.get("distance_m") or 9999)
        s -= dist / 200.0  # closer = better
        if "upscale" in constraints and int(c.get("price_level") or 0) >= 3:
            s += 5
        if "cheap" in constraints and int(c.get("price_level") or 0) <= 2:
            s += 5
        if "walkable" in constraints and dist <= 800:
            s += 4
        if "open now" in constraints and c.get("open_now"):
            s += 3
        if "quiet" in constraints and int(c.get("price_level") or 0) >= 2:
            s += 1
        return s

    ranked_candidates = sorted(candidates, key=score, reverse=True)[:5]
    ranked = []
    for c in ranked_candidates:
        open_txt = "open now" if c.get("open_now") else "currently closed"
        reason = (
            f"{c.get('name')} — ★{c.get('rating')} · "
            f"{c.get('distance_m')}m away · {open_txt} "
            f"(price level {c.get('price_level')})."
        )
        # Strip any weird control chars just in case.
        reason = re.sub(r"\s+", " ", reason).strip()
        ranked.append({"place_id": c["place_id"], "reason": reason})

    return {"ranked": ranked}
