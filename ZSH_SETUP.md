# Hacker News CLI for Zsh Users

## Adding the `hn` shortcut to your Zsh

To make the Hacker News CLI available from anywhere in your terminal, add this to your `~/.zshrc` file:

```bash
# Add this to your ~/.zshrc file:
# Replace /path/to/hncli with the actual path to your HN CLI installation
HNCLI_PATH="/path/to/hncli"  # Change this to the actual path where you installed hncli

function hn() {
  $HNCLI_PATH/run-hncli.sh "$@"
}
```

You can add this automatically by running:

```bash
# Make sure to change this to the path where you installed the CLI
echo 'HNCLI_PATH="'$(pwd)'"' >> ~/.zshrc
echo 'function hn() {' >> ~/.zshrc
echo '  $HNCLI_PATH/run-hncli.sh "$@"' >> ~/.zshrc
echo '}' >> ~/.zshrc
```

After adding this to your `.zshrc`, either:
1. Open a new terminal window, or
2. Run `source ~/.zshrc` to load the changes in your current session

## Using the `hn` command

Now you can use the `hn` command directly from anywhere:

```bash
# View top stories
hn top

# View new stories with specific limit
hn new --limit 5

# View best stories
hn best

# View a specific story with comments
hn story <id>

# Search for stories
hn search "python"

# View user profile
hn user <username>

# View or modify configuration
hn config-get
hn config-set stories_per_page 10

# Clear cache
hn cache-clear
```

## Optional: Add Zsh completions

For better command completion, you can add this to your `~/.zshrc`:

```bash
# Generate completions for hn command
_hn_completion() {
  local -a commands
  commands=(
    'top:Show top stories from Hacker News'
    'new:Show new stories from Hacker News'
    'best:Show best stories from Hacker News'
    'story:Show a specific story and its comments'
    'user:Show a user profile'
    'search:Search for stories on Hacker News'
    'open:Open a story in the web browser'
    'config-get:Get current configuration settings'
    'config-set:Update a configuration setting'
    'config-reset:Reset configuration to defaults'
    'cache-clear:Clear the cache to fetch fresh data'
  )

  _describe 'command' commands
}

# Only run if you have compdef available (typical in Zsh with Oh-My-Zsh or similar)
compdef _hn_completion hn
```

## Enjoy Hacker News from your terminal!

The HN CLI is now accessible from anywhere in your terminal with the simple `hn` command. Enjoy browsing Hacker News right from your Zsh prompt! 