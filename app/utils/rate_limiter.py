from functools import wraps
from flask import request, jsonify
from datetime import datetime, timedelta
from collections import defaultdict, deque

class RateLimiter:
    """Simple in-memory rate limiter"""
    
    def __init__(self):
        # Store request timestamps per IP: {ip: deque([timestamp1, timestamp2, ...])}
        self.requests = defaultdict(deque)
    
    def is_rate_limited(self, ip, max_requests=10, window_seconds=60):
        """
        Check if IP has exceeded rate limit
        
        Args:
            ip: Client IP address
            max_requests: Maximum requests allowed in window
            window_seconds: Time window in seconds
        
        Returns:
            tuple: (is_limited: bool, retry_after: int)
        """
        now = datetime.now()
        cutoff_time = now - timedelta(seconds=window_seconds)
        
        # Get request history for this IP
        request_times = self.requests[ip]
        
        # Remove old requests outside the time window
        while request_times and request_times[0] < cutoff_time:
            request_times.popleft()
        
        # Check if limit exceeded
        if len(request_times) >= max_requests:
            # Calculate retry_after (seconds until oldest request expires)
            oldest_request = request_times[0]
            retry_after = int((oldest_request + timedelta(seconds=window_seconds) - now).total_seconds()) + 1
            return True, retry_after
        
        # Add current request
        request_times.append(now)
        
        return False, 0
    
    def cleanup_old_entries(self, max_age_seconds=3600):
        """
        Clean up old IP entries to prevent memory bloat
        Should be called periodically (e.g., every hour)
        """
        now = datetime.now()
        cutoff_time = now - timedelta(seconds=max_age_seconds)
        
        # Remove IPs with no recent requests
        ips_to_remove = []
        for ip, request_times in self.requests.items():
            if not request_times or request_times[-1] < cutoff_time:
                ips_to_remove.append(ip)
        
        for ip in ips_to_remove:
            del self.requests[ip]

# Global rate limiter instance
rate_limiter = RateLimiter()

def rate_limit(max_requests=10, window_seconds=60):
    """
    Decorator to rate limit endpoints
    
    Usage:
        @rate_limit(max_requests=10, window_seconds=60)
        def my_endpoint():
            return jsonify({'data': 'something'})
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get client IP
            client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
            
            # Check rate limit
            is_limited, retry_after = rate_limiter.is_rate_limited(
                client_ip, max_requests, window_seconds
            )
            
            if is_limited:
                return jsonify({
                    'status': 'error',
                    'message': f'Rate limit exceeded. Try again in {retry_after} seconds.',
                    'retry_after': retry_after
                }), 429
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator
