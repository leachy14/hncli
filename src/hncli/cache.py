"""
Simple caching module for the Hacker News CLI.
"""

import os
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional

# Cache structure: {key: (timestamp, value)}
_cache = {}

def get_cache_dir() -> Path:
    """Get the path to the cache directory."""
    cache_dir = Path.home() / ".cache" / "hncli"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir

def cache_key(prefix: str, *args) -> str:
    """Create a cache key from a prefix and arguments."""
    return f"{prefix}_{'-'.join(str(arg) for arg in args)}"

def get_cache_file(key: str) -> Path:
    """Get the path to a cache file for a key."""
    return get_cache_dir() / f"{key}.json"

def load_cache_from_disk() -> None:
    """Load all cache files from disk."""
    cache_dir = get_cache_dir()
    for cache_file in cache_dir.glob("*.json"):
        try:
            with open(cache_file, "r") as f:
                key = cache_file.stem
                timestamp, value = json.load(f)
                _cache[key] = (timestamp, value)
        except Exception:
            # Ignore corrupted cache files
            pass

def save_cache_to_disk(key: str) -> None:
    """Save a cache entry to disk."""
    if key in _cache:
        cache_file = get_cache_file(key)
        try:
            with open(cache_file, "w") as f:
                json.dump(_cache[key], f)
        except Exception:
            # Ignore errors when saving cache
            pass

def get(key: str, ttl: int = 300) -> Optional[Any]:
    """Get a value from cache if it exists and is not expired."""
    if key in _cache:
        timestamp, value = _cache[key]
        if time.time() - timestamp < ttl:
            return value
    return None

def set(key: str, value: Any) -> None:
    """Set a value in the cache."""
    _cache[key] = (time.time(), value)
    save_cache_to_disk(key)

def clear() -> None:
    """Clear the entire cache."""
    _cache.clear()
    cache_dir = get_cache_dir()
    for cache_file in cache_dir.glob("*.json"):
        try:
            os.unlink(cache_file)
        except Exception:
            # Ignore errors when deleting cache files
            pass

def clear_expired(ttl: int = 300) -> None:
    """Clear expired cache entries."""
    now = time.time()
    expired_keys = [key for key, (timestamp, _) in _cache.items() if now - timestamp >= ttl]
    
    for key in expired_keys:
        del _cache[key]
        cache_file = get_cache_file(key)
        try:
            os.unlink(cache_file)
        except Exception:
            # Ignore errors when deleting cache files
            pass

# Initialize cache from disk
load_cache_from_disk() 