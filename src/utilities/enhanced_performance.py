"""
Enhanced Error Recovery and Performance Optimizations for VAPOR
"""

import asyncio
import time
import hashlib
import gzip
from pathlib import Path
from typing import Any, Callable, Optional

class EnhancedRetryMechanism:
    """Intelligent retry system with exponential backoff and circuit breaker pattern"""
    
    def __init__(self, max_retries=3, base_delay=1.0, max_delay=30.0, circuit_breaker_threshold=5):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.circuit_breaker_threshold = circuit_breaker_threshold
        self.consecutive_failures = 0
        self.last_failure_time = 0
        
    def calculate_delay(self, attempt: int) -> float:
        """Calculate delay with exponential backoff and jitter"""
        import random
        base_delay = min(self.base_delay * (2 ** attempt), self.max_delay)
        # Add jitter to prevent thundering herd
        jitter = random.uniform(0.5, 1.5)
        return base_delay * jitter
    
    def is_circuit_open(self) -> bool:
        """Check if circuit breaker is open (too many recent failures)"""
        if self.consecutive_failures >= self.circuit_breaker_threshold:
            # Circuit is open for 5 minutes after threshold failures
            return (time.time() - self.last_failure_time) < 300
        return False
    
    def execute_with_retry(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with intelligent retry logic"""
        if self.is_circuit_open():
            raise Exception("Circuit breaker is open - too many recent failures")
        
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                result = func(*args, **kwargs)
                # Success - reset circuit breaker
                self.consecutive_failures = 0
                return result
                
            except Exception as e:
                last_exception = e
                self.consecutive_failures += 1
                self.last_failure_time = time.time()
                
                if attempt < self.max_retries and self._is_retryable_error(e):
                    delay = self.calculate_delay(attempt)
                    print(f"Retry attempt {attempt + 1}/{self.max_retries} after {delay:.1f}s delay")
                    time.sleep(delay)
                else:
                    break
        
        # All retries exhausted
        raise last_exception
    
    def _is_retryable_error(self, error: Exception) -> bool:
        """Determine if error is worth retrying"""
        error_str = str(error).lower()
        retryable_patterns = [
            'timeout', 'connection', 'network', 'dns', 'rate limit',
            '429', '500', '502', '503', '504', 'temporary'
        ]
        return any(pattern in error_str for pattern in retryable_patterns)


class IntelligentCache:
    """Smart caching system with LRU eviction and compression"""
    
    def __init__(self, cache_dir: Path, max_size_mb: int = 500):
        self.cache_dir = cache_dir
        self.max_size = max_size_mb * 1024 * 1024
        self.index_file = cache_dir / "cache_index.json"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.index = self._load_index()
    
    def _load_index(self) -> dict:
        """Load cache index from disk"""
        try:
            if self.index_file.exists():
                import json
                with open(self.index_file, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        return {}
    
    def _save_index(self):
        """Save cache index to disk"""
        try:
            import json
            with open(self.index_file, 'w') as f:
                json.dump(self.index, f, indent=2)
        except Exception as e:
            print(f"Failed to save cache index: {e}")
    
    def _get_cache_file(self, key: str) -> Path:
        """Get cache file path for key"""
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{key_hash}.gz"
    
    def get(self, key: str) -> Optional[bytes]:
        """Get cached data"""
        if key not in self.index:
            return None
        
        cache_file = self._get_cache_file(key)
        if not cache_file.exists():
            # Remove stale index entry
            del self.index[key]
            self._save_index()
            return None
        
        try:
            with open(cache_file, 'rb') as f:
                compressed_data = f.read()
            
            # Update access time for LRU
            self.index[key]['last_access'] = time.time()
            
            return gzip.decompress(compressed_data)
        except Exception:
            return None
    
    def put(self, key: str, data: bytes):
        """Cache data with compression"""
        try:
            compressed_data = gzip.compress(data)
            cache_file = self._get_cache_file(key)
            
            with open(cache_file, 'wb') as f:
                f.write(compressed_data)
            
            # Update index
            self.index[key] = {
                'size': len(compressed_data),
                'created': time.time(),
                'last_access': time.time()
            }
            
            self._cleanup_if_needed()
            self._save_index()
            
        except Exception as e:
            print(f"Failed to cache data: {e}")
    
    def _cleanup_if_needed(self):
        """Remove old cache entries if size limit exceeded"""
        total_size = sum(entry['size'] for entry in self.index.values())
        
        if total_size > self.max_size:
            # Sort by last access time (LRU)
            sorted_items = sorted(
                self.index.items(),
                key=lambda x: x[1]['last_access']
            )
            
            # Remove oldest entries until under limit
            for key, entry in sorted_items:
                if total_size <= self.max_size * 0.8:  # Leave some headroom
                    break
                
                cache_file = self._get_cache_file(key)
                try:
                    cache_file.unlink(missing_ok=True)
                    total_size -= entry['size']
                    del self.index[key]
                except Exception:
                    pass


class PerformanceTelemetry:
    """Anonymous performance monitoring and optimization insights"""
    
    def __init__(self):
        self.metrics = {
            'startup_time': 0,
            'api_calls_count': 0,
            'cache_hit_rate': 0,
            'total_games_processed': 0,
            'average_processing_time': 0,
            'memory_usage_peak': 0,
            'errors_encountered': 0
        }
        self.enabled = False  # Opt-in only
    
    def enable_telemetry(self, user_consent: bool):
        """Enable telemetry only with explicit user consent"""
        self.enabled = user_consent
    
    def record_metric(self, metric_name: str, value: float):
        """Record a performance metric"""
        if self.enabled:
            self.metrics[metric_name] = value
    
    def increment_metric(self, metric_name: str, amount: int = 1):
        """Increment a counter metric"""
        if self.enabled:
            self.metrics[metric_name] = self.metrics.get(metric_name, 0) + amount
    
    def get_optimization_suggestions(self) -> list:
        """Generate optimization suggestions based on metrics"""
        suggestions = []
        
        if self.metrics['cache_hit_rate'] < 50:
            suggestions.append("Consider increasing cache size for better performance")
        
        if self.metrics['average_processing_time'] > 3.0:
            suggestions.append("Network connection may be slow - try closing other applications")
        
        if self.metrics['errors_encountered'] > 5:
            suggestions.append("Multiple errors detected - check API keys and network connection")
        
        return suggestions
