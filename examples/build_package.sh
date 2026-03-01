#!/bin/bash
# Example script to build the photorand package and verify the output

set -e

echo "Starting build process..."

# Navigate to the project root (assumed to be one level up from examples/)
cd "$(dirname "$0")/.."

# Build the package
python3 -m build

# Check if dist/ folder exists
if [ ! -d "dist" ]; then
	echo "Error: dist/ folder not found after build."
	exit 1
fi

# Check for .whl and .tar.gz files
WHL_COUNT=$(find dist -name "*.whl" | wc -l)
TAR_COUNT=$(find dist -name "*.tar.gz" | wc -l)

echo "Build artifacts found:"
ls -lh dist/

if [ "$WHL_COUNT" -gt 0 ] && [ "$TAR_COUNT" -gt 0 ]; then
	echo "Success: Valid package found in dist/ folder."
else
	echo "Error: Could not find both .whl and .tar.gz files in dist/ folder."
	exit 1
fi
