from datetime import datetime, timedelta

class PredictionCache:
    """Simple cache for ML predictions"""
    
    def __init__(self, ttl_minutes=10):
        """
        Initialize cache
        
        Args:
            ttl_minutes: Time to live in minutes (default: 10)
        """
        self.cache = {}
        self.ttl_minutes = ttl_minutes
    
    def get(self, key='next_hour_prediction'):
        """
        Get cached prediction if still valid
        
        Returns:
            dict or None: Cached prediction or None if expired/not found
        """
        if key not in self.cache:
            return None
        
        cached_data, cached_time = self.cache[key]
        
        # Check if cache is still valid
        if datetime.now() - cached_time < timedelta(minutes=self.ttl_minutes):
            return cached_data
        
        # Cache expired, remove it
        del self.cache[key]
        return None
    
    def set(self, data, key='next_hour_prediction'):
        """
        Cache prediction data
        
        Args:
            data: Prediction data to cache
            key: Cache key (default: 'next_hour_prediction')
        """
        self.cache[key] = (data, datetime.now())
    
    def clear(self, key=None):
        """
        Clear cache
        
        Args:
            key: Specific key to clear, or None to clear all
        """
        if key:
            if key in self.cache:
                del self.cache[key]
        else:
            self.cache.clear()
    
    def get_cache_info(self):
        """Get information about cached items"""
        info = {}
        for key, (data, cached_time) in self.cache.items():
            age_seconds = (datetime.now() - cached_time).total_seconds()
            ttl_seconds = max(0, self.ttl_minutes * 60 - age_seconds)
            info[key] = {
                'cached_at': cached_time.isoformat(),
                'age_seconds': int(age_seconds),
                'ttl_seconds': int(ttl_seconds),
                'is_valid': ttl_seconds > 0
            }
        return info

# Global cache instance
prediction_cache = PredictionCache(ttl_minutes=10)
