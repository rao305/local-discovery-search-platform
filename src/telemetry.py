"""Evals measure quality offline; telemetry measures the LIVE product. Each
query gets an OpenTelemetry span (trace parse→ground→rank end to end) and we
record the product signals that reveal whether the experience works: result
counts, FAILED queries, and downstream clicks / saves / refinements."""

from __future__ import annotations

import logging

from opentelemetry import metrics, trace
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import (
    ConsoleMetricExporter,
    PeriodicExportingMetricReader,
)
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

_log = logging.getLogger("discovery.telemetry")
_configured = False


def setup_telemetry(console: bool = True) -> None:
    """Wire OTel to the console so beginners see spans/metrics without Jaeger."""
    global _configured
    if _configured:
        return

    resource = Resource.create({"service.name": "local-discovery"})

    tracer_provider = TracerProvider(resource=resource)
    if console:
        tracer_provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
    trace.set_tracer_provider(tracer_provider)

    if console:
        reader = PeriodicExportingMetricReader(
            ConsoleMetricExporter(),
            export_interval_millis=60_000,
        )
        meter_provider = MeterProvider(resource=resource, metric_readers=[reader])
    else:
        meter_provider = MeterProvider(resource=resource)
    metrics.set_meter_provider(meter_provider)
    _configured = True


# Configure once on import so API/tests always have a tracer/meter.
setup_telemetry(console=False)

tracer = trace.get_tracer("discovery")
meter = metrics.get_meter("discovery")

queries = meter.create_counter("discovery.queries")  # total, by failed/ok
clicks = meter.create_counter("discovery.clicks")  # user opened a rec
saves = meter.create_counter("discovery.saves")  # user saved a rec
refinements = meter.create_counter("discovery.refinements")  # user clicked a follow-up


def record_query(q, intent, results, failed):
    with tracer.start_as_current_span("discovery.query") as span:
        span.set_attribute("query", (q or "")[:120])
        span.set_attribute("category", intent.get("category", "?"))
        span.set_attribute("results", results)
        span.set_attribute("failed", failed)  # zero grounded results
        queries.add(1, {"failed": str(failed)})
        if failed:
            _log.info("FAILED query (no grounded results): %s", q)


def record_click(place_id):
    clicks.add(1)  # which recommendations actually earn a tap
    with tracer.start_as_current_span("discovery.click") as span:
        span.set_attribute("place_id", place_id)


def record_save(place_id):
    saves.add(1)
    with tracer.start_as_current_span("discovery.save") as span:
        span.set_attribute("place_id", place_id)


def record_refinement(label):
    """Follow-up chips like 'More upscale' — each is a NEW grounded query."""
    refinements.add(1)
    with tracer.start_as_current_span("discovery.refinement") as span:
        span.set_attribute("label", label)
