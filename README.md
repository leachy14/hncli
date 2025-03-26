# HackerNews CLI

A command-line interface for browsing Hacker News.

## Features

- Browse top/new/best stories from Hacker News
- Read comments on stories
- Search for stories
- View user profiles
- Configurable settings
- Built-in caching for improved performance

## Installation

### For Linux/macOS/WSL:

```bash
# Clone the repository
git clone https://github.com/yourusername/hncli.git
cd hncli

# Run the setup script (creates virtual environment and installs dependencies)
./setup.sh
```

## Usage

### For Zsh Users (Recommended)

We've created an alias and Zsh-specific enhancements for you. See [ZSH_SETUP.md](ZSH_SETUP.md) for details.

After running the setup and sourcing your `.zshrc`, you can simply use:

```bash
# View top stories
hn top

# View new stories with specific limit
hn new --limit 20

# View best stories
hn best

# And all other commands
```

### For WSL Users

The `run-hncli.sh` script handles activating the virtual environment for you:

```bash
# View top stories
./run-hncli.sh top

# View new stories with specific limit
./run-hncli.sh new --limit 20

# View best stories
./run-hncli.sh best

# And so on...
```

### Standard Usage (Requires Activating Virtual Environment)

Make sure the virtual environment is activated before running commands:

```bash
# First, activate the virtual environment
source venv/bin/activate  # On Linux/macOS/WSL
# or
. ./venv/bin/activate     # Alternative for some shells

# Then run commands:
./hncli top
./hncli new --limit 20
./hncli best
./hncli story <id>
./hncli search "search term"
./hncli user <username>
./hncli open <id>
```

## Configuration

The CLI is configurable through a simple configuration system:

```bash
# View all configuration settings
./run-hncli.sh config-get

# View a specific setting
./run-hncli.sh config-get stories_per_page

# Update a setting
./run-hncli.sh config-set stories_per_page 20

# Reset to default configuration
./run-hncli.sh config-reset
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
./run-hncli.sh cache-clear
```

## Development

If you want to develop the CLI further, you can:

```bash
# Activate the virtual environment
source venv/bin/activate

# Make your code changes

# Test your changes directly
./hncli top
```

## Shell Integration Tips

### Zsh Users
See [ZSH_SETUP.md](ZSH_SETUP.md) for detailed Zsh integration.

### Bash Users
You can create an alias in your `.bashrc` file:
```bash
echo 'alias hn="/path/to/hncli/run-hncli.sh"' >> ~/.bashrc
source ~/.bashrc
```

### PowerShell Users
If you're using PowerShell to launch WSL, you can create a function in your PowerShell profile:
```powershell
function hncli { wsl -e /path/to/hncli/run-hncli.sh $args }
```

## License

MIT 