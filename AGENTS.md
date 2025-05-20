# Hacker News CLI Project Guide

## Project Overview
This is a CLI tool for interacting with Hacker News. The project is written in Python and uses Typer for CLI functionality, Rich for terminal formatting, and Pydantic for data validation.

## Development Environment
- Python 3.8+ is required
- The project uses a virtual environment for dependency management
- Dependencies are managed through requirements.txt and pyproject.toml

## Code Structure
- `src/` - Contains the main source code
- `setup.sh` - Environment setup script
- `requirements.txt` - Python package dependencies
- `pyproject.toml` - Project metadata and build configuration

## Testing and Validation
- Run tests using: `python -m pytest`
- Type checking: `mypy src/`
- Linting: `flake8 src/`

## Code Style Guidelines
- Follow PEP 8 style guide
- Use type hints for all function parameters and return values
- Document all public functions and classes with docstrings
- Keep functions focused and single-purpose
- Use meaningful variable and function names

## Common Tasks
1. Adding new CLI commands:
   - Add the command function in the appropriate module
   - Register it in the main CLI group
   - Add tests for the new command
   - Update documentation if needed

2. Modifying existing functionality:
   - Ensure backward compatibility
   - Update tests to cover changes
   - Update documentation if needed

## Error Handling
- Use custom exceptions for domain-specific errors
- Provide clear error messages to users
- Log errors appropriately
- Handle network errors gracefully

## Documentation
- Keep README.md up to date
- Document all public APIs
- Include examples in docstrings
- Update help text for CLI commands

## Pull Request Guidelines
- Title format: `[Feature/Fix] Brief description`
- Include tests for new features
- Update documentation as needed
- Ensure all tests pass before submitting 