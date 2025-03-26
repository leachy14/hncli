# Hacker News CLI for Zsh Users

## Using with Zsh

We've added an alias to your `~/.zshrc` file that makes it easy to use the Hacker News CLI. To start using it:

1. Close and reopen your terminal, or run:
   ```bash
   source ~/.zshrc
   ```

2. Now you can use the `hn` command directly:
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

## Zsh-specific Tips

### Add to your Zsh prompt

You can display Hacker News notifications in your Zsh prompt by adding this to your `~/.zshrc`:

```bash
# Add HN story count to prompt (example)
function hn_story_count() {
  local count=$(hn top --limit 1 | grep -o -E '\[\d+\]' | wc -l 2>/dev/null)
  if [[ $count -gt 0 ]]; then
    echo " %F{orange}(HN: $count)%f"
  fi
}

# Then add $(hn_story_count) to your PROMPT
```

### Create Zsh completions

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

compdef _hn_completion hn
```

Note: To use the completion, you'll need to make sure you have the `compdef` function available by loading `compinit` in your `~/.zshrc`.

## Enjoy Hacker News from your terminal!

The HN CLI is now fully integrated with your Zsh environment. Enjoy browsing Hacker News right from your terminal! 