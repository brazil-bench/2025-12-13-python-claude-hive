# Brazilian Soccer MCP Hive Mind - Test Suite

## Quick Start

```bash
# Install test dependencies
pip install -r requirements-test.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# View coverage report
open htmlcov/index.html
```

## Test Files (7 files, 2,401 lines)

### Core Test Files

| File | Purpose | Tests | Lines |
|------|---------|-------|-------|
| `conftest.py` | Shared fixtures | 10 fixtures | ~300 |
| `test_data_loader.py` | Data loading & validation | 13 | ~400 |
| `test_query_engine.py` | Queries & statistics | 13 | ~500 |
| `test_neo4j_client.py` | Graph database ops | 14 | ~450 |
| `test_team_normalizer.py` | Name normalization | 12 | ~400 |
| `test_integration.py` | End-to-end workflows | 12 | ~650 |

**Total: 64+ tests, 90+ effective test cases (with parametrization)**

## Test Structure (BDD/GWT)

All tests follow Given-When-Then structure:

```python
def test_example(self, sample_data):
    """
    Scenario: What is being tested

    Given: Initial state
    When: Action performed
    Then: Expected outcome
    """
    # Given
    loader = DataLoader()

    # When
    result = loader.load_matches(sample_data)

    # Then
    assert len(result) > 0
```

## Fixtures (from conftest.py)

### Data Fixtures
- `sample_teams` - 10 Brazilian teams
- `sample_matches` - 5 complete matches
- `sample_players` - 4 player records
- `temp_data_file` - Temporary CSV file

### Component Fixtures
- `data_loader` - Configured DataLoader
- `query_engine` - Configured QueryEngine
- `neo4j_client` - Mocked Neo4j client
- `neo4j_client_integration` - Real Neo4j (skips if unavailable)

## Test Categories

### Run by Marker

```bash
# Unit tests only (fast)
pytest -m "not integration"

# Integration tests (requires Neo4j)
pytest -m integration

# Performance tests
pytest -m performance

# Neo4j tests
pytest -m neo4j
```

### Available Markers
- `unit` - Fast, isolated unit tests
- `integration` - Require external services
- `neo4j` - Require Neo4j database
- `performance` - Performance benchmarks
- `mcp` - MCP integration tests

## Test Coverage

### Target Coverage
- Statements: >80%
- Branches: >75%
- Functions: >80%
- Lines: >80%

### Generate Coverage Report

```bash
# Terminal report
pytest --cov=src --cov-report=term-missing

# HTML report
pytest --cov=src --cov-report=html
open htmlcov/index.html

# Both
pytest --cov=src --cov-report=html --cov-report=term
```

## Test Examples

### Data Loading Test

```python
def test_load_matches_from_csv(self, temp_data_file):
    """
    Scenario: Load matches from CSV file

    Given: A CSV file with match data
    When: I load the matches using DataLoader
    Then: The matches should be parsed correctly
    """
    from data_loader import DataLoader

    loader = DataLoader()
    loader.load_from_csv(temp_data_file)

    matches = loader.get_matches()
    assert len(matches) > 0
```

### Query Engine Test

```python
def test_find_matches_between_teams(self, query_engine):
    """
    Scenario: Find matches between two teams

    Given: The match data is loaded
    When: I search for matches between teams
    Then: I should receive matching results
    """
    results = query_engine.find_matches_between_teams(
        "Flamengo", "Fluminense"
    )

    assert isinstance(results, list)
    assert len(results) > 0
```

### Parametrized Test

```python
@pytest.mark.parametrize("full_name,expected", [
    ("Clube de Regatas do Flamengo", "Flamengo"),
    ("Sociedade Esportiva Palmeiras", "Palmeiras"),
])
def test_normalize_names(self, full_name, expected):
    normalizer = TeamNormalizer()
    assert normalizer.normalize(full_name) == expected
```

## Integration Tests

### Neo4j Integration

Requires environment variables:

```bash
export NEO4J_URI="bolt://localhost:7687"
export NEO4J_USER="neo4j"
export NEO4J_PASSWORD="password"

pytest -m integration
```

Tests automatically skip if Neo4j is unavailable.

## Performance Tests

Test with large datasets:

```python
def test_query_performance_10k_matches(self):
    """Test query speed with 10,000 matches"""
    import time

    large_dataset = sample_matches * 2000
    engine.load_matches(large_dataset)

    start = time.time()
    results = engine.find_matches_by_team("Flamengo")
    duration = time.time() - start

    assert duration < 1.0  # <1 second
```

## CI/CD Integration

### GitHub Actions

Tests run automatically on:
- Push to `main` or `develop`
- Pull requests
- Multiple Python versions (3.9, 3.10, 3.11)

See `.github/workflows/tests.yml`

## Running Specific Tests

```bash
# Single file
pytest tests/test_data_loader.py

# Single class
pytest tests/test_query_engine.py::TestMatchQueries

# Single test
pytest tests/test_query_engine.py::TestMatchQueries::test_find_matches_between_teams

# Pattern matching
pytest -k "normalize"

# Verbose output
pytest -v

# Show print statements
pytest -s
```

## Test Development

### Adding New Tests

1. Choose appropriate test file
2. Follow GWT structure
3. Use existing fixtures
4. Add parametrization for multiple cases
5. Include edge cases
6. Update documentation

### Example Template

```python
class TestNewFeature:
    """
    Feature: New Feature Description
    Tests for the new feature
    """

    def test_basic_functionality(self, fixture):
        """
        Scenario: Basic functionality test

        Given: Initial state
        When: Action is performed
        Then: Expected outcome occurs
        """
        # Given
        component = Component()

        # When
        result = component.method()

        # Then
        assert result is not None

    @pytest.mark.parametrize("input,expected", [
        ("input1", "output1"),
        ("input2", "output2"),
    ])
    def test_multiple_cases(self, input, expected):
        """Test with multiple inputs"""
        assert process(input) == expected
```

## Debugging Tests

```bash
# Drop into debugger on failure
pytest --pdb

# Drop into debugger on first failure
pytest -x --pdb

# Show local variables on failure
pytest -l

# Detailed traceback
pytest --tb=long

# Show slowest tests
pytest --durations=10
```

## Common Issues

### Import Errors

```bash
# Add src to Python path
export PYTHONPATH="${PYTHONPATH}:/workspaces/2025-12-13-python-claude-hive/src"
```

### Neo4j Connection Errors

```bash
# Check Neo4j is running
docker ps | grep neo4j

# Verify credentials
echo $NEO4J_PASSWORD
```

### Coverage Issues

Check `pytest.ini` for source paths:

```ini
[coverage:run]
source = src
```

## Resources

- [PyTest Documentation](https://docs.pytest.org/)
- [Coverage.py](https://coverage.readthedocs.io/)
- [Detailed Testing Guide](/docs/TESTING.md)
- [Test Suite Summary](/docs/TEST_SUITE_SUMMARY.md)

## Test Statistics

- **Total Test Files:** 7
- **Total Lines:** 2,401
- **Total Tests:** 64+
- **Parametrized Cases:** 30+
- **Effective Test Cases:** 90+
- **Coverage Target:** 80%

## Quick Reference

| Command | Description |
|---------|-------------|
| `pytest` | Run all tests |
| `pytest -v` | Verbose output |
| `pytest -x` | Stop on first failure |
| `pytest -k "pattern"` | Run matching tests |
| `pytest -m marker` | Run marked tests |
| `pytest --cov` | With coverage |
| `pytest --lf` | Run last failed |
| `pytest --ff` | Failed first, then rest |

---

For detailed documentation, see:
- `/docs/TESTING.md` - Comprehensive testing guide
- `/docs/TEST_SUITE_SUMMARY.md` - Full test suite summary
