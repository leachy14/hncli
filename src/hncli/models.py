from __future__ import annotations

"""Pydantic models for Hacker News API objects."""

from typing import Any, List, Optional
from pydantic import BaseModel, ConfigDict


class Story(BaseModel):
    """Representation of an item returned by the Hacker News API."""

    id: int
    by: Optional[str] = None
    time: Optional[int] = None
    type: Optional[str] = None
    title: Optional[str] = None
    url: Optional[str] = None
    score: Optional[int] = None
    descendants: Optional[int] = None
    kids: Optional[List[int]] = None
    text: Optional[str] = None
    parent: Optional[int] = None

    model_config = ConfigDict(extra="allow")

    def get(self, key: str, default: Optional[Any] = None) -> Optional[Any]:
        """Dictionary-style access helper."""
        return getattr(self, key, default)


class User(BaseModel):
    """Representation of a user profile returned by the Hacker News API."""

    id: str
    created: Optional[int] = None
    karma: Optional[int] = None
    about: Optional[str] = None
    submitted: Optional[List[int]] = None

    model_config = ConfigDict(extra="allow")

    def get(self, key: str, default: Optional[Any] = None) -> Optional[Any]:
        """Dictionary-style access helper."""
        return getattr(self, key, default)
