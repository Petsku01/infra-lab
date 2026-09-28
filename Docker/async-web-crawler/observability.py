"""
Structured observability logging module
Provides JSON-formatted logs with trace IDs, metrics, and context
@author pk
"""

import logging
import json
import time
import uuid
from typing import Dict, Any, Optional
from contextlib import contextmanager
from datetime import datetime


class StructuredLogger:
    """
    Provides structured logging with trace IDs and metrics.
    Outputs JSON-formatted logs for easy parsing by log aggregators.
    """
    
    def __init__(self, name: str, trace_id: Optional[str] = None):
        self.logger = logging.getLogger(name)
        self.trace_id = trace_id or str(uuid.uuid4())
        self.context = {}
    
    def _format_message(self, level: str, message: str, **kwargs) -> str:
        """Format log message as JSON."""
        log_entry = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': level,
            'trace_id': self.trace_id,
            'logger': self.logger.name,
            'message': message,
            **self.context,
            **kwargs
        }
        return json.dumps(log_entry)
    
    def debug(self, message: str, **kwargs):
        """Log debug message with structured data."""
        self.logger.debug(self._format_message('DEBUG', message, **kwargs))
    
    def info(self, message: str, **kwargs):
        """Log info message with structured data."""
        self.logger.info(self._format_message('INFO', message, **kwargs))
    
    def warning(self, message: str, **kwargs):
        """Log warning message with structured data."""
        self.logger.warning(self._format_message('WARNING', message, **kwargs))
    
    def error(self, message: str, **kwargs):
        """Log error message with structured data."""
        self.logger.error(self._format_message('ERROR', message, **kwargs))
    
    def critical(self, message: str, **kwargs):
        """Log critical message with structured data."""
        self.logger.critical(self._format_message('CRITICAL', message, **kwargs))
    
    def add_context(self, **kwargs):
        """Add persistent context to all log messages."""
        self.context.update(kwargs)
    
    def clear_context(self):
        """Clear all persistent context."""
        self.context.clear()
    
    @contextmanager
    def operation(self, operation_name: str, **kwargs):
        """
        Context manager for tracking operation timing and status.
        
        Usage:
            with logger.operation('fetch_url', url='https://example.com'):
                # do work
                pass
        """
        operation_id = str(uuid.uuid4())[:8]
        start_time = time.time()
        
        self.info(
            f"Operation started: {operation_name}",
            operation=operation_name,
            operation_id=operation_id,
            status='started',
            **kwargs
        )
        
        try:
            yield
            duration_ms = (time.time() - start_time) * 1000
            
            self.info(
                f"Operation completed: {operation_name}",
                operation=operation_name,
                operation_id=operation_id,
                status='completed',
                duration_ms=round(duration_ms, 2),
                **kwargs
            )
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            
            self.error(
                f"Operation failed: {operation_name}",
                operation=operation_name,
                operation_id=operation_id,
                status='failed',
                duration_ms=round(duration_ms, 2),
                error_type=type(e).__name__,
                error_message=str(e),
                **kwargs
            )
            raise


class MetricsCollector:
    """
    Collects application metrics for observability.
    Tracks counters, gauges, histograms, and timing data.
    """
    
    def __init__(self):
        self.counters = {}
        self.gauges = {}
        self.histograms = {}
        self.timings = {}
    
    def increment(self, metric: str, value: int = 1, **labels):
        """Increment a counter metric."""
        key = self._make_key(metric, labels)
        self.counters[key] = self.counters.get(key, 0) + value
    
    def set_gauge(self, metric: str, value: float, **labels):
        """Set a gauge metric (current value)."""
        key = self._make_key(metric, labels)
        self.gauges[key] = value
    
    def record_timing(self, metric: str, duration_ms: float, **labels):
        """Record a timing measurement."""
        key = self._make_key(metric, labels)
        if key not in self.histograms:
            self.histograms[key] = []
        self.histograms[key].append(duration_ms)
    
    @contextmanager
    def time_operation(self, metric: str, **labels):
        """Context manager for timing operations."""
        start_time = time.time()
        try:
            yield
        finally:
            duration_ms = (time.time() - start_time) * 1000
            self.record_timing(metric, duration_ms, **labels)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of all metrics."""
        summary = {
            'counters': dict(self.counters),
            'gauges': dict(self.gauges),
            'histograms': {}
        }
        
        # Calculate histogram statistics
        for key, values in self.histograms.items():
            if values:
                sorted_values = sorted(values)
                n = len(values)
                summary['histograms'][key] = {
                    'count': n,
                    'min': round(min(values), 2),
                    'max': round(max(values), 2),
                    'mean': round(sum(values) / n, 2),
                    'p50': round(sorted_values[n // 2], 2),
                    'p95': round(sorted_values[int(n * 0.95)], 2) if n > 1 else sorted_values[0],
                    'p99': round(sorted_values[int(n * 0.99)], 2) if n > 1 else sorted_values[0]
                }
        
        return summary
    
    def _make_key(self, metric: str, labels: Dict[str, Any]) -> str:
        """Create unique key for metric with labels."""
        if not labels:
            return metric
        label_str = ','.join(f"{k}={v}" for k, v in sorted(labels.items()))
        return f"{metric}{{{label_str}}}"
    
    def reset(self):
        """Reset all metrics."""
        self.counters.clear()
        self.gauges.clear()
        self.histograms.clear()
        self.timings.clear()


# Global metrics collector instance
metrics = MetricsCollector()
