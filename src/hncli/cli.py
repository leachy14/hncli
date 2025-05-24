#!/usr/bin/env python3
"""
HackerNews CLI - A command-line interface for browsing Hacker News
"""


import typer
import requests
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt
from rich.markup import escape
import webbrowser
from typing import Any, List, Optional, Tuple
import textwrap
from hncli import config, cache
import os
import shutil
import re
import inspect
import click

# ---------------------------------------------------------------------------
# Compatibility patches
# ---------------------------------------------------------------------------
# Typer 0.9 is incompatible with Click ≥ 8.2 due to the new "ctx" parameter in
# ``Parameter.make_metavar``. When Click 8.2+ is used, calling ``make_metavar``
# without a context raises ``TypeError`` during command execution.  To maintain
# compatibility with newer Click versions, we patch ``Parameter.make_metavar``
# to accept an optional ``ctx`` argument.

if "ctx" in inspect.signature(click.Parameter.make_metavar).parameters:
    _original_make_metavar = click.Parameter.make_metavar

    def _patched_make_metavar(self, ctx: Optional[click.Context] = None) -> str:
        if ctx is None:
            ctx = click.Context(click.Command("dummy"))
        return _original_make_metavar(self, ctx)

    click.Parameter.make_metavar = _patched_make_metavar  # type: ignore[assignment]

app = typer.Typer(help="Hacker News CLI")
console = Console()

# Base URLs for the Hacker News API
BASE_URL = "https://hacker-news.firebaseio.com/v0"
ITEM_URL = f"{BASE_URL}/item"
USER_URL = f"{BASE_URL}/user"
HN_WEB_URL = "https://news.ycombinator.com"

# Load configuration

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

def get_terminal_size() -> Tuple[int, int]:
    """Get the current terminal size."""
    try:
        # Get terminal size
        columns, rows = shutil.get_terminal_size()
        return columns, rows
    except Exception:
        # Default to standard size if detection fails
        return 80, 24

def calculate_stories_per_page() -> int:
    """
    Calculate how many stories to display per page based on terminal size.

    Calculates available rows after reserving lines for interface elements
    (banner, header, blank lines, navigation menu) and clamps the result
    between 10 and 20 stories per page for optimal readability.
    """
    # Determine terminal height and estimate available rows for stories
    _, rows = get_terminal_size()
    # Reserve lines for interface elements (banner/title, table header,
    # blank lines, and navigation menu).
    RESERVED_ROWS = 8
    available_rows = max(rows - RESERVED_ROWS, 1)

    # Clamp the number of stories per page between defined minimum and maximum
    MIN_STORIES = 10
    MAX_STORIES = 20
    # If terminal too small, show at least MIN_STORIES; if too large, cap at MAX_STORIES
    return max(MIN_STORIES, min(available_rows, MAX_STORIES))

# ---------------------------------------------------------------------------
# Story presentation helpers
# ---------------------------------------------------------------------------

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
    
    # Make the story title itself clickable. For panels (single‑story
    # view) we rely on Rich markup to apply both the *bold* style and the
    # hyperlink.

    index_prefix = f"[{show_index}] " if show_index is not None else ""

    content = (
        f"{index_prefix}[link={url}][bold]{escape(title)}[/bold][/link]\n\n"
    )
    if domain:
        content += f"[link={url}]{domain}[/link]\n"
    content += f"\n{points} points by {author} {time_ago} | {comments_count} comments"
    
    panel = Panel(content, expand=False)
    console.print(panel)

def display_stories(stories: List[dict]) -> None:
    """Display a list of stories in a compact table format."""

    if not stories:
        console.print("No stories to display.")
        return

    columns, _ = get_terminal_size()

    table = Table(show_header=True, header_style="bold", expand=False)
    table.add_column("#", style="dim", width=4, no_wrap=True)

    # The width left for the title column after subtracting the fixed‑width
    # columns (index + points + comments + age + column padding).
    fixed_width = 4 + 6 + 9 + 12 + 4  # column widths + minimal paddings
    title_width = max(columns - fixed_width, 20)

    table.add_column("Title", width=title_width, overflow="ellipsis", no_wrap=True)
    table.add_column("Pts", justify="right", width=6, no_wrap=True)
    table.add_column("Cmts", justify="right", width=9, no_wrap=True)
    table.add_column("Age", style="dim", width=12, no_wrap=True)

    for idx, story in enumerate(stories, 1):
        title = story.get("title", "No title")
        url = story.get("url", f"{HN_WEB_URL}/item?id={story['id']}")
        domain = ""
        if url and "://" in url:
            domain = url.split("://")[1].split("/")[0]
        title_text = escape(title)
        domain_text = escape(domain)

        title_markup = f"[link={url}]{title_text}[/link]"
        if domain:
            title_markup += f" ({domain_text})"

        points = str(story.get("score", 0))
        comments_count = str(len(story.get("kids", [])))
        age = format_time_ago(story.get("time", 0))

        table.add_row(str(idx), title_markup, points, comments_count, age)

    console.print(table)

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
    columns, _ = get_terminal_size()
    wrap_width = min(100, columns - len(indent) - 5)  # Account for indent and margin
    wrapped_text = textwrap.fill(text, width=wrap_width)
    wrapped_text = "\n".join(f"{indent}{line}" for line in wrapped_text.split("\n"))
    console.print(wrapped_text)
    console.print("")

def display_comments(story: dict, max_comments: int = None) -> None:
    """
    Interactive display of top-level comments for a story.
    Users can navigate parent comments using arrow keys and press Enter to expand comment threads.
    By default, a limited number of parent comments (5-10) are loaded based on screen space,
    or a custom limit can be specified via the --comments option.
    """
    parent_ids = story.get("kids", [])
    console.print(f"\n[bold]Comments for: {story.get('title', 'Unknown Story')}[/bold]\n")
    if not parent_ids:
        console.print("No comments yet.")
        return

    # Determine number of parent comments to display
    if max_comments is not None:
        # Use user-specified limit
        parent_ids = parent_ids[:max_comments]
    else:
        # Limit based on terminal size (between 5 and 10)
        _, rows = get_terminal_size()
        max_parents = max(5, min(10, rows - 5))
        parent_ids = parent_ids[:max_parents]

    # Pre-fetch parent comments for summaries
    parent_comments = []
    for cid in parent_ids:
        try:
            comment = get_item(cid)
            if comment and "deleted" not in comment and "dead" not in comment:
                parent_comments.append(comment)
        except Exception:
            pass

    def read_single_keypress():
        import sys, termios, tty
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

    def get_key():
        key = read_single_keypress()
        if key == "\x1b":
            # Arrow keys start with ESC sequence
            next1 = read_single_keypress()
            if next1 == "[":
                next2 = read_single_keypress()
                if next2 == "A":
                    return "UP"
                elif next2 == "B":
                    return "DOWN"
            return None
        elif key in ("\r", "\n"):
            return "ENTER"
        elif key.lower() == "q":
            return "QUIT"
        elif key.lower() == "b":
            return "BACK"
        return None

    def strip_html_tags(text: str) -> str:
        return re.sub(r"<[^>]+>", "", text)

    def get_summary_text(comment: dict, length: int = 80) -> str:
        import html
        text = html.unescape(comment.get("text", "") or "")
        text = strip_html_tags(text).replace("\n", " ")
        return truncate_text(text, length)

    def expand_comment_tree(comment):
        # Flatten the comment thread into lines for interactive scrolling
        lines: List[str] = []
        import html

        def collect(cmt: dict, depth: int):
            if not cmt or "deleted" in cmt or "dead" in cmt:
                return
            author = cmt.get("by", "unknown")
            time_ago = format_time_ago(cmt.get("time", 0))
            indent = "  " * depth
            header = f"{indent}[bold]{author}[/bold] {time_ago}"
            lines.append(header)
            # Process and wrap text
            text = html.unescape(cmt.get("text", "") or "")
            text = text.replace("<p>", "\n\n").replace("</p>", "")
            text = strip_html_tags(text)
            cols, _ = get_terminal_size()
            wrap_width = min(100, cols - len(indent) - 5)
            wrapped = textwrap.fill(text, width=wrap_width)
            for ln in wrapped.split("\n"):
                lines.append(f"{indent}{ln}")
            lines.append("")
            for kid in cmt.get("kids", []):
                try:
                    child = get_item(kid)
                    collect(child, depth + 1)
                except Exception:
                    continue

        collect(comment, 0)
        # Interactive scroll through the collected lines
        offset = 0
        _, rows = get_terminal_size()
        # Reserve one line for instructions
        view_height = max(rows - 1, 1)
        max_offset = max(len(lines) - view_height, 0)
        while True:
            clear_screen()
            for ln in lines[offset: offset + view_height]:
                console.print(ln)
            console.print("[grey]Use ↑/↓ to scroll, any other key to return[/grey]")
            key = get_key()
            if key == "UP":
                offset = max(0, offset - 1)
            elif key == "DOWN":
                offset = min(max_offset, offset + 1)
            else:
                break

    # Interactive navigation loop
    selected = 0
    while True:
        clear_screen()
        console.print(f"[bold]Comments for: {story.get('title', 'Unknown Story')}[/bold]")
        console.print("[grey]Use ↑/↓ to navigate, Enter to expand, b to go back, q to quit[/grey]\n")
        for idx, comment in enumerate(parent_comments):
            author = comment.get("by", "unknown")
            time_ago = format_time_ago(comment.get("time", 0))
            summary = get_summary_text(comment)
            prefix = "→" if idx == selected else "  "
            console.print(f"{prefix} [{idx+1}] {author} {time_ago}: {summary}")
        key = get_key()
        if key == "UP":
            selected = (selected - 1) % len(parent_comments)
        elif key == "DOWN":
            selected = (selected + 1) % len(parent_comments)
        elif key == "ENTER":
            expand_comment_tree(parent_comments[selected])
        elif key in ("QUIT", "BACK"):
            break

def clear_screen():
    """Clear the terminal screen based on OS."""
    os.system('cls' if os.name == 'nt' else 'clear')

def show_navigation_menu(story_type: str, page: int, total_pages: int, story_count: int) -> str:
    """Show navigation menu and return user command."""
    console.print("\n--- Navigation ---")
    console.print(f"Page {page}/{total_pages} ({story_count} stories total)")
    console.print("[n] Next page | [p] Previous page | [#] Select story | [r] Refresh | [q] Quit")
    return Prompt.ask("Enter command", default="n")

def handle_story_viewing(story: dict, max_comments: int = None) -> None:
    """Display a story followed by its comments.

    Once the user exits the comment view we immediately return to the caller
    (i.e. the main stories list) instead of going through an extra submenu.
    """

    clear_screen()
    display_story(story)
    display_comments(story, max_comments)

    # Returning here goes straight back to the main list – no extra submenu.

def browse_stories(story_type: str, stories_per_page: int = None) -> None:
    """Browse stories with pagination and interactive navigation."""
    if stories_per_page is None:
        # Dynamically calculate stories per page based on terminal size
        stories_per_page = calculate_stories_per_page()
    
    with console.status(f"Fetching {story_type} stories..."):
        story_ids = get_story_ids(story_type)
        total_stories = len(story_ids)
    
    current_page = 1
    total_pages = (total_stories + stories_per_page - 1) // stories_per_page
    
    while True:
        # Recalculate stories per page in case terminal has been resized
        if stories_per_page == calculate_stories_per_page():
            # Only recalculate total pages if the stories per page value changed
            pass
        else:
            stories_per_page = calculate_stories_per_page()
            total_pages = (total_stories + stories_per_page - 1) // stories_per_page
            # Adjust current page if needed
            current_page = min(current_page, total_pages)
        
        clear_screen()
        start_idx = (current_page - 1) * stories_per_page
        end_idx = min(start_idx + stories_per_page, total_stories)
        
        # Fetch and display current page of stories
        stories = []
        with console.status(f"Loading page {current_page}..."):
            for story_id in story_ids[start_idx:end_idx]:
                try:
                    story = get_item(story_id)
                    if story and story.get("type") == "story":
                        stories.append(story)
                except Exception as e:
                    console.print(f"Error fetching story {story_id}: {e}")
        
        columns, _ = get_terminal_size()
        title = f"{story_type.capitalize()} Stories (Page {current_page}/{total_pages})"
        padding = max(0, (columns - len(title) - 2) // 2)
        centered_title = " " * padding + title
        
        console.print(f"\n[bold]{centered_title}[/bold]\n")
        display_stories(stories)
        
        # Show navigation menu
        command = show_navigation_menu(story_type, current_page, total_pages, total_stories)
        
        # Process navigation command
        if command.lower() == 'n':
            if current_page < total_pages:
                current_page += 1
        elif command.lower() == 'p':
            if current_page > 1:
                current_page -= 1
        elif command.lower() == 'r':
            # Refresh the current page
            cache.clear()
            with console.status(f"Refreshing {story_type} stories..."):
                story_ids = get_story_ids(story_type)
                total_stories = len(story_ids)
                total_pages = (total_stories + stories_per_page - 1) // stories_per_page
        elif command.lower() == 'q':
            break
        elif command.isdigit():
            idx = int(command)
            if 1 <= idx <= len(stories):
                handle_story_viewing(stories[idx-1])
            else:
                console.print(f"[red]Invalid story number. Choose between 1 and {len(stories)}.[/red]")

@app.command()
def top(limit: int = None) -> None:
    """Show top stories from Hacker News with interactive browsing."""
    browse_stories("top", limit)

@app.command()
def new(limit: int = None) -> None:
    """Show new stories from Hacker News with interactive browsing."""
    browse_stories("new", limit)

@app.command()
def best(limit: int = None) -> None:
    """Show best stories from Hacker News with interactive browsing."""
    browse_stories("best", limit)

@app.command()
def story(
    item_id: int,
    comments: Optional[int] = typer.Option(
        None,
        "--comments",
        "-c",
        help="Number of top-level comments to display.",
    ),
) -> None:
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
    
    handle_story_viewing(story, comments)

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
    
    # Automatically open in browser based on configuration
    if get_config_value("open_links_in_browser", True):
        webbrowser.open(f"{HN_WEB_URL}/user?id={username}")
    else:
        # Ask if user wants to open in browser when automatic opening is disabled
        if typer.confirm("\nOpen user profile in browser?"):
            webbrowser.open(f"{HN_WEB_URL}/user?id={username}")

@app.command()
def search(query: str, limit: int = None) -> None:
    """Search for stories on Hacker News.
    
    Note: This uses a simple search by fetching top stories and filtering locally.
    For a more comprehensive search, consider using the Algolia HN Search API.
    """
    if limit is None:
        # Dynamically calculate stories per page based on terminal size
        limit = calculate_stories_per_page()
        
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
            if len(matching_stories) >= 100:  # Limit to 100 matches max for pagination
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
    
    if not matching_stories:
        console.print(f"\n[bold]Search Results for '{query}'[/bold]\n")
        console.print("No matching stories found.")
        return
        
    # Display stories with interactive browsing
    current_page = 1
    stories_per_page = calculate_stories_per_page()
    total_stories = len(matching_stories)
    total_pages = (total_stories + stories_per_page - 1) // stories_per_page
    
    while True:
        # Recalculate stories per page in case terminal has been resized
        if stories_per_page == calculate_stories_per_page():
            # Only recalculate total pages if the stories per page value changed
            pass
        else:
            stories_per_page = calculate_stories_per_page()
            total_pages = (total_stories + stories_per_page - 1) // stories_per_page
            # Adjust current page if needed
            current_page = min(current_page, total_pages)
            
        clear_screen()
        start_idx = (current_page - 1) * stories_per_page
        end_idx = min(start_idx + stories_per_page, total_stories)
        
        columns, _ = get_terminal_size()
        title = f"Search Results for '{query}' (Page {current_page}/{total_pages})"
        padding = max(0, (columns - len(title) - 2) // 2)
        centered_title = " " * padding + title
        
        console.print(f"\n[bold]{centered_title}[/bold]\n")
        display_stories(matching_stories[start_idx:end_idx])
        
        # Show navigation menu
        command = show_navigation_menu("search", current_page, total_pages, total_stories)
        
        # Process navigation command
        if command.lower() == 'n':
            if current_page < total_pages:
                current_page += 1
        elif command.lower() == 'p':
            if current_page > 1:
                current_page -= 1
        elif command.lower() == 'r':
            # Just stay on the same page since search results don't change
            pass
        elif command.lower() == 'q':
            break
        elif command.isdigit():
            idx = int(command)
            if 1 <= idx <= len(matching_stories[start_idx:end_idx]):
                handle_story_viewing(matching_stories[start_idx + idx - 1])
            else:
                console.print(f"[red]Invalid story number. Choose between 1 and {len(matching_stories[start_idx:end_idx])}.[/red]")

@app.command()
def open(story_id: int) -> None:
    """Open a story in the web browser."""
    url = f"{HN_WEB_URL}/item?id={story_id}"
    if get_config_value("open_links_in_browser", True):
        webbrowser.open(url)
        console.print(f"Opening story {story_id} in browser...")
    else:
        if typer.confirm("Open story in browser?"):
            webbrowser.open(url)
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
            
            # Add additional information about adaptive display
            table.add_row("Terminal Size", f"{get_terminal_size()[0]}x{get_terminal_size()[1]}")
            table.add_row("Current Stories per Page", str(calculate_stories_per_page()))
            
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
