#!/bin/bash

set -e 

VENV_DIR="venv"
PYTHON_VERSION="3.11"
REQUIREMENTS_FILE="requirements.txt"
UV_COMMAND="uv venv --clear --seed --python $PYTHON_VERSION $VENV_DIR"

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "uv not found."
    exit 1
fi

echo "Creating Python $PYTHON_VERSION venv..."
venv_output=$($UV_COMMAND 2>&1) || {
    echo "Failed to create virtual environment:"
    echo "$venv_output"
    exit 1
}
echo "Done!"

if [ -f "$REQUIREMENTS_FILE" ]; then
    echo "Installing dependencies..."
    "$VENV_DIR/bin/python" -m pip install -r "$REQUIREMENTS_FILE" &> /dev/null
else
    echo "⚠️  No $REQUIREMENTS_FILE found"
fi
echo "$venv_output" | tail -n 1