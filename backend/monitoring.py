"""
Monitoring and Metrics Collection
"""

import time
import psutil
from datetime import datetime
from typing import Dict, List
from collections import defaultdict

class MetricsCollector:
    """Collect system and trading metrics"""
    
    def __init__(self):
        self.request_counts = defaultdict(int)
        self.request_times = defaultdict(list)
        self.error_counts = defaultdict(int)
        self.start_time = datetime.now()
        
    def record_request(self, endpoint: str, duration_ms: float):
        """Record API request metrics"""
        self.request_counts[endpoint] += 1
        self.request_times[endpoint].append(duration_ms)
        
        # Keep only last 1000 times
        if len(self.request_times[endpoint]) > 1000:
            self.request_times[endpoint] = self.request_times[endpoint][-1000:]
    
    def record_error(self, endpoint: str):
        """Record error metrics"""
        self.error_counts[endpoint] += 1
    
    def get_metrics(self) -> Dict:
        """Get current metrics"""
        metrics = {
            'uptime_seconds': (datetime.now() - self.start_time).total_seconds(),
            'total_requests': sum(self.request_counts.values()),
            'total_errors': sum(self.error_counts.values()),
            'endpoints': {},
            'system': {
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_usage': psutil.disk_usage('/').percent
            }
        }
        
        for endpoint, times in self.request_times.items():
            if times:
                metrics['endpoints'][endpoint] = {
                    'count': self.request_counts[endpoint],
                    'errors': self.error_counts[endpoint],
                    'avg_latency_ms': sum(times) / len(times),
                    'max_latency_ms': max(times),
                    'min_latency_ms': min(times)
                }
        
        return metrics
    
    def get_performance_report(self) -> str:
        """Generate performance report"""
        metrics = self.get_metrics()
        
        report = f"""
        ========================================
        TRADING ENGINE PERFORMANCE REPORT
        ========================================
        Uptime: {metrics['uptime_seconds'] / 3600:.1f} hours
        Total Requests: {metrics['total_requests']}
        Total Errors: {metrics['total_errors']}
        Error Rate: {(metrics['total_errors'] / max(metrics['total_requests'], 1)) * 100:.2f}%
        
        System Resources:
        - CPU: {metrics['system']['cpu_percent']}%
        - Memory: {metrics['system']['memory_percent']}%
        - Disk: {metrics['system']['disk_usage']}%
        
        Endpoint Performance:
        """
        
        for endpoint, stats in metrics['endpoints'].items():
            report += f"""
        {endpoint}:
            - Requests: {stats['count']}
            - Avg Latency: {stats['avg_latency_ms']:.2f}ms
            - Max Latency: {stats['max_latency_ms']:.2f}ms
        """
        
        return report

# Global metrics collector
metrics = MetricsCollector()