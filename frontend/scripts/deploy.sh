#!/bin/bash
# Vercel Deployment Script for CondoManager Frontend
# Usage: ./deploy.sh [options]
#   --prod    Deploy to production (default: preview)
#   --debug   Show verbose output

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}CondoManager Frontend Deploy Script${NC}"
echo "====================================="
echo ""

# Parse arguments
DEPLOY_MODE="preview"
DEBUG=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --prod|--production)
            DEPLOY_MODE="production"
            shift
            ;;
        --debug)
            DEBUG=true
            shift
            ;;
        --help|-h)
            echo "Usage: ./deploy.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --prod, --production    Deploy to production"
            echo "  --debug                 Show verbose output"
            echo "  --help, -h              Show this help"
            echo ""
            echo "Examples:"
            echo "  ./deploy.sh              # Deploy preview"
            echo "  ./deploy.sh --prod       # Deploy production"
            exit 0
            ;;
        *)
            echo -e "${YELLOW}Warning: Unknown option $1${NC}"
            shift
            ;;
    esac
done

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo -e "${RED}Error: package.json not found${NC}"
    echo "Please run this script from the frontend directory"
    exit 1
fi

echo -e "${BLUE}1. Checking dependencies...${NC}"

# Check for Vercel CLI
if ! command -v vercel &> /dev/null; then
    echo -e "${YELLOW}Vercel CLI not found. Installing...${NC}"
    npm install -g vercel
fi

# Check for environment variables
echo -e "${BLUE}2. Checking environment variables...${NC}"
if [ -f ".env.production" ]; then
    echo -e "${GREEN}✓ .env.production found${NC}"
    
    # Check if VITE_API_URL is set
    if grep -q "your-backend.onrender.com" .env.production; then
        echo -e "${YELLOW}⚠ VITE_API_URL contains placeholder values${NC}"
        echo "   Please update .env.production with your actual backend URL"
        echo "   Then run: cp .env.production .env.local"
        exit 1
    fi
else
    echo -e "${YELLOW}⚠ .env.production not found${NC}"
    echo "   Copy from template: cp .env.production.example .env.production"
    exit 1
fi

# Build locally first to catch errors
echo ""
echo -e "${BLUE}3. Running local build test...${NC}"
if npm run build 2>&1 | tee build.log; then
    echo -e "${GREEN}✓ Build successful${NC}"
    rm build.log
else
    echo -e "${RED}✗ Build failed${NC}"
    echo "   Check build.log for details"
    exit 1
fi

# Run tests
echo ""
echo -e "${BLUE}4. Running tests...${NC}"
if npm test -- --run 2>&1; then
    echo -e "${GREEN}✓ Tests passed${NC}"
else
    echo -e "${YELLOW}⚠ Some tests failed${NC}"
    read -p "Continue deployment anyway? (y/N): " continue
    if [[ ! $continue =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Deploy
echo ""
echo -e "${BLUE}5. Deploying to Vercel...${NC}"
echo "   Mode: $DEPLOY_MODE"

if [ "$DEBUG" = true ]; then
    VERCEL_FLAGS="--debug"
else
    VERCEL_FLAGS=""
fi

if [ "$DEPLOY_MODE" = "production" ]; then
    npx vercel --prod $VERCEL_FLAGS
else
    npx vercel $VERCEL_FLAGS
fi

echo ""
echo -e "${GREEN}✓ Deployment complete!${NC}"

# Show deployment info
if [ "$DEPLOY_MODE" = "production" ]; then
    echo ""
    echo -e "${BLUE}Production URL:${NC}"
    npx vercel ls --prod
else
    echo ""
    echo -e "${BLUE}Preview URLs:${NC}"
    npx vercel ls
fi

echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "1. Update backend CORS with new frontend URL"
echo "2. Update backend FRONTEND_URL env var"
echo "3. Test the deployed app"
