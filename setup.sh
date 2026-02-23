#!/bin/bash
# DepoSafety V2 - One-Command Setup
# Run this to set up the entire development environment

set -e

echo "🚀 DepoSafety V2 Setup"
echo "======================"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"

if ! command -v docker &> /dev/null; then
    echo -e "${RED}Docker not found. Installing...${NC}"
    curl -fsSL https://get.docker.com | sh
    sudo usermod -aG docker $USER
    echo -e "${GREEN}Docker installed. Please log out and back in, then re-run this script.${NC}"
    exit 0
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${YELLOW}Installing Docker Compose...${NC}"
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

if ! command -v node &> /dev/null; then
    echo -e "${YELLOW}Node.js not found. Please install Node.js 18+${NC}"
    echo "Visit: https://nodejs.org/"
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}Python 3 not found. Please install Python 3.11+${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Prerequisites met${NC}"

# Create environment files
echo ""
echo -e "${YELLOW}Setting up environment files...${NC}"

# Backend .env
if [ ! -f backend/.env ]; then
    cat > backend/.env << 'EOF'
# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/deposafety

# Security
SECRET_KEY=change-me-in-production-use-random-string
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# Supabase (optional, for production)
SUPABASE_URL=
SUPABASE_KEY=

# Cloudflare R2 (optional, for production)
R2_ACCESS_KEY=
R2_SECRET_KEY=
R2_ENDPOINT=
R2_BUCKET=deposafety

# Blockchain (Polygon Mumbai)
POLYGON_RPC=https://rpc-mumbai.maticvigil.com
CONTRACT_ADDRESS=
PRIVATE_KEY=

# Email (SendGrid)
SENDGRID_API_KEY=
FROM_EMAIL=noreply@deposafety.com

# Environment
ENVIRONMENT=development
DEBUG=True
EOF
    echo -e "${GREEN}✓ Created backend/.env${NC}"
fi

# Frontend .env
if [ ! -f frontend/.env.local ]; then
    cat > frontend/.env.local << 'EOF'
VITE_API_URL=http://localhost:8000
VITE_SUPABASE_URL=
VITE_SUPABASE_ANON_KEY=
EOF
    echo -e "${GREEN}✓ Created frontend/.env.local${NC}"
fi

echo ""
echo -e "${YELLOW}Installing dependencies...${NC}"

# Backend
cd backend
python3 -m venv venv 2>/dev/null || true
source venv/bin/activate
pip install -q -r requirements.txt
cd ..

# Frontend
cd frontend
npm install
cd ..

echo -e "${GREEN}✓ Dependencies installed${NC}"

# Create storage directories
echo ""
echo -e "${YELLOW}Creating storage directories...${NC}"
mkdir -p storage/uploads storage/models storage/reports
echo -e "${GREEN}✓ Storage directories created${NC}"

# Start services
echo ""
echo -e "${YELLOW}Starting services with Docker...${NC}"
docker-compose up -d db redis
echo -e "${GREEN}✓ Database and Redis started${NC}"

# Wait for database
echo ""
echo -e "${YELLOW}Waiting for database...${NC}"
sleep 5

# Run migrations
cd backend
source venv/bin/activate
alembic upgrade head 2>/dev/null || echo "No migrations to run"
cd ..

echo ""
echo -e "${GREEN}✓ Setup complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Edit backend/.env with your credentials"
echo "2. Edit frontend/.env.local with your API URL"
echo "3. Start backend: cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
echo "4. Start frontend: cd frontend && npm run dev"
echo "5. Or use Docker: docker-compose up"
echo ""
echo "Documentation: docs/README.md"
