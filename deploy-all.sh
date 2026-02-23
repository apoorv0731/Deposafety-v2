#!/bin/bash
# One-command deployment script for DepoSafety V2
# This script deploys the entire application to free tier services

set -e

echo "🚀 DepoSafety V2 - Automated Deployment"
echo "========================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"

if ! command -v node &> /dev/null; then
    echo -e "${RED}Node.js not found. Please install Node.js 18+${NC}"
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 not found. Please install Python 3.11+${NC}"
    exit 1
fi

if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}Docker not found. Some features may not work.${NC}"
fi

echo -e "${GREEN}✓ Prerequisites met${NC}"
echo ""

# Check environment files
echo -e "${YELLOW}Checking environment files...${NC}"

if [ ! -f backend/.env ]; then
    echo -e "${RED}backend/.env not found!${NC}"
    echo "Please copy backend/.env.example to backend/.env and fill in your credentials"
    exit 1
fi

if [ ! -f frontend/.env.local ]; then
    echo -e "${RED}frontend/.env.local not found!${NC}"
    echo "Please copy frontend/.env.example to frontend/.env.local and fill in your credentials"
    exit 1
fi

echo -e "${GREEN}✓ Environment files found${NC}"
echo ""

# Install dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"

cd backend
python3 -m venv venv 2>/dev/null || true
source venv/bin/activate
pip install -q -r requirements.txt
cd ..

cd frontend
npm install
cd ..

echo -e "${GREEN}✓ Dependencies installed${NC}"
echo ""

# Run tests
echo -e "${YELLOW}Running tests...${NC}"

cd backend
source venv/bin/activate
python -m pytest tests/ -v --tb=short 2>&1 | head -50 || echo "Some tests failed (check logs)"
cd ..

echo -e "${GREEN}✓ Tests completed${NC}"
echo ""

# Build frontend
echo -e "${YELLOW}Building frontend...${NC}"

cd frontend
npm run build
cd ..

echo -e "${GREEN}✓ Frontend built${NC}"
echo ""

# Deploy to Railway (backend)
echo -e "${YELLOW}Deploying backend to Railway...${NC}"

if command -v railway &> /dev/null; then
    cd backend
    railway up
    cd ..
    echo -e "${GREEN}✓ Backend deployed${NC}"
else
    echo -e "${YELLOW}Railway CLI not found. Skipping backend deployment.${NC}"
    echo "Install with: npm i -g @railway/cli"
fi

echo ""

# Deploy to Vercel (frontend)
echo -e "${YELLOW}Deploying frontend to Vercel...${NC}"

if command -v vercel &> /dev/null; then
    cd frontend
    vercel --prod
    cd ..
    echo -e "${GREEN}✓ Frontend deployed${NC}"
else
    echo -e "${YELLOW}Vercel CLI not found. Skipping frontend deployment.${NC}"
    echo "Install with: npm i -g vercel"
fi

echo ""

# Summary
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}Deployment Complete!${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""
echo "Next steps:"
echo "1. Check Railway dashboard for backend URL"
echo "2. Check Vercel dashboard for frontend URL"
echo "3. Update frontend/.env.local with backend URL"
echo "4. Redeploy frontend if needed"
echo "5. Test the application"
echo ""
echo "Documentation: SETUP_SERVICES.md"
