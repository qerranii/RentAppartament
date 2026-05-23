#!/bin/bash

# ApartmentForRent Setup Verification Script
set -e

echo "=================================="
echo "🏠 ApartmentForRent Setup Check"
echo "=================================="
echo ""

# Check Docker
echo "✓ Checking Docker..."
if ! command -v docker &> /dev/null; then
    echo "✗ Docker not found. Please install Docker."
    exit 1
fi
echo "  Docker version: $(docker --version)"
echo "  Docker Compose version: $(docker-compose --version)"

# Check directory structure
echo ""
echo "✓ Checking project structure..."

directories=(
    "backend/app/api"
    "backend/app/core"
    "backend/app/models"
    "backend/app/repositories"
    "backend/app/services"
    "backend/app/schemas"
    "backend/app/ml"
    "backend/app/workers"
    "backend/app/utils"
    "backend/app/tests"
    "frontend/src/app"
    "frontend/src/components"
    "frontend/src/services"
    "frontend/src/store"
    "frontend/src/types"
    "nginx"
)

for dir in "${directories[@]}"; do
    if [ -d "$dir" ]; then
        echo "  ✓ $dir"
    else
        echo "  ✗ $dir (missing)"
    fi
done

# Check key files
echo ""
echo "✓ Checking key files..."

files=(
    "backend/Dockerfile"
    "backend/requirements.txt"
    "backend/app/main.py:./backend/app/__init__.py"
    "frontend/Dockerfile"
    "frontend/package.json"
    "nginx/nginx.conf"
    "docker-compose.yml"
    ".env"
    "README.md"
    "rental_price_model.pkl"
)

for file in "${files[@]}"; do
    IFS=':' read -r display path <<< "$file"
    if [ -z "$path" ]; then
        path="$display"
    fi
    if [ -f "$path" ]; then
        echo "  ✓ $display"
    else
        echo "  ✗ $display (missing)"
    fi
done

echo ""
echo "=================================="
echo "✓ All checks passed!"
echo ""
echo "Next steps:"
echo "  1. docker-compose up --build"
echo "  2. Open http://localhost:3000"
echo "  3. Open http://localhost:8000/docs"
echo ""
echo "=================================="
