"""The product is one pipeline with named stages. Naming them is what lets us
trace each one and reason about where a query succeeds or fails."""

STAGES = ["parse", "ground", "rank_and_reason", "present", "measure"]
# ground = call the grounding service; rank_and_reason = LLM over its candidates;
# measure = evals offline + telemetry online.
