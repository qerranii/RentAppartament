#!/bin/bash

# ApartmentForRent - Quick Start Script
# This script provides a guided setup experience

set -e

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║         🏠 ApartmentForRent - Complete Setup Guide 🏠          ║"
echo "║                 AI-Powered Rental Price Platform               ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check requirements
echo "${BLUE}📋 Checking requirements...${NC}"
echo ""

if ! command -v docker &> /dev/null; then
    echo "${RED}✗ Docker not found${NC}"
    echo "  Please install Docker: https://www.docker.com/products/docker-desktop"
    exit 1
fi
echo "${GREEN}✓ Docker installed${NC} ($(docker --version | cut -d' ' -f3))"

if ! command -v docker-compose &> /dev/null; then
    echo "${RED}✗ Docker Compose not found${NC}"
    echo "  Please install Docker Compose"
    exit 1
fi
echo "${GREEN}✓ Docker Compose installed${NC}"

echo ""
echo "${BLUE}📂 Project Structure${NC}"
echo ""

# Verify key files
files=(
    "docker-compose.yml"
    "backend/Dockerfile"
    "backend/requirements.txt"
    "frontend/Dockerfile"
    "frontend/package.json"
    "nginx/nginx.conf"
    ".env"
    "rental_price_model.pkl"
)

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "${GREEN}✓${NC} $file"
    else
        echo "${RED}✗${NC} $file (missing!)"
    fi
done

echo ""
echo "${BLUE}🚀 Starting Application${NC}"
echo ""

# Check if services are already running
if [ "$(docker-compose ps -q 2>/dev/null | wc -l)" -gt 0 ]; then
    echo "${YELLOW}⚠ Some containers are already running${NC}"
    read -p "  Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "  Aborted."
        exit 1
    fi
fi

echo "  Building and starting services..."
echo "  (This may take 2-5 minutes on first run)"
echo ""

docker-compose up --build -d

# Wait for services to be healthy
echo ""
echo "${BLUE}⏳ Waiting for services to be healthy...${NC}"
echo ""

services=("postgres" "redis" "rabbitmq" "backend" "frontend")
max_attempts=30
attempt=1

while [ $attempt -le $max_attempts ]; do
    echo "  Attempt $attempt/$max_attempts..."
    
    if docker-compose exec -T postgres pg_isready -U user &>/dev/null 2>&1 && \
       docker-compose exec -T redis redis-cli ping &>/dev/null 2>&1 && \
       curl -s http://localhost:8000/health &>/dev/null && \
       curl -s http://localhost:3000 &>/dev/null; then
        echo "${GREEN}✓ All services are healthy!${NC}"
        break
    fi
    
    sleep 3
    attempt=$((attempt + 1))
done

if [ $attempt -gt $max_attempts ]; then
    echo "${YELLOW}⚠ Services may still be starting. Check logs with: docker-compose logs -f${NC}"
fi

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                    ✅ Setup Complete! ✅                        ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

echo "${GREEN}URLs:${NC}"
echo "  🌐 Frontend:      http://localhost:3000"
echo "  📚 API Docs:      http://localhost:8000/docs"
echo "  💻 API Base:      http://localhost:8000"
echo "  🐰 RabbitMQ:      http://localhost:15672 (guest/guest)"
echo ""

echo "${YELLOW}Next Steps:${NC}"
echo "  1. Open http://localhost:3000 in your browser"
echo "  2. Register a new account"
echo "  3. Create your first prediction!"
echo ""

echo "${GREEN}Useful Commands:${NC}"
echo "  View logs:        docker-compose logs -f backend"
echo "  Stop services:    docker-compose down"
echo "  Full reset:       docker-compose down -v && docker-compose up --build"
echo "  Shell in backend: docker-compose exec backend bash"
echo ""

echo "${BLUE}Documentation:${NC}"
echo "  Full Guide:       README.md"
echo "  Deployment:       DEPLOYMENT.md"
echo "  Project Info:     PROJECT_SUMMARY.md"
echo ""

echo "${GREEN}🎉 Enjoy ApartmentForRent!${NC}"
echo ""
