# HackerNews CLI

A command-line interface for browsing Hacker News.

## Features

- Browse top/new/best stories from Hacker News
- Read comments on stories
- Search for stories
- View user profiles
- Configurable settings
- Built-in caching for improved performance

## Quick Start

```bash
# Clone the repository
git clone https://github.com/yourusername/hncli.git
cd hncli

# Run the all-in-one setup script
./setup.sh

# Source your shell configuration (if you added the 'hn' shortcut)
source ~/.zshrc  # For Zsh users
# or
source ~/.bashrc  # For Bash users

# Start using the CLI
hn top         # Show top stories
hn new         # Show new stories
hn search ai   # Search for AI-related stories
```

## Installation

Our all-in-one setup script takes care of everything:

1. Creates a Python virtual environment
2. Installs all dependencies
3. Sets up shell integration for Bash or Zsh
4. Adds the `hn` command to your shell

Just run:

```bash
./setup.sh
```

The script will detect your shell and guide you through the setup process.

## Usage

### Using the `hn` command

If you added the shell shortcut during setup:

```bash
# View top stories
hn top

# View new stories with specific limit
hn new --limit 20

# View best stories
hn best

# View a specific story with comments
hn story <id>

# Search for stories
hn search "python"

# View user profile
hn user <username>
```

### Using the run script directly

If you prefer not to add the shortcut:

```bash
# View top stories
./run-hncli.sh top

# View new stories with specific limit
./run-hncli.sh new --limit 20

# And so on...
```

### Manual virtual environment activation

For development or if you prefer manual control:

```bash
# Activate the virtual environment
source venv/bin/activate

# Run commands directly with the Python script
./hncli top
./hncli new --limit 20
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
- `stories_per_page`: Number of stories to display (default: 10)
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
source venv/bin/activate

# Make your code changes

# Test your changes directly
./hncli top
```

## License

MIT 