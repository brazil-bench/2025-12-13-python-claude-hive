"""
Brazilian Soccer MCP Hive Mind - Test Suite
============================================

This test package contains comprehensive BDD-style tests using Given-When-Then (GWT)
structure for all three phases of the Brazilian Soccer MCP project.

Test Organization:
- conftest.py: Shared fixtures and test configuration
- test_data_loader.py: Data loading and parsing tests
- test_query_engine.py: Match query and statistics tests
- test_neo4j_client.py: Graph database operations tests
- test_team_normalizer.py: Team name normalization tests
- test_integration.py: End-to-end integration tests

Testing Methodology:
- BDD (Behavior-Driven Development) with GWT structure
- Unit tests with mocked dependencies
- Integration tests with real components
- Parametrized tests for multiple scenarios
- Edge case coverage (empty data, invalid inputs, etc.)

Dependencies:
- pytest: Test framework
- pytest-mock: Mocking support
- pytest-asyncio: Async test support (if needed)
"""

__version__ = "1.0.0"
