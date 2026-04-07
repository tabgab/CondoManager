#!/bin/bash
# Migration Runner Script for CondoManager
# Usage: ./run_migrations.sh [--check] [--rollback]
#   --check: Verify migrations are up to date (dry run)
#   --rollback: Rollback one migration (for debugging)

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}CondoManager Migration Runner${NC}"
echo "================================"
echo ""

# Check if we're in the right directory
if [ ! -f "alembic.ini" ]; then
    echo -e "${RED}Error: alembic.ini not found${NC}"
    echo "Please run this script from the backend directory"
    exit 1
fi

# Parse arguments
CHECK_MODE=false
ROLLBACK_MODE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --check)
            CHECK_MODE=true
            shift
            ;;
        --rollback)
            ROLLBACK_MODE=true
            shift
            ;;
        *)
            echo -e "${YELLOW}Warning: Unknown option $1${NC}"
            shift
            ;;
    esac
done

# Check database connection
echo -e "${BLUE}Checking database connection...${NC}"
if [ -z "$DATABASE_URL" ]; then
    echo -e "${RED}Error: DATABASE_URL not set${NC}"
    echo "Please set the DATABASE_URL environment variable"
    exit 1
fi

echo -e "${GREEN}✓ Database URL configured${NC}"
echo ""

# Show current migration status
echo -e "${BLUE}Current migration status:${NC}"
alembic current 2>/dev/null || echo -e "${YELLOW}No migrations applied yet${NC}"
echo ""

# Run migrations based on mode
if [ "$CHECK_MODE" = true ]; then
    echo -e "${BLUE}Running migration check (dry-run)...${NC}"
    # Check if there are pending migrations
    PENDING=$(alembic history --indicate-current 2>&1 | grep "(current)" | head -1)
    if [ -n "$PENDING" ]; then
        echo -e "${GREEN}✓ Database is up to date${NC}"
    else
        echo -e "${YELLOW}⚠ Pending migrations found:${NC}"
        alembic history --indicate-current | head -20
    fi
    exit 0
fi

if [ "$ROLLBACK_MODE" = true ]; then
    echo -e "${YELLOW}Rolling back one migration...${NC}"
    alembic downgrade -1
    echo -e "${GREEN}✓ Rolled back successfully${NC}"
    exit 0
fi

# Normal upgrade mode
echo -e "${BLUE}Running migrations...${NC}"
echo "Target: head (latest version)"
echo ""

# Run the migration
alembic upgrade head

# Verify
CURRENT=$(alembic current 2>/dev/null | grep -oE '[a-f0-9]{12}' | head -1)
if [ -n "$CURRENT" ]; then
    echo ""
    echo -e "${GREEN}✓ Migrations applied successfully${NC}"
    echo -e "${BLUE}Current revision:${NC} $CURRENT"
    echo ""
    echo -e "${BLUE}Migration history:${NC}"
    alembic history --indicate-current | head -10
else
    echo -e "${YELLOW}⚠ Could not verify migration status${NC}"
fi

# Show version info
echo ""
echo -e "${BLUE}Version info:${NC}"
python -c "import alembic; print(f'Alembic: {alembic.__version__}')" 2>/dev/null || echo "Alembic version unknown"
python -c "import sqlalchemy; print(f'SQLAlchemy: {sqlalchemy.__version__}')" 2>/dev/null || echo "SQLAlchemy version unknown"

echo ""
echo -e "${GREEN}Migration complete!${NC}"
