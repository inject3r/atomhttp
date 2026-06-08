#!/bin/bash

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}      AtomHTTP - Clean Test Files       ${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

echo -e "${YELLOW}Cleaning test output directories...${NC}"
echo ""

# Remove pytest cache
if [ -d ".pytest_cache" ]; then
    rm -rf .pytest_cache
    echo -e "  ${GREEN}✓ Removed .pytest_cache/${NC}"
else
    echo -e "  ${YELLOW}⚠ .pytest_cache/ not found${NC}"
fi

# Remove coverage files from root
if [ -f ".coverage" ]; then
    rm -f .coverage
    echo -e "  ${GREEN}✓ Removed .coverage${NC}"
else
    echo -e "  ${YELLOW}⚠ .coverage not found${NC}"
fi

# Remove HTML coverage report
if [ -d "htmlcov" ]; then
    rm -rf htmlcov
    echo -e "  ${GREEN}✓ Removed htmlcov/${NC}"
else
    echo -e "  ${YELLOW}⚠ htmlcov/ not found${NC}"
fi

# Remove coverage files in tests directory
if [ -f "tests/.coverage" ]; then
    rm -f tests/.coverage
    echo -e "  ${GREEN}✓ Removed tests/.coverage${NC}"
fi

if ls tests/.coverage.* 1>/dev/null 2>&1; then
    rm -f tests/.coverage.*
    echo -e "  ${GREEN}✓ Removed tests/.coverage.*${NC}"
fi

# Remove __pycache__ directories
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
echo -e "  ${GREEN}✓ Removed all __pycache__/ directories${NC}"

# Remove .pyc files
find . -type f -name "*.pyc" -delete 2>/dev/null || true
echo -e "  ${GREEN}✓ Removed all .pyc files${NC}"

# Remove .pyo files
find . -type f -name "*.pyo" -delete 2>/dev/null || true
echo -e "  ${GREEN}✓ Removed all .pyo files${NC}"

# Remove pytest temp files
find . -type d -name "pytest-*" -exec rm -rf {} + 2>/dev/null || true

echo ""
echo -e "${GREEN}✓ Clean completed successfully!${NC}"
echo ""
echo -e "${YELLOW}To run tests: ./scripts/tests.sh${NC}"
echo -e "${BLUE}========================================${NC}"