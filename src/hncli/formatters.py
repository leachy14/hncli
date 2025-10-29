"""
Formatters module for Hacker News CLI.

This module contains all display and formatting functions for terminal output,
including story rendering, comment trees, and interactive navigation.
"""

import os
import re
import html
import shutil
import textwrap
from typing import List, Optional, Tuple
from datetime import datetime

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt
from rich.markup import escape

from hncli.models import Story, User

# Initialize console for this module
console = Console()

# HN web URL for links
HN_WEB_URL = "https://news.ycombinator.com"


def format_time_ago(timestamp: int) -> str:
    """Format a Unix timestamp as a human-readable time ago string."""
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


def clear_screen():
    """Clear the terminal screen based on OS."""
    os.system('cls' if os.name == 'nt' else 'clear')


def strip_html_tags(text: str) -> str:
    """Remove HTML tags from text."""
    return re.sub(r"<[^>]+>", "", text)


# ---------------------------------------------------------------------------
# Story presentation helpers
# ---------------------------------------------------------------------------

def display_story(story: Story, show_index: Optional[int] = None) -> None:
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


def display_stories(stories: List[Story]) -> None:
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


def display_comment(comment: Story, indent_level: int = 0) -> None:
    """Display a comment with appropriate indentation."""
    if comment.get("deleted") or comment.get("dead"):
        return

    author = comment.get("by", "unknown")
    time_ago = format_time_ago(comment.get("time", 0))
    text = comment.get("text", "")

    # Process HTML in comment text
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


def show_navigation_menu(story_type: str, page: int, total_pages: int, story_count: int) -> str:
    """Show navigation menu and return user command."""
    console.print("\n--- Navigation ---")
    console.print(f"Page {page}/{total_pages} ({story_count} stories total)")
    console.print("[n] Next page | [p] Previous page | [#] Select story | [r] Refresh | [q] Quit")
    return Prompt.ask("Enter command", default="n")


def display_comments(story: Story, max_comments: int = None, get_item_func=None) -> None:
    """
    Interactive display of top-level comments for a story.
    Users can navigate parent comments using arrow keys and press Enter to expand comment threads.
    By default, a limited number of parent comments (5-10) are loaded based on screen space,
    or a custom limit can be specified via the --comments option.

    Args:
        story: The story whose comments to display
        max_comments: Optional limit on number of top-level comments to show
        get_item_func: Function to fetch items by ID (required for fetching comment children)
    """
    if get_item_func is None:
        raise ValueError("get_item_func is required for display_comments")

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
            comment = get_item_func(cid)
            if comment and not comment.get("deleted") and not comment.get("dead"):
                parent_comments.append(comment)
        except Exception:
            pass

    def read_single_keypress():
        import sys
        import termios
        import tty
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

    def get_summary_text(comment: dict, length: int = 80) -> str:
        text = html.unescape(comment.get("text", "") or "")
        text = strip_html_tags(text).replace("\n", " ")
        return truncate_text(text, length)

    def expand_comment_tree(comment):
        # Flatten the comment thread into lines for interactive scrolling
        lines: List[str] = []

        def collect(cmt: Story, depth: int):
            if not cmt or cmt.get("deleted") or cmt.get("dead"):
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
                    child = get_item_func(kid)
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


def handle_story_viewing(story: Story, max_comments: int = None, get_item_func=None) -> None:
    """Display a story followed by its comments.

    Once the user exits the comment view we immediately return to the caller
    (i.e. the main stories list) instead of going through an extra submenu.

    Args:
        story: The story to display
        max_comments: Optional limit on number of top-level comments to show
        get_item_func: Function to fetch items by ID (required for fetching comment children)
    """
    clear_screen()
    display_story(story)
    display_comments(story, max_comments, get_item_func)

    # Returning here goes straight back to the main list – no extra submenu.
