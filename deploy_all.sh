#!/bin/bash

# Exit on error
set -e

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "Starting deployment process..."

# Initialize an array to store deployed folders
deployed_folders=()

# Find all subdirectories and run deploy.sh if it exists
find "$SCRIPT_DIR" -mindepth 1 -maxdepth 1 -type d | while read -r dir; do
    deploy_script="$dir/deploy.sh"
    if [ -f "$deploy_script" ]; then
        folder_name="$(basename "$dir")"
        echo "Deploying in $folder_name..."
        cd "$dir" && ./deploy.sh
        cd "$SCRIPT_DIR"
        deployed_folders+=("$folder_name")
    fi
done

echo -e "\nDeployment Summary:"
echo "------------------"
if [ ${#deployed_folders[@]} -eq 0 ]; then
    echo "No folders were deployed."
else
    echo "Successfully deployed folders:"
    for folder in "${deployed_folders[@]}"; do
        echo "- $folder"
    done
fi 