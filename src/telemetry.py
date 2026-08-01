"""Evals measure quality offline; telemetry measures the LIVE product. Each
query gets an OpenTelemetry span (trace parse→ground→rank end to end) and we
record the product signals that reveal whether the experience works: result
counts, FAILED queries, and downstream clicks / saves / refinements."""

from opentelemetry import trace, metrics

tracer = trace.get_tracer("discovery")
meter = metrics.get_meter("discovery")

queries = meter.create_counter("discovery.queries")            # total, by failed/ok
clicks = meter.create_counter("discovery.clicks")              # user opened a rec
saves = meter.create_counter("discovery.saves")               # user saved a rec
refinements = meter.create_counter("discovery.refinements")   # user clicked a follow-up


def record_query(q, intent, results, failed):
    with tracer.start_as_current_span("discovery.query") as span:
        span.set_attribute("category", intent.get("category", "?"))
        span.set_attribute("results", results)
        span.set_attribute("failed", failed)         # zero grounded results
        queries.add(1, {"failed": str(failed)})


def record_click(place_id):
    clicks.add(1)        # which recommendations actually earn a tap
