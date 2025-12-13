#!/bin/bash
# Brazilian Soccer MCP Hive Mind - Test Runner Script

set -e

echo "=========================================="
echo "Brazilian Soccer MCP Test Suite"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo -e "${RED}Error: pytest is not installed${NC}"
    echo "Install with: pip install -r requirements-test.txt"
    exit 1
fi

# Parse arguments
MODE=${1:-all}

case $MODE in
    unit)
        echo -e "${GREEN}Running unit tests only...${NC}"
        pytest -m "not integration" -v
        ;;
    integration)
        echo -e "${YELLOW}Running integration tests...${NC}"
        echo "Note: Requires Neo4j to be running"
        pytest -m integration -v
        ;;
    coverage)
        echo -e "${GREEN}Running tests with coverage...${NC}"
        pytest --cov=src --cov-report=html --cov-report=term-missing
        echo ""
        echo -e "${GREEN}Coverage report generated: htmlcov/index.html${NC}"
        ;;
    quick)
        echo -e "${GREEN}Running quick tests (no integration)...${NC}"
        pytest -m "not integration and not slow" -v
        ;;
    performance)
        echo -e "${YELLOW}Running performance tests...${NC}"
        pytest -m performance -v
        ;;
    all)
        echo -e "${GREEN}Running all tests with coverage...${NC}"
        pytest --cov=src --cov-report=html --cov-report=term-missing -v
        echo ""
        echo -e "${GREEN}All tests completed!${NC}"
        echo -e "${GREEN}Coverage report: htmlcov/index.html${NC}"
        ;;
    *)
        echo -e "${RED}Unknown mode: $MODE${NC}"
        echo ""
        echo "Usage: ./run_tests.sh [mode]"
        echo ""
        echo "Modes:"
        echo "  all           - Run all tests with coverage (default)"
        echo "  unit          - Run only unit tests"
        echo "  integration   - Run only integration tests"
        echo "  coverage      - Run with detailed coverage report"
        echo "  quick         - Run fast tests only"
        echo "  performance   - Run performance benchmarks"
        echo ""
        echo "Examples:"
        echo "  ./run_tests.sh"
        echo "  ./run_tests.sh unit"
        echo "  ./run_tests.sh coverage"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}=========================================="
echo "Test run completed!"
echo "==========================================${NC}"
