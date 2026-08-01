"""You can't trust what you don't measure. The eval harness runs a SUITE of
graded local queries against a prompt/version and scores three things:
HALLUCINATION (did any recommended place_id escape the grounded set?), RELEVANCE
(did the top picks match the intent?), and QUALITY (are the reasons grounded and
useful?). A prompt change ships only if hallucination stays 0 and relevance holds."""

from __future__ import annotations

from .ground import fetch_ids
from .recommend import recommend_for_eval

# Tiny graded suite — River North sample data. Each case knows which grounded
# ids are "legal" and which place we'd hope to see for relevance.
DEFAULT_SUITE: list[dict] = [
    {
        "name": "upscale italian",
        "q": "upscale italian near river north",
        "lat": 41.892,
        "lng": -87.634,
        "grounded_ids": None,  # filled at runtime from fetch_ids
        "expected_top": "p_gibsons",  # high price + italian in sample set
        "category": "italian",
    },
    {
        "name": "walkable italian",
        "q": "walkable italian near river north",
        "lat": 41.892,
        "lng": -87.634,
        "grounded_ids": None,
        "expected_top": "p_rpm",
        "category": "italian",
    },
    {
        "name": "impossible sushi on the lake",
        "q": "sushi right here",
        "lat": 41.900,
        "lng": -87.600,  # Lake Michigan — nothing should ground
        "grounded_ids": [],
        "expected_top": None,  # empty is correct
        "category": "sushi",
    },
]


def _prepare_suite(suite: list[dict]) -> list[dict]:
    """Fill grounded_ids from the real grounding function when not hardcoded."""
    prepared = []
    for case in suite:
        c = dict(case)
        if c.get("grounded_ids") is None:
            c["grounded_ids"] = fetch_ids(c["lat"], c["lng"], c.get("category", "restaurant"))
        prepared.append(c)
    return prepared


def evaluate(version: str, suite: list[dict] | None = None) -> dict:
    suite = _prepare_suite(suite or DEFAULT_SUITE)
    halluc, rel, quality = 0, 0.0, 0.0
    details = []

    for case in suite:
        res = recommend_for_eval(case["q"], case["lat"], case["lng"], version=version)
        ids = {r["place_id"] for r in res["recommendations"]}
        grounded = set(case["grounded_ids"] or [])

        # HALLUCINATION: any recommended id NOT in the grounded candidate set is fatal.
        case_halluc = bool(ids - grounded)
        if case_halluc:
            halluc += 1

        # RELEVANCE: did we surface the expected good place (or correctly stay empty)?
        expected = case.get("expected_top")
        if expected is None:
            case_rel = len(ids) == 0
        else:
            case_rel = expected in ids
        if case_rel:
            rel += 1

        # QUALITY: every rec has a non-empty reason that mentions a grounded fact cue.
        reasons_ok = True
        for r in res["recommendations"]:
            reason = (r.get("reason") or "").lower()
            if not reason:
                reasons_ok = False
                break
            # Soft check: reason should cite something from evidence.
            if str(r.get("rating", "")) not in reason and "★" not in reason and "m" not in reason:
                reasons_ok = False
                break
        if reasons_ok:
            quality += 1

        details.append({
            "name": case.get("name", case["q"]),
            "hallucination": case_halluc,
            "relevant": case_rel,
            "quality_ok": reasons_ok,
            "n_recs": len(ids),
        })

    n = max(len(suite), 1)
    return {
        "version": version,
        "hallucination_rate": halluc / n,
        "relevance": rel / n,
        "quality": quality / n,
        "n": n,
        "details": details,
    }


def gate(baseline: dict, candidate: dict) -> bool:
    # Ship only if no new hallucination and relevance doesn't regress.
    return candidate["hallucination_rate"] == 0 and candidate["relevance"] >= baseline["relevance"]


def main() -> None:
    """Run: python -m src.evals  → prints measured results for the README."""
    baseline = evaluate("baseline")
    candidate = evaluate("candidate")  # same mock path today; gate should pass
    ok = gate(baseline, candidate)

    print("=== Local Discovery — measured results ===")
    print(f"version:              {candidate['version']}")
    print(f"suite size:           {candidate['n']}")
    print(f"hallucination_rate:   {candidate['hallucination_rate']:.2f}  (want 0.00)")
    print(f"relevance:            {candidate['relevance']:.2f}")
    print(f"quality:              {candidate['quality']:.2f}")
    print(f"gate vs baseline:     {'PASS — ship it' if ok else 'FAIL — do not ship'}")
    print("--- per case ---")
    for d in candidate["details"]:
        print(
            f"  {d['name']}: halluc={d['hallucination']} "
            f"relevant={d['relevant']} quality={d['quality_ok']} n={d['n_recs']}"
        )


if __name__ == "__main__":
    main()
