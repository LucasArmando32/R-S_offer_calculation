#!/bin/bash

# Go to the folder where this script lives
cd "$(dirname "$0")"

# Find a working Python (skip Xcode's broken one)
find_python() {
    for p in \
        "$HOME/opt/anaconda3/bin/python3" \
        "$HOME/opt/miniconda3/bin/python3" \
        "$HOME/anaconda3/bin/python3" \
        "$HOME/miniconda3/bin/python3" \
        "/opt/homebrew/bin/python3" \
        "/usr/local/bin/python3"; do
        if [ -x "$p" ]; then
            echo "$p"
            return
        fi
    done
    echo ""
}

PYTHON=$(find_python)

if [ -z "$PYTHON" ]; then
    echo "❌ Kein Python gefunden."
    echo "Bitte Python installieren: https://www.python.org/downloads/"
    read -p "Drücke Enter zum Schliessen..."
    exit 1
fi

echo "✅ Python: $PYTHON"

# Install dependencies if not already installed
"$PYTHON" -m pip install -r requirements.txt -q

# Run the app
"$PYTHON" asbestos_calc.py
