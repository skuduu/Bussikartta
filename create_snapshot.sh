#!/bin/bash
OUTPUT="files_snapshot.txt"
echo "# Project Snapshot: Bussikartta" > $OUTPUT
echo "# Git Commit: $(git rev-parse HEAD)" >> $OUTPUT
echo "# Generated: $(date -u +"%Y-%m-%dT%H:%M:%SZ")" >> $OUTPUT
echo "" >> $OUTPUT

git ls-files --exclude-standard | while read -r file; do
  echo "=== FILE: $file ===" >> $OUTPUT
  cat "$file" >> $OUTPUT
  echo -e "\n" >> $OUTPUT
done