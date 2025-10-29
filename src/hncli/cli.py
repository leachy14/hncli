#!/usr/bin/env python3
"""
HackerNews CLI - A command-line interface for browsing Hacker News
"""

import typer
import webbrowser
from typing import Optional
import inspect
import click

from rich.console import Console

from hncli import config, cache
from hncli.errors import APIRequestError
from hncli.api import get_story_ids, get_item, get_user, get_config_value, HN_WEB_URL
from hncli.formatters import (
    display_story,
    display_stories,
    handle_story_viewing,
    show_navigation_menu,
    clear_screen,
    get_terminal_size,
    calculate_stories_per_page,
    format_time_ago,
)
from rich.panel import Panel
from rich.table import Table

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

# Also patch TyperArgument if it exists
try:
    from typer.core import TyperArgument
    if hasattr(TyperArgument, 'make_metavar'):
        # TyperArgument.make_metavar doesn't accept ctx, but it may be called with ctx in Click 8.2+
        _original_typer_make_metavar = TyperArgument.make_metavar

        def _patched_typer_make_metavar(self, ctx: Optional[click.Context] = None) -> str:
            # Call the original without ctx (it doesn't use it)
            return _original_typer_make_metavar(self)

        TyperArgument.make_metavar = _patched_typer_make_metavar  # type: ignore[assignment]
except ImportError:
    pass

app = typer.Typer(help="Hacker News CLI")
console = Console()


def browse_stories(story_type: str, stories_per_page: int = None) -> None:
    """Browse stories with pagination and interactive navigation."""
    if stories_per_page is None:
        # Dynamically calculate stories per page based on terminal size
        stories_per_page = calculate_stories_per_page()

    with console.status(f"Fetching {story_type} stories..."):
        try:
            story_ids = get_story_ids(story_type)
            total_stories = len(story_ids)
        except APIRequestError as e:
            console.print(f"Error fetching {story_type} stories: {e}")
            return

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
                except APIRequestError as e:
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
                try:
                    story_ids = get_story_ids(story_type)
                    total_stories = len(story_ids)
                    total_pages = (total_stories + stories_per_page - 1) // stories_per_page
                except APIRequestError as e:
                    console.print(f"Error refreshing {story_type} stories: {e}")
                    continue
        elif command.lower() == 'q':
            break
        elif command.isdigit():
            idx = int(command)
            if 1 <= idx <= len(stories):
                handle_story_viewing(stories[idx-1], get_item_func=get_item)
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
        except APIRequestError as e:
            console.print(f"Error fetching story {item_id}: {e}")
            return

    handle_story_viewing(story, comments, get_item_func=get_item)


@app.command()
def user(username: str) -> None:
    """Show a user profile."""
    with console.status(f"Fetching user {username}..."):
        try:
            user_data = get_user(username)
            if not user_data:
                console.print(f"User {username} not found.")
                return
        except APIRequestError as e:
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
def search(query: str, limit: Optional[int] = typer.Option(None, "--limit", "-l", help="Maximum number of results to display")) -> None:
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
            except APIRequestError as e:
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
            except APIRequestError:
                # Silently ignore errors during search
                pass

        if limit:
            matching_stories = matching_stories[:limit]

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
                handle_story_viewing(matching_stories[start_idx + idx - 1], get_item_func=get_item)
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
def config_get(key: Optional[str] = typer.Argument(None)) -> None:
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
