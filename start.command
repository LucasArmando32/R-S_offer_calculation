#!/bin/bash

# Go to the folder where this script lives
cd "$(dirname "$0")"

# Create venv if it doesn't exist yet
if [ ! -d "venv" ]; then
    echo "Einmalige Installation läuft..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Run the app
python asbestos_calc.py
