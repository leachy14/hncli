#!/bin/bash
# HackerNews CLI Demo Script
# This script demonstrates the interactive features of the HackerNews CLI.

# Function to display step information
show_step() {
    clear
    echo "=========================================================="
    echo "  HackerNews CLI Interactive Demo"
    echo "=========================================================="
    echo ""
    echo "$1"
    echo ""
    echo "Press ENTER to continue..."
    read
}

# Ensure we're in the right directory
cd "$(dirname "$0")"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Step 1: Introduction
show_step "Welcome to the HackerNews CLI Interactive Demo!

This demo will showcase the interactive features of the HackerNews CLI,
including pagination, story selection, and comment viewing.

Let's get started!"

# Step 2: View Top Stories
show_step "First, let's browse the top stories.

You'll see a list of stories with numbers. You can:
- Press 'n' to see the next page
- Press 'p' to see the previous page
- Type a story number to select it
- Press 'r' to refresh the stories
- Press 'q' to quit

Try navigating through the pages with 'n' and 'p'."

./hncli.py top

# Step 3: Search for stories
show_step "Now, let's search for stories.

The CLI will search for stories matching your query and
display them with the same interactive navigation."

echo "Enter a search term (e.g. python, ai, web):"
read search_term

./hncli.py search "$search_term"

# Step 4: View a specific story
show_step "You can also view a specific story directly by its ID.

When viewing a story, you can:
- Press 'c' to view comments
- Press 'o' to open in browser
- Press 'b' to go back to stories
- Press 'q' to quit

Let's try viewing a popular story (ID: 38767026)."

./hncli.py story 38767026

# Step 5: Configuration
show_step "The CLI is configurable! You can change settings like:
- stories_per_page: Number of stories per page
- max_comment_depth: How many levels of comments to show

Let's look at the current configuration:"

./hncli.py config-get

# Final step
show_step "This concludes the HackerNews CLI Interactive Demo!

Try exploring more features:
- View user profiles: ./hncli.py user <username>
- Change settings: ./hncli.py config-set stories_per_page 20
- Clear cache: ./hncli.py cache-clear

Enjoy using the HackerNews CLI!"

# Deactivate virtual environment if we activated it
if [ -n "$VIRTUAL_ENV" ]; then
    deactivate
fi 