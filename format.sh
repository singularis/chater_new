#!/bin/bash

# Exit on error
set -e

echo "Running black..."
black .

echo "Running isort..."
isort .

echo "Formatting complete!" 