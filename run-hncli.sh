#!/bin/bash
# Wrapper script to run the Hacker News CLI
# Usage: ./run-hncli.sh [arguments]

python -m hncli.cli "$@"
