import os
import time
from typing import Callable

from flask import Response, request
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    CollectorRegistry,
    Counter,
    Histogram,
    generate_latest,
)

metrics_registry = CollectorRegistry()


http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"],
    registry=metrics_registry,
)

http_request_latency_seconds = Histogram(
    "http_request_latency_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint"],
    buckets=(
        0.01,
        0.025,
        0.05,
        0.1,
        0.25,
        0.5,
        1.0,
        2.5,
        5.0,
        10.0,
    ),
    registry=metrics_registry,
)


# Eater operation metrics
eater_operation_total = Counter(
    "eater_operation_total",
    "Count of eater operations by name and outcome",
    ["operation", "outcome"],
    registry=metrics_registry,
)

eater_operation_latency_seconds = Histogram(
    "eater_operation_latency_seconds",
    "Latency of eater operations in seconds",
    ["operation", "outcome"],
    buckets=(
        0.01,
        0.025,
        0.05,
        0.1,
        0.25,
        0.5,
        1.0,
        2.5,
        5.0,
        10.0,
    ),
    registry=metrics_registry,
)


def metrics_endpoint() -> Response:
    """Return Prometheus metrics in text format."""
    return Response(generate_latest(metrics_registry), mimetype=CONTENT_TYPE_LATEST)


def record_http_metrics(start_time: float, endpoint: str, status: int) -> None:
    """Record metrics for an HTTP request."""
    method = request.method if request else "UNKNOWN"
    elapsed = time.time() - start_time
    http_request_latency_seconds.labels(method=method, endpoint=endpoint).observe(
        elapsed
    )
    http_requests_total.labels(
        method=method, endpoint=endpoint, status=str(status)
    ).inc()


def track_eater_operation(
    operation_name: str,
) -> Callable[[Callable[..., Response]], Callable[..., Response]]:
    """Decorator to track eater operation success/failure and latency."""

    def decorator(func: Callable[..., Response]) -> Callable[..., Response]:
        def wrapper(*args, **kwargs):
            start = time.time()
            try:
                response = func(*args, **kwargs)
                status_code = getattr(response, "status_code", 200)
                outcome = "success" if 200 <= int(status_code) < 400 else "error"
                elapsed = time.time() - start
                eater_operation_total.labels(
                    operation=operation_name, outcome=outcome
                ).inc()
                eater_operation_latency_seconds.labels(
                    operation=operation_name, outcome=outcome
                ).observe(elapsed)
                return response
            except Exception:
                elapsed = time.time() - start
                eater_operation_total.labels(
                    operation=operation_name, outcome="exception"
                ).inc()
                eater_operation_latency_seconds.labels(
                    operation=operation_name, outcome="exception"
                ).observe(elapsed)
                raise

        wrapper.__name__ = getattr(func, "__name__", f"wrapped_{operation_name}")
        return wrapper

    return decorator
