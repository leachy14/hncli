# HackerNews CLI

A command-line interface for browsing Hacker News.

## Features

- Browse top/new/best stories from Hacker News
- Interactive navigation with pagination
- Read comments on stories
- Search for stories
- View user profiles
- Configurable settings
- Built-in caching for improved performance
- VS Code integration
- Adaptive display that adjusts to terminal size

## Quick Start

```bash
# Clone the repository
git clone https://github.com/yourusername/hncli.git
cd hncli

# Run the minimal setup script
./setup.sh

# Start using the CLI
hn top         # Show top stories
hn new         # Show new stories
hn search ai   # Search for AI-related stories
```

## Installation

Our minimal setup script takes care of everything:

1. Creates a Python virtual environment
2. Installs the package in editable mode

Just run:

```bash
./setup.sh
```

## Usage

### Using the `hn` command

```bash
# View top stories
hn top

# View new stories with specific limit
hn new --limit 20

# View best stories
hn best

# Search for stories
hn search "python"

# View user profile
hn user <username>
```

### Interactive Navigation

The CLI now features an interactive navigation system:

- Browse through pages of stories with `n` (next) and `p` (previous)
- Select a story by typing its number (e.g., `1`, `2`, etc.)
- Refresh the current page with `r`
- Quit to the command line with `q`

When viewing a story:

- View comments with `c`
- Open in browser with `o`
- Go back to the stories list with `b`
- Quit to the command line with `q`

### Adaptive Display

The CLI automatically adjusts the number of stories displayed based on your terminal window size:

- Resize your terminal window to see more or fewer stories per page
- The application recalculates the optimal number of stories each time you navigate
- Comment display also adapts to available space
- Text wrapping adjusts to fit your terminal width
- Titles and headers are centered for better readability

You can see your current terminal size and the calculated number of stories per page by running:

```bash
hn config-get
```

### VS Code Integration

The project includes VS Code configurations for easy development and interactive usage:

1. **Launch Configurations**: Run the CLI directly from VS Code's Run panel:
   - Interactive browsing for Top, New, and Best stories
   - Interactive story viewing with comments
   - Interactive search functionality
   - Custom command runner with parameter selection

2. **Tasks**: Run CLI commands as VS Code tasks:
   - Press `Ctrl+Shift+B` to show available tasks
   - Choose from interactive browsing tasks for different story types
   - Search and view specific stories with interactive navigation

All VS Code run configurations and tasks support the new interactive navigation features, allowing you to:
- Browse through multiple pages of stories
- Select stories to view their details and comments
- Navigate back to story lists
- Refresh content as needed

To use these features:
1. Open the project in VS Code
2. Go to the Run and Debug panel (Ctrl+Shift+D)
3. Select a launch configuration from the dropdown
4. Press the play button or F5 to run

### Manual virtual environment activation

For development or if you prefer manual control:

```bash
# Activate the virtual environment
source .venv/bin/activate

# Run commands directly with the Python script
hn top
hn new --limit 20
```

## Configuration

The CLI is configurable through a simple configuration system:

```bash
# View all configuration settings
hn config-get

# View a specific setting
hn config-get stories_per_page

# Update a setting
hn config-set stories_per_page 20

# Reset to default configuration
hn config-reset
```

Available configuration options:
- `stories_per_page`: Number of stories to display per page (default: 10)
  - Note: The actual number displayed may be lower depending on terminal size
- `max_comment_depth`: Maximum depth of comments to display (default: 3)
- `open_links_in_browser`: Whether to automatically open links in browser (default: true)
- `color_theme`: Color theme to use (default: "default")
- `cache_timeout_minutes`: Cache timeout in minutes (default: 5)

## Cache Management

The CLI caches API requests to improve performance:

```bash
# Clear the cache to fetch fresh data
hn cache-clear
```

## Development

If you want to develop the CLI further:

```bash
# Activate the virtual environment
source .venv/bin/activate

# Make your code changes

# Test your changes directly
hn top
```

### VS Code Development Setup

The project includes VS Code settings to make development easier:

1. The Python interpreter is set to use the virtual environment automatically
2. Debug configurations are provided for running and testing
3. Tasks are configured for running the CLI directly

When you open the project in VS Code, it will:
- Recognize the virtual environment
- Use the correct Python interpreter
- Provide proper IntelliSense and code navigation

## License

MIT 