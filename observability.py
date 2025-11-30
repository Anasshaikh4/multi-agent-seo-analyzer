"""
Observability module for SEO Analysis ADK Project.

Implements:
- Structured logging with context
- Timing metrics collection
- Tracing for agent execution
- Performance monitoring

Demonstrates ADK observability concepts:
- Logging
- Tracing
- Metrics
"""

import logging
import time
import functools
import json
from typing import Any, Dict, Optional, Callable
from datetime import datetime
from contextlib import contextmanager
from dataclasses import dataclass, field, asdict

import config

# Configure structured logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL, logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - [%(trace_id)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


class TraceContextFilter(logging.Filter):
    """Add trace context to log records."""
    
    def __init__(self):
        super().__init__()
        self.trace_id = None
    
    def filter(self, record):
        record.trace_id = self.trace_id or "no-trace"
        return True


# Global trace filter
trace_filter = TraceContextFilter()


def get_logger(name: str) -> logging.Logger:
    """Get a logger with trace context support."""
    logger = logging.getLogger(name)
    logger.addFilter(trace_filter)
    return logger


logger = get_logger(__name__)


@dataclass
class Span:
    """Represents a tracing span for an operation."""
    name: str
    trace_id: str
    span_id: str
    parent_span_id: Optional[str] = None
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    duration_ms: Optional[int] = None
    status: str = "in_progress"
    attributes: Dict[str, Any] = field(default_factory=dict)
    events: list = field(default_factory=list)
    
    def end(self, status: str = "completed"):
        """End the span and calculate duration."""
        self.end_time = time.time()
        self.duration_ms = int((self.end_time - self.start_time) * 1000)
        self.status = status
    
    def add_event(self, name: str, attributes: Dict[str, Any] = None):
        """Add an event to the span."""
        self.events.append({
            "name": name,
            "timestamp": time.time(),
            "attributes": attributes or {}
        })
    
    def set_attribute(self, key: str, value: Any):
        """Set a span attribute."""
        self.attributes[key] = value
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert span to dictionary."""
        return asdict(self)


@dataclass
class Metric:
    """Represents a metric measurement."""
    name: str
    value: float
    unit: str
    timestamp: float = field(default_factory=time.time)
    labels: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class MetricsCollector:
    """Collects and stores metrics."""
    
    def __init__(self):
        self.metrics: list[Metric] = []
        self._counters: Dict[str, float] = {}
        self._gauges: Dict[str, float] = {}
        self._histograms: Dict[str, list] = {}
    
    def counter(self, name: str, value: float = 1, labels: Dict[str, str] = None):
        """Increment a counter metric."""
        key = f"{name}:{json.dumps(labels or {}, sort_keys=True)}"
        self._counters[key] = self._counters.get(key, 0) + value
        self.metrics.append(Metric(
            name=name,
            value=self._counters[key],
            unit="count",
            labels=labels or {}
        ))
    
    def gauge(self, name: str, value: float, labels: Dict[str, str] = None):
        """Set a gauge metric."""
        key = f"{name}:{json.dumps(labels or {}, sort_keys=True)}"
        self._gauges[key] = value
        self.metrics.append(Metric(
            name=name,
            value=value,
            unit="value",
            labels=labels or {}
        ))
    
    def histogram(self, name: str, value: float, labels: Dict[str, str] = None):
        """Record a histogram value."""
        key = f"{name}:{json.dumps(labels or {}, sort_keys=True)}"
        if key not in self._histograms:
            self._histograms[key] = []
        self._histograms[key].append(value)
        self.metrics.append(Metric(
            name=name,
            value=value,
            unit="ms",
            labels=labels or {}
        ))
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of all metrics."""
        return {
            "counters": self._counters,
            "gauges": self._gauges,
            "histograms": {
                k: {
                    "count": len(v),
                    "min": min(v) if v else 0,
                    "max": max(v) if v else 0,
                    "avg": sum(v) / len(v) if v else 0
                }
                for k, v in self._histograms.items()
            }
        }
    
    def clear(self):
        """Clear all metrics."""
        self.metrics.clear()
        self._counters.clear()
        self._gauges.clear()
        self._histograms.clear()


class Tracer:
    """Simple tracer for tracking operation execution."""
    
    def __init__(self):
        self.spans: list[Span] = []
        self._span_id_counter = 0
        self._trace_id_counter = 0
        self._current_trace_id: Optional[str] = None
        self._current_span_id: Optional[str] = None
    
    def _generate_span_id(self) -> str:
        """Generate a unique span ID."""
        self._span_id_counter += 1
        return f"span_{self._span_id_counter:08d}"
    
    def _generate_trace_id(self) -> str:
        """Generate a unique trace ID."""
        self._trace_id_counter += 1
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"trace_{timestamp}_{self._trace_id_counter:04d}"
    
    def start_trace(self, name: str) -> str:
        """Start a new trace and return the trace ID."""
        self._current_trace_id = self._generate_trace_id()
        trace_filter.trace_id = self._current_trace_id
        logger.info(f"Starting trace: {name}")
        return self._current_trace_id
    
    def end_trace(self):
        """End the current trace."""
        logger.info(f"Ending trace")
        trace_filter.trace_id = None
        self._current_trace_id = None
        self._current_span_id = None
    
    @contextmanager
    def span(self, name: str, attributes: Dict[str, Any] = None):
        """Context manager for creating a span."""
        trace_id = self._current_trace_id or self._generate_trace_id()
        span_id = self._generate_span_id()
        parent_span_id = self._current_span_id
        
        span_obj = Span(
            name=name,
            trace_id=trace_id,
            span_id=span_id,
            parent_span_id=parent_span_id,
            attributes=attributes or {}
        )
        
        self._current_span_id = span_id
        logger.debug(f"Starting span: {name}")
        
        try:
            yield span_obj
            span_obj.end("completed")
        except Exception as e:
            span_obj.end("error")
            span_obj.set_attribute("error", str(e))
            raise
        finally:
            self.spans.append(span_obj)
            self._current_span_id = parent_span_id
            logger.debug(f"Ended span: {name} ({span_obj.duration_ms}ms)")
    
    def get_trace_summary(self, trace_id: str = None) -> list[Dict[str, Any]]:
        """Get summary of spans for a trace."""
        spans = self.spans
        if trace_id:
            spans = [s for s in spans if s.trace_id == trace_id]
        return [s.to_dict() for s in spans]
    
    def clear(self):
        """Clear all spans."""
        self.spans.clear()


# Global instances
metrics = MetricsCollector()
tracer = Tracer()


def trace(name: str = None):
    """Decorator to trace function execution."""
    def decorator(func: Callable):
        span_name = name or func.__name__
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with tracer.span(span_name) as span:
                span.set_attribute("function", func.__name__)
                start = time.time()
                try:
                    result = func(*args, **kwargs)
                    duration = (time.time() - start) * 1000
                    metrics.histogram(
                        f"function_duration_{func.__name__}",
                        duration,
                        {"function": func.__name__}
                    )
                    return result
                except Exception as e:
                    metrics.counter(
                        "function_errors",
                        labels={"function": func.__name__, "error": type(e).__name__}
                    )
                    raise
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            with tracer.span(span_name) as span:
                span.set_attribute("function", func.__name__)
                start = time.time()
                try:
                    result = await func(*args, **kwargs)
                    duration = (time.time() - start) * 1000
                    metrics.histogram(
                        f"function_duration_{func.__name__}",
                        duration,
                        {"function": func.__name__}
                    )
                    return result
                except Exception as e:
                    metrics.counter(
                        "function_errors",
                        labels={"function": func.__name__, "error": type(e).__name__}
                    )
                    raise
        
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return wrapper
    
    return decorator


def log_agent_start(agent_name: str, url: str, request_id: str):
    """Log agent start event."""
    metrics.counter("agent_starts", labels={"agent": agent_name})
    logger.info(f"Agent {agent_name} starting analysis of {url}")


def log_agent_complete(agent_name: str, duration_ms: int, success: bool, request_id: str):
    """Log agent completion event."""
    status = "success" if success else "error"
    metrics.counter("agent_completions", labels={"agent": agent_name, "status": status})
    metrics.histogram("agent_duration", duration_ms, {"agent": agent_name})
    logger.info(f"Agent {agent_name} completed in {duration_ms}ms (status: {status})")


def log_analysis_start(url: str, request_id: str):
    """Log analysis start."""
    tracer.start_trace(f"seo_analysis_{request_id}")
    metrics.counter("analysis_starts")
    logger.info(f"Starting SEO analysis for {url}")


def log_analysis_complete(request_id: str, total_duration_ms: int, status: str):
    """Log analysis completion."""
    metrics.counter("analysis_completions", labels={"status": status})
    metrics.histogram("analysis_duration", total_duration_ms)
    logger.info(f"Analysis complete in {total_duration_ms}ms (status: {status})")
    tracer.end_trace()


def get_observability_report() -> Dict[str, Any]:
    """Get complete observability report."""
    return {
        "metrics_summary": metrics.get_summary(),
        "recent_traces": tracer.get_trace_summary()[-10:],  # Last 10 traces
        "timestamp": datetime.now().isoformat()
    }
