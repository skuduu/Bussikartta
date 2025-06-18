#!/bin/bash

OUTPUT="files_snapshot.txt"
MAX_BYTES=5000

# Collect file list first
FILE_LIST=$(git ls-files | grep -v "^${OUTPUT}$" | sort)

# Write header and file index
{
  echo "# Project Snapshot: Bussikartta"
  echo "# Git Commit: $(git rev-parse HEAD)"
  echo "# Branch: $(git rev-parse --abbrev-ref HEAD)"
  echo "# Generated: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
  echo ""
  echo "# Files in this snapshot:"
  echo "$FILE_LIST"
  echo ""
} > "$OUTPUT"

# Output content for each file
echo "$FILE_LIST" | while read -r file; do
  echo "=== FILE: $file ===" >> "$OUTPUT"
  if [ -f "$file" ]; then
    head -c "$MAX_BYTES" "$file" >> "$OUTPUT"
    FILE_SIZE=$(wc -c < "$file")
    if [ "$FILE_SIZE" -gt "$MAX_BYTES" ]; then
      echo -e "\n[... TRUNCATED]\n" >> "$OUTPUT"
    else
      echo -e "\n" >> "$OUTPUT"
    fi
  else
    echo "[SKIPPED: not a regular file]" >> "$OUTPUT"
    echo -e "\n" >> "$OUTPUT"
  fi
done

# Append ignored files (optional insight)
{
  echo -e "\n# Ignored Files:"
  git status --ignored --short | grep '^!!' || echo "(none)"
} >> "$OUTPUT"