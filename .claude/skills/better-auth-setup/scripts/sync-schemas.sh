#!/bin/bash
#
# sync-schemas.sh - Synchronize Prisma and Alembic database schemas
#
# This script detects type mismatches between Prisma (auth-server) and Alembic (backend)
# schemas and provides recommendations for fixing them.
#
# Common issues:
# - Prisma String vs Alembic INET (ip_address field)
# - Prisma Int vs Alembic BigInteger
# - Nullable differences
#
# Usage:
#   bash scripts/sync-schemas.sh
#   bash scripts/sync-schemas.sh --auto-fix  # Automatically apply fixes

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

PRISMA_SCHEMA="${PRISMA_SCHEMA:-auth-server/prisma/schema.prisma}"
ALEMBIC_MIGRATIONS="${ALEMBIC_MIGRATIONS:-backend/src/database/migrations}"

echo -e "${BLUE}🔄 Synchronizing Prisma and Alembic schemas...${NC}\n"

# Check if files exist
if [ ! -f "$PRISMA_SCHEMA" ]; then
    echo -e "${RED}❌ Error: Prisma schema not found at $PRISMA_SCHEMA${NC}"
    exit 1
fi

if [ ! -d "$ALEMBIC_MIGRATIONS" ]; then
    echo -e "${RED}❌ Error: Alembic migrations directory not found at $ALEMBIC_MIGRATIONS${NC}"
    exit 1
fi

# Find latest Alembic migration
LATEST_MIGRATION=$(find "$ALEMBIC_MIGRATIONS" -name "*.py" -type f | sort | tail -1)

if [ -z "$LATEST_MIGRATION" ]; then
    echo -e "${RED}❌ Error: No Alembic migrations found${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} Prisma schema: $PRISMA_SCHEMA"
echo -e "${GREEN}✓${NC} Latest Alembic migration: $LATEST_MIGRATION"
echo ""

# Check for common type mismatches
ISSUES_FOUND=0

# Issue 1: ip_address field type mismatch
if grep -q "ip_address" "$PRISMA_SCHEMA" && grep -q "INET" "$LATEST_MIGRATION"; then
    echo -e "${YELLOW}⚠️  Issue detected:${NC} ip_address type mismatch"
    echo "   Prisma: String (or Text)"
    echo "   Alembic: INET"
    echo ""
    echo "   ${BLUE}Recommendation:${NC} Change Alembic to use sa.Text instead of postgresql.INET"
    echo "   Edit: $LATEST_MIGRATION"
    echo "   Change: sa.Column('ip_address', postgresql.INET, ...)"
    echo "   To: sa.Column('ip_address', sa.Text, nullable=True)"
    echo ""
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
fi

# Issue 2: Check for BigInteger vs Int mismatches
if grep -q "@db.Int" "$PRISMA_SCHEMA" && grep -q "BigInteger" "$LATEST_MIGRATION"; then
    echo -e "${YELLOW}⚠️  Issue detected:${NC} Integer size mismatch"
    echo "   Prisma: Int (32-bit)"
    echo "   Alembic: BigInteger (64-bit)"
    echo ""
    echo "   ${BLUE}Recommendation:${NC} Ensure consistent integer sizes"
    echo ""
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
fi

# Issue 3: Check for nullable differences
echo -e "${BLUE}ℹ️  Checking nullable field consistency...${NC}"

# Parse Prisma schema for nullable fields
PRISMA_NULLABLE=$(grep -E "^\s+\w+\s+\w+\?" "$PRISMA_SCHEMA" | awk '{print $1}' || true)

# Parse Alembic for nullable fields
ALEMBIC_NULLABLE=$(grep "nullable=True" "$LATEST_MIGRATION" | grep -oP "(?<=')[^']+(?=')" || true)

if [ -n "$PRISMA_NULLABLE" ] && [ -n "$ALEMBIC_NULLABLE" ]; then
    echo -e "${GREEN}✓${NC} Nullable fields found in both schemas"
else
    echo -e "${YELLOW}⚠️  Warning:${NC} Could not fully verify nullable field consistency"
fi

echo ""

# Summary
if [ $ISSUES_FOUND -eq 0 ]; then
    echo -e "${GREEN}✅ No type mismatches detected!${NC}"
    echo ""
    echo "Your Prisma and Alembic schemas appear to be in sync."
else
    echo -e "${YELLOW}⚠️  Found $ISSUES_FOUND potential type mismatch(es)${NC}"
    echo ""
    echo "Please review and fix the issues above to ensure database compatibility."
    echo ""
    echo "After fixing, run:"
    echo "  For Alembic projects: cd backend && alembic upgrade head"
    echo "  For custom Python migrations: cd backend && python src/database/run_migration.py"
fi

# Auto-fix option (if --auto-fix flag provided)
if [ "$1" = "--auto-fix" ]; then
    echo ""
    echo -e "${BLUE}🔧 Auto-fix mode enabled${NC}"
    echo ""

    # Fix ip_address INET issue
    if grep -q "INET" "$LATEST_MIGRATION"; then
        echo "Fixing ip_address type mismatch..."
        # Create backup
        cp "$LATEST_MIGRATION" "${LATEST_MIGRATION}.backup"

        # Replace INET with Text
        sed -i.bak "s/postgresql\.INET/sa.Text/g" "$LATEST_MIGRATION"
        rm "${LATEST_MIGRATION}.bak"

        echo -e "${GREEN}✓${NC} Fixed: Changed INET to Text"
        echo "   Backup created: ${LATEST_MIGRATION}.backup"
    fi

    echo ""
    echo -e "${GREEN}✅ Auto-fix complete!${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Review the changes in: $LATEST_MIGRATION"
    echo "  2. Run: cd backend && alembic upgrade head"
    echo "     OR: cd backend && python src/database/run_migration.py"
fi

echo ""
echo -e "${BLUE}💡 Pro tip:${NC} Add this script to your pre-commit hooks to catch mismatches early!"
