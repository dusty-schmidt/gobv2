#!/bin/bash
# Simple entry point for the chatbot application

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Run the Python application
python3 "$SCRIPT_DIR/main.py" "$@"