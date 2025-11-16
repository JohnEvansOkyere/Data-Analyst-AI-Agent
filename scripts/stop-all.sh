#!/bin/bash

# Stop all VexaAI servers

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🛑 Stopping VexaAI Servers${NC}"
echo ""

# Stop backend (port 8000)
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    echo -e "${YELLOW}Stopping backend server (port 8000)...${NC}"
    kill $(lsof -ti:8000) 2>/dev/null
    echo -e "${GREEN}✓ Backend stopped${NC}"
else
    echo -e "${YELLOW}Backend server not running${NC}"
fi

# Stop frontend (port 3000)
if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null ; then
    echo -e "${YELLOW}Stopping frontend server (port 3000)...${NC}"
    kill $(lsof -ti:3000) 2>/dev/null
    echo -e "${GREEN}✓ Frontend stopped${NC}"
else
    echo -e "${YELLOW}Frontend server not running${NC}"
fi

echo ""
echo -e "${GREEN}All servers stopped!${NC}"
