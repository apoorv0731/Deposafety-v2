#!/bin/bash
# DepoSafety V2 - Deployment Script
# Deploys to Railway (backend) and Vercel (frontend)

set -e

echo "🚀 DepoSafety V2 - Deployment"
echo "=============================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Parse arguments
DEPLOY_BACKEND=false
DEPLOY_FRONTEND=false
DEPLOY_ALL=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --backend)
            DEPLOY_BACKEND=true
            shift
            ;;
        --frontend)
            DEPLOY_FRONTEND=true
            shift
            ;;
        --all)
            DEPLOY_ALL=true
            shift
            ;;
        --help|-h)
            echo "Usage: ./deploy.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --backend    Deploy backend to Railway"
            echo "  --frontend   Deploy frontend to Vercel"
            echo "  --all        Deploy both backend and frontend"
            echo "  --help, -h   Show this help message"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

if [ "$DEPLOY_ALL" = true ]; then
    DEPLOY_BACKEND=true
    DEPLOY_FRONTEND=true
fi

if [ "$DEPLOY_BACKEND" = false ] && [ "$DEPLOY_FRONTEND" = false ]; then
    echo -e "${YELLOW}No deployment target specified. Use --backend, --frontend, or --all${NC}"
    exit 1
fi

# Check prerequisites
check_cli() {
    if ! command -v $1 &> /dev/null; then
        echo -e "${RED}❌ $1 CLI is not installed${NC}"
        echo "Install from: $2"
        return 1
    fi
    echo -e "${GREEN}✅ $1 CLI installed${NC}"
    return 0
}

echo ""
echo "📋 Checking deployment tools..."

if [ "$DEPLOY_BACKEND" = true ]; then
    check_cli "railway" "https://docs.railway.app/develop/cli" || exit 1
fi

if [ "$DEPLOY_FRONTEND" = true ]; then
    check_cli "vercel" "https://vercel.com/download" || exit 1
fi

# Verify environment variables
echo ""
echo "🔐 Checking environment variables..."

if [ "$DEPLOY_BACKEND" = true ]; then
    if [ -z "$RAILWAY_TOKEN" ]; then
        echo -e "${YELLOW}⚠️  RAILWAY_TOKEN not set. You may need to login manually.${NC}"
    fi
fi

if [ "$DEPLOY_FRONTEND" = true ]; then
    if [ -z "$VERCEL_TOKEN" ]; then
        echo -e "${YELLOW}⚠️  VERCEL_TOKEN not set. You may need to login manually.${NC}"
    fi
fi

# Deploy Backend
deploy_backend() {
    echo ""
    echo -e "${BLUE}📦 Deploying Backend to Railway...${NC}"
    
    cd ../backend
    
    # Check if linked to Railway project
    if ! railway status &> /dev/null; then
        echo "Linking to Railway project..."
        railway link
    fi
    
    # Deploy
    railway up --detach
    
    echo -e "${GREEN}✅ Backend deployed to Railway${NC}"
    echo ""
    echo "View logs: railway logs"
    echo "Open app: railway open"
    
    cd ../infrastructure
}

# Deploy Frontend
deploy_frontend() {
    echo ""
    echo -e "${BLUE}🌐 Deploying Frontend to Vercel...${NC}"
    
    cd ../frontend
    
    # Check if linked to Vercel project
    if ! vercel status &> /dev/null; then
        echo "Linking to Vercel project..."
        vercel link
    fi
    
    # Deploy to production
    vercel --prod
    
    echo -e "${GREEN}✅ Frontend deployed to Vercel${NC}"
    
    cd ../infrastructure
}

# Run deployments
if [ "$DEPLOY_BACKEND" = true ]; then
    deploy_backend
fi

if [ "$DEPLOY_FRONTEND" = true ]; then
    deploy_frontend
fi

echo ""
echo "=============================="
echo -e "${GREEN}✅ Deployment complete!${NC}"
echo ""

if [ "$DEPLOY_BACKEND" = true ]; then
    echo "Backend: https://deposafety-api.up.railway.app"
fi

if [ "$DEPLOY_FRONTEND" = true ]; then
    echo "Frontend: https://deposafety.vercel.app"
fi

echo ""
echo "Next steps:"
echo "  - Verify deployments are working"
echo "  - Check monitoring dashboards"
echo "  - Update DNS if needed"
