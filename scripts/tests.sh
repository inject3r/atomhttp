#!/bin/bash

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}         AtomHTTP - Test Runner         ${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo -e "${YELLOW}Project directory: ${PROJECT_DIR}${NC}"
echo ""

cd "$PROJECT_DIR"

# Check if Python is available
if ! command -v python &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed${NC}"
    exit 1
fi

echo -e "${BLUE}Python version:${NC}"
python --version
echo ""

# Install test dependencies if needed
echo -e "${YELLOW}Checking test dependencies...${NC}"

if ! python -c "import pytest" 2>/dev/null; then
    echo -e "${YELLOW}pytest not found. Installing...${NC}"
    exit
fi

if ! python -c "import pytest_asyncio" 2>/dev/null; then
    echo -e "${YELLOW}pytest-asyncio not found. Installing...${NC}"
    exit
fi

echo -e "${GREEN}✓ Dependencies ready${NC}"
echo ""

# Clean previous coverage
echo -e "${YELLOW}Cleaning previous coverage data...${NC}"
rm -rf .pytest_cache .coverage htmlcov tests/.coverage tests/.coverage.* 2>/dev/null || true
echo ""

# Run tests with coverage
echo -e "${BLUE}Running tests with coverage...${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

python -m pytest tests/ \
    -v \
    --tb=short \
    --cov=atomhttp \
    --cov-report=term-missing \
    --cov-report=html:htmlcov \
    --asyncio-mode=auto \
    -W ignore::DeprecationWarning

TEST_EXIT_CODE=$?

echo ""
echo -e "${BLUE}========================================${NC}"

if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
else
    echo -e "${RED}✗ Some tests failed!${NC}"
fi

echo ""
echo -e "${YELLOW}Coverage report saved to: htmlcov/index.html${NC}"
echo -e "${BLUE}========================================${NC}"

exit $TEST_EXIT_CODE