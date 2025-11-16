#!/bin/bash

# VexaAI Backend Startup Script

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Starting VexaAI Backend Server${NC}"
echo ""

# Navigate to project root
cd "$(dirname "$0")/.." || exit

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ Virtual environment not found!${NC}"
    echo "Please create it first: python -m venv venv"
    exit 1
fi

# Check if port 8000 is already in use
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    echo -e "${YELLOW}⚠️  Port 8000 is already in use${NC}"
    echo ""
    echo "Options:"
    echo "  1. Stop the existing process: kill \$(lsof -ti:8000)"
    echo "  2. Use the already running server"
    echo ""
    read -p "Kill existing process and restart? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}Stopping existing server...${NC}"
        kill $(lsof -ti:8000) 2>/dev/null
        sleep 2
    else
        echo -e "${GREEN}Using existing server on http://localhost:8000${NC}"
        exit 0
    fi
fi

# Activate virtual environment and start server
echo -e "${GREEN}Starting FastAPI server...${NC}"
echo -e "${YELLOW}Backend will be available at: http://localhost:8000${NC}"
echo -e "${YELLOW}API Docs available at: http://localhost:8000/docs${NC}"
echo ""

source venv/bin/activate
uvicorn backend_api.main:app --host 0.0.0.0 --port 8000 --reload
