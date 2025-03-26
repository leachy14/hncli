#!/usr/bin/env python3
"""
HackerNews CLI - A command-line interface for browsing Hacker News
"""

import typer
import requests
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress
from rich.markup import escape
from rich.text import Text
import webbrowser
from typing import List, Optional
import textwrap
import config
import cache

app = typer.Typer(help="Hacker News CLI")
console = Console()

# Base URLs for the Hacker News API
BASE_URL = "https://hacker-news.firebaseio.com/v0"
ITEM_URL = f"{BASE_URL}/item"
USER_URL = f"{BASE_URL}/user"
HN_WEB_URL = "https://news.ycombinator.com"

# Load configuration
def get_config_value(key, default=None):
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
    response = requests.get(f"{BASE_URL}/{story_type}stories.json")
    response.raise_for_status()
    result = response.json()
    
    # Cache the result
    cache.set(cache_key, result)
    return result

def get_item(item_id: int) -> dict:
    """Get an item (story, comment, etc.) by its ID."""
    # Check cache first
    cache_key = cache.cache_key("item", item_id)
    cached = cache.get(cache_key, ttl=get_config_value("cache_timeout_minutes", 5) * 60)
    if cached:
        return cached
    
    # Fetch from API if not cached
    response = requests.get(f"{ITEM_URL}/{item_id}.json")
    response.raise_for_status()
    result = response.json()
    
    # Cache the result
    cache.set(cache_key, result)
    return result

def get_user(username: str) -> dict:
    """Get a user profile by username."""
    # Check cache first
    cache_key = cache.cache_key("user", username)
    cached = cache.get(cache_key, ttl=get_config_value("cache_timeout_minutes", 5) * 60)
    if cached:
        return cached
    
    # Fetch from API if not cached
    response = requests.get(f"{USER_URL}/{username}.json")
    response.raise_for_status()
    result = response.json()
    
    # Cache the result
    cache.set(cache_key, result)
    return result

def format_time_ago(timestamp: int) -> str:
    """Format a Unix timestamp as a human-readable time ago string."""
    from datetime import datetime
    seconds_ago = int(datetime.now().timestamp() - timestamp)
    
    if seconds_ago < 60:
        return f"{seconds_ago} seconds ago"
    minutes_ago = seconds_ago // 60
    if minutes_ago < 60:
        return f"{minutes_ago} minutes ago"
    hours_ago = minutes_ago // 60
    if hours_ago < 24:
        return f"{hours_ago} hours ago"
    days_ago = hours_ago // 24
    if days_ago < 30:
        return f"{days_ago} days ago"
    months_ago = days_ago // 30
    if months_ago < 12:
        return f"{months_ago} months ago"
    years_ago = months_ago // 12
    return f"{years_ago} years ago"

def truncate_text(text: str, max_length: int = 80) -> str:
    """Truncate text to a maximum length."""
    if text and len(text) > max_length:
        return text[:max_length-3] + "..."
    return text or ""

def display_story(story: dict, show_index: Optional[int] = None) -> None:
    """Display a story in a rich panel."""
    title = story.get("title", "No title")
    url = story.get("url", f"{HN_WEB_URL}/item?id={story['id']}")
    points = story.get("score", 0)
    author = story.get("by", "unknown")
    comments_count = len(story.get("kids", []))
    time_ago = format_time_ago(story.get("time", 0))
    
    domain = ""
    if url and "://" in url:
        domain = url.split("://")[1].split("/")[0]
    
    title_display = Text(title)
    title_display.stylize("bold")
    
    index_prefix = f"[{show_index}] " if show_index is not None else ""
    
    content = f"{index_prefix}{title_display}\n\n"
    if domain:
        content += f"[link={url}]{domain}[/link]\n"
    content += f"\n{points} points by {author} {time_ago} | {comments_count} comments"
    
    panel = Panel(content, expand=False)
    console.print(panel)

def display_stories(stories: List[dict]) -> None:
    """Display a list of stories."""
    for i, story in enumerate(stories, 1):
        display_story(story, i)
        if i < len(stories):
            console.print("")  # Add a newline between stories

def display_comment(comment: dict, indent_level: int = 0) -> None:
    """Display a comment with appropriate indentation."""
    if "deleted" in comment or "dead" in comment:
        return
    
    author = comment.get("by", "unknown")
    time_ago = format_time_ago(comment.get("time", 0))
    text = comment.get("text", "")
    
    # Process HTML in comment text
    import html
    text = html.unescape(text)
    # Remove HTML tags (basic implementation, can be improved)
    text = text.replace("<p>", "\n\n").replace("</p>", "")
    
    indent = "  " * indent_level
    header = f"{indent}[bold]{author}[/bold] {time_ago}"
    console.print(header)
    
    # Wrap and indent comment text
    wrapped_text = textwrap.fill(text, width=100 - len(indent))
    wrapped_text = "\n".join(f"{indent}{line}" for line in wrapped_text.split("\n"))
    console.print(wrapped_text)
    console.print("")

def display_comments(story: dict, max_depth: int = None) -> None:
    """Display comments for a story with a maximum depth."""
    if max_depth is None:
        max_depth = get_config_value("max_comment_depth", 3)
        
    console.print(f"\n[bold]Comments for: {story.get('title', 'Unknown Story')}[/bold]\n")
    
    comment_ids = story.get("kids", [])
    if not comment_ids:
        console.print("No comments yet.")
        return
    
    def fetch_and_display_comments(comment_ids, depth=0):
        if depth >= max_depth or not comment_ids:
            return
        
        for comment_id in comment_ids[:10]:  # Limit to first 10 comments per level
            try:
                comment = get_item(comment_id)
                if "deleted" not in comment and "dead" not in comment:
                    display_comment(comment, depth)
                    # Recursively fetch child comments
                    if "kids" in comment:
                        fetch_and_display_comments(comment["kids"], depth + 1)
            except Exception as e:
                console.print(f"Error fetching comment {comment_id}: {e}")
    
    fetch_and_display_comments(comment_ids)

@app.command()
def top(limit: int = None) -> None:
    """Show top stories from Hacker News."""
    if limit is None:
        limit = get_config_value("stories_per_page", 10)
        
    with console.status("Fetching top stories..."):
        story_ids = get_story_ids("top")
        stories = []
        
        for story_id in story_ids[:limit]:
            try:
                story = get_item(story_id)
                if story and story.get("type") == "story":
                    stories.append(story)
            except Exception as e:
                console.print(f"Error fetching story {story_id}: {e}")
    
    console.print(f"\n[bold]Top {len(stories)} Stories[/bold]\n")
    display_stories(stories)

@app.command()
def new(limit: int = None) -> None:
    """Show new stories from Hacker News."""
    if limit is None:
        limit = get_config_value("stories_per_page", 10)
        
    with console.status("Fetching new stories..."):
        story_ids = get_story_ids("new")
        stories = []
        
        for story_id in story_ids[:limit]:
            try:
                story = get_item(story_id)
                if story and story.get("type") == "story":
                    stories.append(story)
            except Exception as e:
                console.print(f"Error fetching story {story_id}: {e}")
    
    console.print(f"\n[bold]Newest {len(stories)} Stories[/bold]\n")
    display_stories(stories)

@app.command()
def best(limit: int = None) -> None:
    """Show best stories from Hacker News."""
    if limit is None:
        limit = get_config_value("stories_per_page", 10)
        
    with console.status("Fetching best stories..."):
        story_ids = get_story_ids("best")
        stories = []
        
        for story_id in story_ids[:limit]:
            try:
                story = get_item(story_id)
                if story and story.get("type") == "story":
                    stories.append(story)
            except Exception as e:
                console.print(f"Error fetching story {story_id}: {e}")
    
    console.print(f"\n[bold]Best {len(stories)} Stories[/bold]\n")
    display_stories(stories)

@app.command()
def story(item_id: int) -> None:
    """Show a specific story and its comments."""
    with console.status(f"Fetching story {item_id}..."):
        try:
            story = get_item(item_id)
            if not story:
                console.print(f"Story {item_id} not found.")
                return
        except Exception as e:
            console.print(f"Error fetching story {item_id}: {e}")
            return
    
    display_story(story)
    
    # Ask if user wants to view comments
    if typer.confirm("\nView comments?"):
        display_comments(story)
    
    # Check if we should open in browser automatically
    open_in_browser = get_config_value("open_links_in_browser", True)
    if open_in_browser or typer.confirm("\nOpen in browser?"):
        webbrowser.open(f"{HN_WEB_URL}/item?id={item_id}")

@app.command()
def user(username: str) -> None:
    """Show a user profile."""
    with console.status(f"Fetching user {username}..."):
        try:
            user_data = get_user(username)
            if not user_data:
                console.print(f"User {username} not found.")
                return
        except Exception as e:
            console.print(f"Error fetching user {username}: {e}")
            return
    
    created = format_time_ago(user_data.get("created", 0))
    karma = user_data.get("karma", 0)
    about = user_data.get("about", "No information provided.")
    
    # Remove HTML from about
    import html
    about = html.unescape(about)
    about = about.replace("<p>", "\n\n").replace("</p>", "")
    
    user_table = Table(show_header=False)
    user_table.add_column("Field")
    user_table.add_column("Value")
    
    user_table.add_row("Username", username)
    user_table.add_row("Created", created)
    user_table.add_row("Karma", str(karma))
    user_table.add_row("About", about)
    
    console.print(Panel(user_table, title=f"[bold]User Profile: {username}[/bold]"))
    
    # Ask if user wants to open in browser
    if typer.confirm("\nOpen user profile in browser?"):
        webbrowser.open(f"{HN_WEB_URL}/user?id={username}")

@app.command()
def search(query: str, limit: int = None) -> None:
    """Search for stories on Hacker News.
    
    Note: This uses a simple search by fetching top stories and filtering locally.
    For a more comprehensive search, consider using the Algolia HN Search API.
    """
    if limit is None:
        limit = get_config_value("stories_per_page", 10)
        
    query = query.lower()
    
    with console.status(f"Searching for '{query}'..."):
        # Fetch stories from different categories to search through
        all_story_ids = []
        for story_type in ["top", "new", "best"]:
            try:
                all_story_ids.extend(get_story_ids(story_type)[:100])  # Get first 100 from each category
            except Exception as e:
                console.print(f"Error fetching {story_type} stories: {e}")
        
        # Remove duplicates
        all_story_ids = list(set(all_story_ids))
        
        # Search through stories
        matching_stories = []
        for story_id in all_story_ids:
            if len(matching_stories) >= limit:
                break
            
            try:
                story = get_item(story_id)
                if story and story.get("type") == "story":
                    title = story.get("title", "").lower()
                    text = story.get("text", "").lower()
                    
                    if query in title or query in text:
                        matching_stories.append(story)
            except Exception as e:
                # Silently ignore errors during search
                pass
    
    console.print(f"\n[bold]Search Results for '{query}'[/bold]\n")
    if matching_stories:
        display_stories(matching_stories)
    else:
        console.print("No matching stories found.")

@app.command()
def open(story_id: int) -> None:
    """Open a story in the web browser."""
    webbrowser.open(f"{HN_WEB_URL}/item?id={story_id}")
    console.print(f"Opening story {story_id} in browser...")

@app.command()
def config_set(key: str, value: str) -> None:
    """Update a configuration setting."""
    # Handle boolean values
    if value.lower() in ["true", "yes", "y", "1"]:
        value = True
    elif value.lower() in ["false", "no", "n", "0"]:
        value = False
    # Handle numeric values
    elif value.isdigit():
        value = int(value)
    
    try:
        config.update_setting(key, value)
        console.print(f"[green]Updated {key} to {value}[/green]")
    except Exception as e:
        console.print(f"[red]Error updating setting: {e}[/red]")

@app.command()
def config_get(key: Optional[str] = None) -> None:
    """Get current configuration settings."""
    if key:
        try:
            value = config.get_setting(key)
            console.print(f"{key}: {value}")
        except Exception as e:
            console.print(f"[red]Error getting setting: {e}[/red]")
    else:
        try:
            all_config = config.load_config()
            table = Table(title="Current Configuration")
            table.add_column("Setting")
            table.add_column("Value")
            
            for k, v in all_config.items():
                table.add_row(k, str(v))
            
            console.print(table)
        except Exception as e:
            console.print(f"[red]Error loading configuration: {e}[/red]")

@app.command()
def config_reset() -> None:
    """Reset configuration to defaults."""
    try:
        config.save_config(config.DEFAULT_CONFIG)
        console.print("[green]Configuration reset to defaults[/green]")
    except Exception as e:
        console.print(f"[red]Error resetting configuration: {e}[/red]")

@app.command()
def cache_clear() -> None:
    """Clear the cache to fetch fresh data."""
    cache.clear()
    console.print("[green]Cache cleared[/green]")

if __name__ == "__main__":
    app() 