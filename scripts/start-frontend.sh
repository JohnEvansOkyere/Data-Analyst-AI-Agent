#!/bin/bash

# VexaAI Frontend Startup Script

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🎨 Starting VexaAI Frontend Server${NC}"
echo ""

# Navigate to frontend directory
cd "$(dirname "$0")/../frontend" || exit

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}📦 Installing dependencies...${NC}"
    npm install
fi

# Check if port 3000 is already in use
if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null ; then
    echo -e "${YELLOW}⚠️  Port 3000 is already in use${NC}"
    echo ""
    echo "Options:"
    echo "  1. Stop the existing process: kill \$(lsof -ti:3000)"
    echo "  2. Use the already running server"
    echo ""
    read -p "Kill existing process and restart? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}Stopping existing server...${NC}"
        kill $(lsof -ti:3000) 2>/dev/null
        sleep 2
    else
        echo -e "${GREEN}Using existing server on http://localhost:3000${NC}"
        exit 0
    fi
fi

# Start Next.js development server
echo -e "${GREEN}Starting Next.js development server...${NC}"
echo -e "${YELLOW}Frontend will be available at: http://localhost:3000${NC}"
echo ""

npm run dev
