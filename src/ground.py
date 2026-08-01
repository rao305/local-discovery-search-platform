"""Grounding = "only recommend places that exist in real data."

In a full product this would call a Maps API / local-geo-grounding-service.
Here we keep a small Chicago River North sample set so the project runs offline.
Every recommendation later MUST come from these candidates (or a filter of them).
"""

from __future__ import annotations

import math

# Sample places near River North, Chicago. Distances are recomputed per query.
# Categories are lowercase so intent matching stays simple.
_PLACES: list[dict] = [
    {
        "place_id": "p_rpm",
        "name": "RPM Italian",
        "lat": 41.8925,
        "lng": -87.6328,
        "rating": 4.5,
        "open_now": True,
        "price_level": 3,
        "category": "italian",
    },
    {
        "place_id": "p_quartino",
        "name": "Quartino Ristorante",
        "lat": 41.8934,
        "lng": -87.6289,
        "rating": 4.4,
        "open_now": True,
        "price_level": 2,
        "category": "italian",
    },
    {
        "place_id": "p_gibsons",
        "name": "Gibsons Italia",
        "lat": 41.8879,
        "lng": -87.6275,
        "rating": 4.6,
        "open_now": True,
        "price_level": 4,
        "category": "italian",
    },
    {
        "place_id": "p_eataly",
        "name": "Eataly Chicago",
        "lat": 41.8917,
        "lng": -87.6250,
        "rating": 4.3,
        "open_now": True,
        "price_level": 2,
        "category": "italian",
    },
    {
        "place_id": "p_sushi",
        "name": "Sushi-san",
        "lat": 41.8908,
        "lng": -87.6312,
        "rating": 4.4,
        "open_now": True,
        "price_level": 3,
        "category": "sushi",
    },
    {
        "place_id": "p_nobu",
        "name": "Nobu Chicago",
        "lat": 41.8939,
        "lng": -87.6255,
        "rating": 4.5,
        "open_now": False,
        "price_level": 4,
        "category": "sushi",
    },
    {
        "place_id": "p_cafe",
        "name": "Sawada Coffee",
        "lat": 41.8865,
        "lng": -87.6480,
        "rating": 4.7,
        "open_now": True,
        "price_level": 2,
        "category": "cafe",
    },
    {
        "place_id": "p_bar",
        "name": "The Violet Hour",
        "lat": 41.9090,
        "lng": -87.6770,
        "rating": 4.6,
        "open_now": True,
        "price_level": 3,
        "category": "bar",
    },
    {
        "place_id": "p_mexican",
        "name": "Broken English Taco Pub",
        "lat": 41.8910,
        "lng": -87.6305,
        "rating": 4.2,
        "open_now": True,
        "price_level": 2,
        "category": "mexican",
    },
    {
        "place_id": "p_pizza",
        "name": "Pizano's Pizza",
        "lat": 41.8920,
        "lng": -87.6278,
        "rating": 4.1,
        "open_now": True,
        "price_level": 2,
        "category": "pizza",
    },
]


def _haversine_m(lat1: float, lng1: float, lat2: float, lng2: float) -> int:
    """Distance in meters between two lat/lng points (Earth as a sphere)."""
    r = 6371000.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlmb = math.radians(lng2 - lng1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlmb / 2) ** 2
    return int(2 * r * math.asin(math.sqrt(a)))


def fetch_grounded(lat: float, lng: float, radius_m: int, category: str) -> list[dict]:
    """Return nearby places that match the category, each with evidence fields.

    If nothing is in range / category, return [] — that is a FAILED query later,
    not a cue to invent restaurants.
    """
    cat = (category or "").lower().strip()
    out: list[dict] = []
    for place in _PLACES:
        dist = _haversine_m(lat, lng, place["lat"], place["lng"])
        if dist > radius_m:
            continue
        # "restaurant" is a loose bucket — include food categories.
        place_cat = place["category"]
        if cat and cat not in ("restaurant", "food", "nearby"):
            if place_cat != cat and cat not in place_cat:
                continue
        candidate = {
            **place,
            "distance_m": dist,  # evidence the ranker may cite
        }
        out.append(candidate)
    # Closest first before the LLM re-ranks.
    out.sort(key=lambda c: c["distance_m"])
    return out


def fetch_ids(lat: float, lng: float, category: str, radius_m: int = 2000) -> list[str]:
    """Helper for tests: which place_ids would grounding return for this query?"""
    return [c["place_id"] for c in fetch_grounded(lat, lng, radius_m, category)]
