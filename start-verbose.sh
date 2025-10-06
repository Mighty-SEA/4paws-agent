#!/bin/bash

# Start 4Paws Agent with verbose pnpm output

echo "========================================"
echo "4Paws Agent - Verbose Mode"
echo "========================================"
echo ""
echo "This mode shows detailed pnpm output"
echo "during dependency installation."
echo ""
echo "Useful for:"
echo "  - Troubleshooting slow installations"
echo "  - Seeing download progress"
echo "  - Debugging package issues"
echo ""
echo "========================================"
echo ""

# Set verbose mode
export PNPM_VERBOSE=1
export VERBOSE=1

# Start agent
python3 agent.py "$@"

