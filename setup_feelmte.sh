#!/bin/bash

# Current directory (FeelMate)
ROOT="."

# Create main folders inside current directory
mkdir -p "$ROOT/pages"
mkdir -p "$ROOT/components"
mkdir -p "$ROOT/utils"
mkdir -p "$ROOT/public"

# Create empty files
touch "$ROOT/pages/_app.jsx"
touch "$ROOT/pages/index.jsx"
touch "$ROOT/pages/app.jsx"
touch "$ROOT/components/ChatBox.jsx"
touch "$ROOT/utils/api.js"
touch "$ROOT/package.json"

echo "Folders and files created inside $(pwd)"
