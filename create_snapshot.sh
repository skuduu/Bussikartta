#!/bin/bash

OUTPUT="files_snapshot.txt"

# Write header
{
  echo "# Project Snapshot: Bussikartta"
  echo "# Git Commit: $(git rev-parse HEAD)"
  echo "# Generated: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
  echo ""
} > "$OUTPUT"

# List all tracked files except the output file itself
git ls-files -z | grep -vzZ '^files_snapshot.txt$' | while IFS= read -r -d '' file; do
  echo "=== FILE: $file ===" >> "$OUTPUT"
  if [ -f "$file" ]; then
    cat "$file" >> "$OUTPUT"
  else
    echo "[SKIPPED: not a regular file]" >> "$OUTPUT"
  fi
  echo -e "\n" >> "$OUTPUT"
done
