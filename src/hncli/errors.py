class HNCLIError(Exception):
    """Base exception for hncli errors."""


class APIRequestError(HNCLIError):
    """Raised when a network request to the Hacker News API fails."""
