#!/bin/bash
cd "$(dirname "$0")/.."
echo "Running NyxOS tests..."
python3 -m pytest tests/ -v
