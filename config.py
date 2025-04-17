"""
Configuration settings for the Hacker News CLI.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional

# Default configuration
DEFAULT_CONFIG = {
    # Maximum number of stories per page (actual number may be lower based on terminal size)
    "stories_per_page": 10,
    # Maximum depth of comments to display 
    "max_comment_depth": 3,
    # Whether to automatically open links in browser
    "open_links_in_browser": True,
    # Color theme to use
    "color_theme": "default",
    # Cache timeout in minutes
    "cache_timeout_minutes": 5
}

def get_config_path() -> Path:
    """Get the path to the configuration file."""
    config_dir = Path.home() / ".config" / "hncli"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir / "config.json"

def load_config() -> Dict[str, Any]:
    """Load configuration from file or create default."""
    config_path = get_config_path()
    
    if config_path.exists():
        try:
            with open(config_path, "r") as f:
                user_config = json.load(f)
                # Update with any missing default values
                config = DEFAULT_CONFIG.copy()
                config.update(user_config)
                return config
        except Exception:
            # If there's an error loading the config, use defaults
            return DEFAULT_CONFIG
    else:
        # Create default config file
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG

def save_config(config: Dict[str, Any]) -> None:
    """Save configuration to file."""
    config_path = get_config_path()
    
    with open(config_path, "w") as f:
        json.dump(config, f, indent=4)

def get_setting(key: str) -> Any:
    """Get a specific setting from the configuration."""
    config = load_config()
    return config.get(key, DEFAULT_CONFIG.get(key))

def update_setting(key: str, value: Any) -> None:
    """Update a specific setting in the configuration."""
    config = load_config()
    config[key] = value
    save_config(config) 