# Brazilian Soccer MCP Hive Mind - Testing Guide

## Overview

This project uses **BDD (Behavior-Driven Development)** with **Given-When-Then (GWT)** structure for all tests. Tests are written using PyTest and follow industry best practices for maintainability, clarity, and coverage.

## Test Structure

### Directory Organization

```
tests/
├── __init__.py              # Test package initialization
├── conftest.py              # Shared fixtures and configuration
├── test_data_loader.py      # Data loading tests
├── test_query_engine.py     # Query and statistics tests
├── test_neo4j_client.py     # Neo4j graph database tests
├── test_team_normalizer.py  # Team name normalization tests
└── test_integration.py      # End-to-end integration tests
```

## Running Tests

### Basic Test Execution

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_data_loader.py

# Run specific test class
pytest tests/test_query_engine.py::TestMatchQueries

# Run specific test
pytest tests/test_query_engine.py::TestMatchQueries::test_find_matches_between_teams
```

### Test Categories

Tests are organized by markers for selective execution:

```bash
# Run only unit tests (fast)
pytest -m unit

# Run only integration tests
pytest -m integration

# Run only Neo4j tests
pytest -m neo4j

# Run only performance tests
pytest -m performance

# Exclude slow tests
pytest -m "not slow"
```

### Coverage Reports

```bash
# Run tests with coverage report
pytest --cov=src --cov-report=html

# View coverage report
open htmlcov/index.html

# Coverage with terminal report
pytest --cov=src --cov-report=term-missing
```

## BDD Given-When-Then Structure

All tests follow the BDD pattern:

```python
def test_example(self, sample_data):
    """
    Scenario: Clear description of what is being tested

    Given: The initial state or preconditions
    When: The action being performed
    Then: The expected outcome
    And: Additional expectations
    """
    # Given - Setup
    loader = DataLoader()

    # When - Execute
    result = loader.load_matches(sample_data)

    # Then - Assert
    assert len(result) > 0
    assert all("home_team" in match for match in result)
```

## Test Fixtures

Common fixtures are defined in `conftest.py`:

### Data Fixtures

- `sample_matches`: Pre-defined match data
- `sample_players`: Pre-defined player data
- `sample_teams`: List of team names
- `temp_data_file`: Temporary CSV file with test data

### Component Fixtures

- `data_loader`: Configured DataLoader instance
- `query_engine`: Configured QueryEngine instance
- `neo4j_client`: Mocked Neo4j client
- `neo4j_client_integration`: Real Neo4j client (for integration tests)

### Using Fixtures

```python
def test_with_fixtures(sample_matches, query_engine):
    """Test using multiple fixtures"""
    query_engine.load_matches(sample_matches)
    results = query_engine.find_matches_by_team("Flamengo")
    assert len(results) > 0
```

## Test Categories

### 1. Data Loader Tests (`test_data_loader.py`)

**Features:**
- Load matches from CSV/JSON
- Validate data integrity
- Handle edge cases (empty files, malformed data)
- Data transformation and filtering

**Example:**
```python
def test_load_matches_from_csv(self, temp_data_file):
    """
    Scenario: Load matches from CSV file

    Given: A CSV file with match data
    When: I load the matches using DataLoader
    Then: The matches should be parsed correctly
    """
```

### 2. Query Engine Tests (`test_query_engine.py`)

**Features:**
- Find matches between teams
- Calculate team statistics
- Generate head-to-head records
- Advanced filtering and aggregation

**Example:**
```python
def test_get_team_statistics(self, query_engine):
    """
    Scenario: Get team statistics for a season

    Given: The match data is loaded
    When: I request statistics for "Palmeiras" in season "2023"
    Then: I should receive wins, losses, draws, and goals
    """
```

### 3. Neo4j Client Tests (`test_neo4j_client.py`)

**Features:**
- Create team and player nodes
- Create match relationships
- Graph queries and traversals
- Connection management

**Note:** Uses mocked driver for unit tests, real connection for integration tests.

### 4. Team Normalizer Tests (`test_team_normalizer.py`)

**Features:**
- Normalize official names to short forms
- Handle accents and special characters
- Process abbreviations and nicknames
- Case-insensitive matching

**Example:**
```python
@pytest.mark.parametrize("full_name,expected", [
    ("Clube de Regatas do Flamengo", "Flamengo"),
    ("Sociedade Esportiva Palmeiras", "Palmeiras"),
])
def test_normalize_official_names(self, full_name, expected):
    normalizer = TeamNormalizer()
    assert normalizer.normalize(full_name) == expected
```

### 5. Integration Tests (`test_integration.py`)

**Features:**
- End-to-end data pipeline
- Cross-component consistency
- Performance benchmarks
- Error recovery

## Parametrized Tests

Use `@pytest.mark.parametrize` for testing multiple scenarios:

```python
@pytest.mark.parametrize("season", ["2023", "2022", "2024"])
def test_find_matches_by_season(self, query_engine, season):
    """Test querying matches across different seasons"""
    results = query_engine.find_matches_by_season(season)
    assert all(match["season"] == season for match in results)
```

## Mocking

### Mocking Neo4j Driver

```python
def test_with_mock_neo4j(self, mock_neo4j_driver):
    """Test with mocked Neo4j driver"""
    mock_session = mock_neo4j_driver.session.return_value.__enter__.return_value
    mock_session.run.return_value = []
    # Test implementation
```

### Mocking File Operations

```python
@patch('builtins.open', mock_open(read_data='csv,data'))
def test_load_from_file():
    """Test with mocked file reading"""
    # Test implementation
```

## Integration Tests

Integration tests require external services:

### Neo4j Integration Tests

```bash
# Set environment variables
export NEO4J_URI="bolt://localhost:7687"
export NEO4J_USER="neo4j"
export NEO4J_PASSWORD="password"

# Run integration tests
pytest -m integration
```

### Skipping Integration Tests

Integration tests automatically skip if services are unavailable:

```python
@pytest.mark.integration
def test_real_neo4j_connection(self, neo4j_client_integration):
    """Automatically skipped if Neo4j not available"""
    assert neo4j_client_integration.verify_connectivity()
```

## Performance Testing

Performance tests measure execution time and resource usage:

```python
def test_query_performance(self, large_dataset):
    """Test query performance with large dataset"""
    import time

    start = time.time()
    results = engine.query_matches(large_dataset)
    duration = time.time() - start

    assert duration < 1.0  # Should complete in under 1 second
```

## Coverage Goals

**Target Coverage:**
- Statements: >80%
- Branches: >75%
- Functions: >80%
- Lines: >80%

**Priority Areas:**
- Core business logic: >90%
- Data validation: >85%
- Error handling: >80%
- Integration paths: >70%

## Best Practices

### 1. Test Naming

- Use descriptive names that explain the scenario
- Follow pattern: `test_<action>_<context>_<expected_result>`
- Example: `test_normalize_team_name_with_accents_returns_canonical_form`

### 2. Test Independence

- Each test should be independent
- Use fixtures for setup
- Clean up after tests (especially integration tests)

### 3. Assertions

- Use specific assertions (`assert x == y`, not `assert x`)
- Include meaningful assertion messages
- Test one behavior per test

### 4. Documentation

- Start each test with GWT docstring
- Explain complex test scenarios
- Document fixture usage

### 5. Edge Cases

Always test:
- Empty inputs
- Null/None values
- Invalid data types
- Boundary conditions
- Error conditions

## Continuous Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          pip install -r requirements-test.txt
      - name: Run tests
        run: |
          pytest --cov=src --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

## Troubleshooting

### Common Issues

**Import Errors:**
```bash
# Ensure src is in Python path
export PYTHONPATH="${PYTHONPATH}:/workspaces/2025-12-13-python-claude-hive/src"
```

**Neo4j Connection Errors:**
```bash
# Check Neo4j is running
docker ps | grep neo4j

# Verify credentials
echo $NEO4J_PASSWORD
```

**Coverage Not Including Files:**
```bash
# Check .coveragerc or pytest.ini
# Ensure source paths are correct
```

## Resources

- [PyTest Documentation](https://docs.pytest.org/)
- [Coverage.py](https://coverage.readthedocs.io/)
- [BDD with Python](https://cucumber.io/docs/gherkin/)
- [Testing Best Practices](https://testdriven.io/blog/testing-best-practices/)
