#!/bin/bash

# Backup the original index.html
cp index.html index.html.backup

# Replace with the new index.html
cp new-index.html index.html

echo "Index.html has been updated. A backup of the original file was saved as index.html.backup."
