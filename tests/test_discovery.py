"""The product's promise, as tests: a real query returns ranked recommendations
that are ALL grounded and each carry a cited reason; an impossible query fails
honestly (empty + recorded), never with an invented place. If these hold, the
product is trustworthy."""

from src.recommend import recommend


def test_real_query_returns_grounded_cited_recs():
    res = recommend(q="upscale italian near river north", lat=41.892, lng=-87.634)
    assert res["recommendations"]                      # we got picks
    grounded_ids = set(fetch_ids(41.892, -87.634, "italian"))
    for rec in res["recommendations"]:
        assert rec["place_id"] in grounded_ids         # every pick is grounded
        assert rec["reason"] and rec["rating"]         # every pick is cited with evidence


def test_impossible_query_fails_honestly():
    # Sushi in the middle of the lake: nothing grounds. Must NOT invent a place.
    res = recommend(q="sushi right here", lat=41.900, lng=-87.600)
    assert res["recommendations"] == []
    assert res["grounded"] is True                     # honest empty, not a guess
