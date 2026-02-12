
"""
Performance monitoring and metrics collection.
Tracks request times, errors, and slow queries.
"""

import time
import logging
from typing import Dict, List
from datetime import datetime, timedelta
from collections import defaultdict
from threading import Lock

logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """
    In-memory performance metrics collector.
    
    In production, use a proper monitoring solution like:
    - Prometheus + Grafana
    - DataDog
    - New Relic
    - AWS CloudWatch
    """
    
    def __init__(self):
        self.metrics: Dict[str, List[float]] = defaultdict(list)
        self.errors: Dict[str, int] = defaultdict(int)
        self.lock = Lock()
        self.start_time = datetime.utcnow()
    
    def record_request(self, endpoint: str, duration: float, status_code: int):
        """
        Record request metrics.
        
        Args:
            endpoint: API endpoint path
            duration: Request duration in seconds
            status_code: HTTP status code
        """
        with self.lock:
            self.metrics[endpoint].append(duration)
            
            # Track errors
            if status_code >= 400:
                self.errors[endpoint] += 1
            
            # Keep only last 1000 requests per endpoint
            if len(self.metrics[endpoint]) > 1000:
                self.metrics[endpoint] = self.metrics[endpoint][-1000:]
    
    def get_stats(self, endpoint: str = None) -> Dict:
        """
        Get performance statistics.
        
        Args:
            endpoint: Specific endpoint (None for all)
            
        Returns:
            Dictionary with statistics
        """
        with self.lock:
            if endpoint:
                durations = self.metrics.get(endpoint, [])
                if not durations:
                    return {"endpoint": endpoint, "requests": 0}
                
                return {
                    "endpoint": endpoint,
                    "requests": len(durations),
                    "avg_time": sum(durations) / len(durations),
                    "min_time": min(durations),
                    "max_time": max(durations),
                    "errors": self.errors.get(endpoint, 0)
                }
            
            # All endpoints
            all_stats = []
            for endpoint, durations in self.metrics.items():
                if durations:
                    all_stats.append({
                        "endpoint": endpoint,
                        "requests": len(durations),
                        "avg_time": sum(durations) / len(durations),
                        "min_time": min(durations),
                        "max_time": max(durations),
                        "errors": self.errors.get(endpoint, 0)
                    })
            
            # Sort by average time (slowest first)
            all_stats.sort(key=lambda x: x["avg_time"], reverse=True)
            
            return {
                "uptime_seconds": (datetime.utcnow() - self.start_time).total_seconds(),
                "total_requests": sum(len(d) for d in self.metrics.values()),
                "total_errors": sum(self.errors.values()),
                "endpoints": all_stats[:10]  # Top 10 slowest
            }
    
    def reset(self):
        """Reset all metrics."""
        with self.lock:
            self.metrics.clear()
            self.errors.clear()
            self.start_time = datetime.utcnow()


# Global monitor instance
performance_monitor = PerformanceMonitor()