#!/bin/bash

# Backup the original package.json
cp package.json package.json.backup

# Replace with the new package.json
cp package.json.new package.json

echo "package.json has been updated. A backup of the original file was saved as package.json.backup."
