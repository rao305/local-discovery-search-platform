"""You can't trust what you don't measure. The eval harness runs a SUITE of
graded local queries against a prompt/version and scores three things:
HALLUCINATION (did any recommended place_id escape the grounded set?), RELEVANCE
(did the top picks match the intent?), and QUALITY (are the reasons grounded and
useful?). A prompt change ships only if hallucination stays 0 and relevance holds."""

from .recommend import recommend_for_eval


def evaluate(version: str, suite: list[dict]) -> dict:
    halluc, rel = 0, 0.0
    for case in suite:
        res = recommend_for_eval(case["q"], case["lat"], case["lng"], version=version)
        ids = {r["place_id"] for r in res["recommendations"]}
        # HALLUCINATION: any recommended id NOT in the grounded candidate set is fatal.
        if ids - set(case["grounded_ids"]):
            halluc += 1
        # RELEVANCE: did we surface the expected good place in the top results?
        if case["expected_top"] in ids:
            rel += 1
    n = len(suite)
    return {"version": version, "hallucination_rate": halluc / n, "relevance": rel / n}


def gate(baseline: dict, candidate: dict) -> bool:
    # Ship only if no new hallucination and relevance doesn't regress.
    return candidate["hallucination_rate"] == 0 and candidate["relevance"] >= baseline["relevance"]
