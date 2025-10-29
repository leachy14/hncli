"""
API module for Hacker News CLI.

This module handles all interactions with the Hacker News Firebase API,
including fetching stories, items, and user profiles with caching support.
"""

import requests
from typing import Any, List
from hncli import config, cache
from hncli.errors import APIRequestError
from hncli.models import Story, User

# Base URLs for the Hacker News API
BASE_URL = "https://hacker-news.firebaseio.com/v0"
ITEM_URL = f"{BASE_URL}/item"
USER_URL = f"{BASE_URL}/user"
HN_WEB_URL = "https://news.ycombinator.com"


def get_config_value(key: str, default: Any = None) -> Any:
    """Get a configuration value with fallback to default."""
    try:
        return config.get_setting(key)
    except Exception:
        return default


def get_story_ids(story_type: str) -> List[int]:
    """Get story IDs based on the story type (top, new, best)."""
    # Check cache first
    cache_key = cache.cache_key("stories", story_type)
    cached = cache.get(cache_key, ttl=get_config_value("cache_timeout_minutes", 5) * 60)
    if cached:
        return cached

    # Fetch from API if not cached
    try:
        response = requests.get(f"{BASE_URL}/{story_type}stories.json")
        response.raise_for_status()
        result = response.json()
    except requests.RequestException as exc:
        raise APIRequestError(f"Failed to fetch {story_type} stories") from exc

    # Cache the result
    cache.set(cache_key, result)
    return result


def get_item(item_id: int) -> Story:
    """Get an item (story, comment, etc.) by its ID."""
    # Check cache first
    cache_key = cache.cache_key("item", item_id)
    cached = cache.get(cache_key, ttl=get_config_value("cache_timeout_minutes", 5) * 60)
    if cached:
        return Story.model_validate(cached)

    # Fetch from API if not cached
    try:
        response = requests.get(f"{ITEM_URL}/{item_id}.json")
        response.raise_for_status()
        result = response.json()
    except requests.RequestException as exc:
        raise APIRequestError(f"Failed to fetch item {item_id}") from exc


    # Cache the result
    cache.set(cache_key, result)
    return Story.model_validate(result)


def get_user(username: str) -> User:
    """Get a user profile by username."""
    # Check cache first
    cache_key = cache.cache_key("user", username)
    cached = cache.get(cache_key, ttl=get_config_value("cache_timeout_minutes", 5) * 60)
    if cached:
        return User.model_validate(cached)

    # Fetch from API if not cached

    try:
        response = requests.get(f"{USER_URL}/{username}.json")
        response.raise_for_status()
        result = response.json()
    except requests.RequestException as exc:
        raise APIRequestError(f"Failed to fetch user {username}") from exc

    # Cache the result
    cache.set(cache_key, result)
    return User.model_validate(result)
