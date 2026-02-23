#!/bin/bash
# DepoSafety V2 - One-Command Setup Script
# Sets up local development environment

set -e

echo "🚀 DepoSafety V2 - Development Setup"
echo "====================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
check_prerequisite() {
    if ! command -v $1 &> /dev/null; then
        echo -e "${RED}❌ $1 is not installed${NC}"
        return 1
    else
        echo -e "${GREEN}✅ $1 installed${NC}"
        return 0
    fi
}

echo ""
echo "📋 Checking prerequisites..."
check_prerequisite "docker" || exit 1
check_prerequisite "docker-compose" || exit 1
check_prerequisite "node" || echo -e "${YELLOW}⚠️  Node.js not installed (needed for local dev outside Docker)${NC}"
check_prerequisite "npm" || echo -e "${YELLOW}⚠️  npm not installed${NC}"

# Create environment files
echo ""
echo "📝 Setting up environment files..."

if [ ! -f "../backend/.env" ]; then
    cat > ../backend/.env << 'EOF'
# Backend Environment Variables
NODE_ENV=development
PORT=3001

# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/deposafety
SUPABASE_URL=your_supabase_project_url
SUPABASE_SERVICE_KEY=your_supabase_service_role_key

# File Storage (Cloudflare R2)
R2_ENDPOINT=https://your_account_id.r2.cloudflarestorage.com
R2_ACCESS_KEY_ID=your_r2_access_key
R2_SECRET_ACCESS_KEY=your_r2_secret_key
R2_BUCKET_NAME=deposafety-uploads

# Security
JWT_SECRET=your_jwt_secret_key_change_in_production

# Frontend URL (for CORS)
FRONTEND_URL=http://localhost:3000
EOF
    echo -e "${GREEN}✅ Created backend/.env${NC}"
else
    echo -e "${YELLOW}⚠️  backend/.env already exists, skipping${NC}"
fi

if [ ! -f "../frontend/.env.local" ]; then
    cat > ../frontend/.env.local << 'EOF'
# Frontend Environment Variables
NEXT_PUBLIC_API_URL=http://localhost:3001
NEXT_PUBLIC_SUPABASE_URL=your_supabase_project_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
EOF
    echo -e "${GREEN}✅ Created frontend/.env.local${NC}"
else
    echo -e "${YELLOW}⚠️  frontend/.env.local already exists, skipping${NC}"
fi

# Create necessary directories
echo ""
echo "📁 Creating directories..."
mkdir -p ../backend/uploads
mkdir -p ../backend/logs
mkdir -p ../frontend/public/uploads
echo -e "${GREEN}✅ Directories created${NC}"

# Start infrastructure services
echo ""
echo "🐳 Starting Docker services..."
docker-compose up -d db redis
echo -e "${GREEN}✅ Database and Redis started${NC}"

# Wait for database
echo ""
echo "⏳ Waiting for database to be ready..."
sleep 5

# Check if database is ready
until docker-compose exec -T db pg_isready -U postgres > /dev/null 2>&1; do
    echo "Waiting for PostgreSQL..."
    sleep 2
done
echo -e "${GREEN}✅ Database is ready${NC}"

# Install backend dependencies
echo ""
echo "📦 Installing backend dependencies..."
cd ../backend
if [ -f "package.json" ]; then
    npm install
    echo -e "${GREEN}✅ Backend dependencies installed${NC}"
else
    echo -e "${YELLOW}⚠️  No package.json found in backend, skipping npm install${NC}"
fi

# Install frontend dependencies
echo ""
echo "📦 Installing frontend dependencies..."
cd ../frontend
if [ -f "package.json" ]; then
    npm install
    echo -e "${GREEN}✅ Frontend dependencies installed${NC}"
else
    echo -e "${YELLOW}⚠️  No package.json found in frontend, skipping npm install${NC}"
fi

# Return to infrastructure directory
cd ../infrastructure

echo ""
echo "====================================="
echo -e "${GREEN}✅ Setup complete!${NC}"
echo ""
echo "Next steps:"
echo "  1. Update environment variables in:"
echo "     - backend/.env"
echo "     - frontend/.env.local"
echo ""
echo "  2. Start development servers:"
echo "     docker-compose up -d     # Full stack with Docker"
echo "     # OR"
echo "     cd ../backend && npm run start:dev    # Backend only"
echo "     cd ../frontend && npm run dev         # Frontend only"
echo ""
echo "  3. Access the application:"
echo "     Frontend: http://localhost:3000"
echo "     Backend API: http://localhost:3001"
echo "     Database: localhost:5432"
echo ""
echo "  4. Setup Supabase and R2 (see DEPLOYMENT.md)"
echo ""
