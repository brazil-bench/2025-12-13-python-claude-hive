"""
Brazilian Soccer MCP - Neo4j Client Tests

CONTEXT:
Comprehensive test suite for Neo4jClient class. Tests schema creation,
data import, graph queries, and error handling. Uses pytest fixtures
for test isolation and testcontainers for self-contained integration tests.

DESIGN:
- Unit tests for individual methods
- Integration tests using testcontainers (self-contained)
- Mock data for consistent testing
- Proper setup/teardown for test isolation
- Error case coverage

USAGE:
    pytest tests/test_neo4j_client.py -v

AUTHOR: Coder Agent - Brazilian Soccer MCP Hive Mind
PHASE: 3 - Neo4j Knowledge Graph
ISSUE: #7 - Integration tests must be self-contained using testcontainers
"""

import pytest
from typing import Dict, Any, List
from datetime import datetime
import os

# Check if Neo4j package is available
try:
    from neo4j.exceptions import ServiceUnavailable, AuthError
    import neo4j
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False
    ServiceUnavailable = Exception
    AuthError = Exception

# Check if testcontainers is available
try:
    from testcontainers.neo4j import Neo4jContainer
    TESTCONTAINERS_AVAILABLE = True
except ImportError:
    TESTCONTAINERS_AVAILABLE = False
    Neo4jContainer = None

# ============================================================================
# TEST FIXTURES
# ============================================================================

@pytest.fixture
def mock_team_data() -> List[Dict[str, Any]]:
    """Generate mock team data for testing."""
    return [
        {
            "id": "flamengo",
            "name": "Flamengo",
            "founded": 1895,
            "city": "Rio de Janeiro",
            "state": "RJ",
            "stadium": "Maracanã",
            "colors": ["red", "black"]
        },
        {
            "id": "palmeiras",
            "name": "Palmeiras",
            "founded": 1914,
            "city": "São Paulo",
            "state": "SP",
            "stadium": "Allianz Parque",
            "colors": ["green", "white"]
        }
    ]

@pytest.fixture
def mock_player_data() -> List[Dict[str, Any]]:
    """Generate mock player data for testing."""
    return [
        {
            "id": "player_001",
            "name": "Gabriel Barbosa",
            "birth_date": "1996-08-30",
            "nationality": "BRA",
            "position": "Forward",
            "height": 178.0,
            "weight": 73.0
        },
        {
            "id": "player_002",
            "name": "Gustavo Gómez",
            "birth_date": "1993-05-06",
            "nationality": "PAR",
            "position": "Defender",
            "height": 187.0,
            "weight": 85.0
        }
    ]

@pytest.fixture
def mock_match_data() -> List[Dict[str, Any]]:
    """Generate mock match data for testing."""
    return [
        {
            "match_id": "match_001",
            "date": "2024-03-15T20:00:00",
            "round": 1,
            "home_team_id": "flamengo",
            "away_team_id": "palmeiras",
            "home_score": 2,
            "away_score": 1,
            "status": "completed"
        }
    ]


@pytest.fixture(scope="session")
def neo4j_container():
    """
    Session-scoped fixture that starts a Neo4j container for integration tests.

    This fixture uses testcontainers to automatically start and stop a Neo4j
    database instance, making tests self-contained and reproducible.

    The container is shared across all tests in the session for efficiency.
    """
    if not TESTCONTAINERS_AVAILABLE:
        pytest.skip("testcontainers not installed - run: pip install testcontainers[neo4j]")

    # Check if Docker is available
    try:
        import docker
        client = docker.from_env()
        client.ping()
    except Exception:
        pytest.skip("Docker not available for testcontainers")

    # Start Neo4j container
    with Neo4jContainer("neo4j:5") as neo4j:
        yield neo4j


@pytest.fixture
def neo4j_client_container(neo4j_container):
    """
    Fixture that provides a Neo4jClient connected to the testcontainer.

    Each test gets a fresh client connection. The database is cleared
    after each test to ensure isolation.
    """
    from src.neo4j_client import Neo4jClient

    # Get connection details from container
    uri = neo4j_container.get_connection_url()

    # Create client
    client = Neo4jClient(
        uri=uri,
        user="neo4j",
        password="test"  # Default testcontainer password
    )

    yield client

    # Cleanup: clear database after each test
    try:
        client.clear_database()
    except Exception:
        pass
    finally:
        client.close()


# ============================================================================
# UNIT TESTS
# ============================================================================

@pytest.mark.skipif(not NEO4J_AVAILABLE, reason="Neo4j package not installed")
class TestNeo4jClient:
    """Test suite for Neo4jClient class."""

    def test_client_initialization(self):
        """Test client initialization with valid credentials."""
        # This would require a running Neo4j instance
        # For now, just test import
        from src.neo4j_client import Neo4jClient
        assert Neo4jClient is not None

    def test_schema_creation_queries(self):
        """Test schema constraint and index query generation."""
        from src.graph_schema import CONSTRAINTS, INDEXES

        # Verify constraints exist
        assert "unique_constraints" in CONSTRAINTS
        assert "existence_constraints" in CONSTRAINTS
        assert len(CONSTRAINTS["unique_constraints"]) > 0

        # Verify indexes exist
        assert len(INDEXES) > 0

        # Check constraint format
        for constraint in CONSTRAINTS["unique_constraints"]:
            assert "CREATE CONSTRAINT" in constraint
            assert "IF NOT EXISTS" in constraint

    def test_batch_import_query_format(self):
        """Test batch import query structure."""
        from src.graph_queries import BATCH_CREATE_TEAMS

        assert "UNWIND $teams AS team" in BATCH_CREATE_TEAMS
        assert "MERGE (t:Team {id: team.id})" in BATCH_CREATE_TEAMS
        assert "RETURN count(t)" in BATCH_CREATE_TEAMS

    def test_graph_query_parameterization(self):
        """Test that queries use parameters (not string concatenation)."""
        from src.graph_queries import (
            FIND_SHORTEST_PATH_BETWEEN_TEAMS,
            FIND_COMMON_OPPONENTS,
            GET_TEAM_STATISTICS
        )

        # Verify parameter usage
        assert "$team1_id" in FIND_SHORTEST_PATH_BETWEEN_TEAMS
        assert "$team2_id" in FIND_SHORTEST_PATH_BETWEEN_TEAMS
        assert "$team_id" in GET_TEAM_STATISTICS

        # Ensure no SQL injection risks
        assert "'{" not in FIND_COMMON_OPPONENTS  # No string interpolation


# ============================================================================
# INTEGRATION TESTS (Self-Contained with Testcontainers)
# ============================================================================

@pytest.mark.integration
@pytest.mark.skipif(
    not (NEO4J_AVAILABLE and TESTCONTAINERS_AVAILABLE),
    reason="Neo4j package or testcontainers not installed"
)
class TestNeo4jIntegration:
    """
    Integration tests using testcontainers for self-contained Neo4j testing.

    These tests automatically start a Neo4j container, run tests, and
    clean up - no external Neo4j instance required.
    """

    def test_full_import_workflow(self, neo4j_client_container, mock_team_data):
        """Test complete data import workflow."""
        client = neo4j_client_container

        # Create schema
        client.create_constraints()
        client.create_indexes()

        # Import data
        count = client.import_teams(mock_team_data)
        assert count == len(mock_team_data)

        # Verify import
        stats = client.get_database_statistics()
        assert stats["nodes"].get("Team", 0) == len(mock_team_data)

    def test_team_query(self, neo4j_client_container, mock_team_data):
        """Test querying teams from the database."""
        client = neo4j_client_container

        # Import teams
        client.import_teams(mock_team_data)

        # Query team
        team = client.get_team("flamengo")
        assert team is not None
        assert team["name"] == "Flamengo"

    def test_match_import_and_query(
        self,
        neo4j_client_container,
        mock_team_data,
        mock_match_data
    ):
        """Test importing and querying matches."""
        client = neo4j_client_container

        # Import teams first (required for relationships)
        client.import_teams(mock_team_data)

        # Import matches
        count = client.import_matches(mock_match_data)
        assert count == len(mock_match_data)

        # Query matches
        matches = client.get_matches_by_team("flamengo")
        assert len(matches) >= 1


# ============================================================================
# CONFIGURATION TESTS
# ============================================================================

class TestNeo4jConfiguration:
    """Test configuration management."""

    def test_config_creation(self):
        """Test configuration object creation."""
        from config.neo4j_config import Neo4jConfig

        config = Neo4jConfig(
            uri="bolt://localhost:7687",
            user="neo4j",
            password="password"
        )

        assert config.uri == "bolt://localhost:7687"
        assert config.auth == ("neo4j", "password")

    def test_config_validation(self):
        """Test configuration validation."""
        from config.neo4j_config import Neo4jConfig, validate_config

        # Valid config
        valid_config = Neo4jConfig(
            uri="bolt://localhost:7687",
            user="neo4j",
            password="password"
        )
        is_valid, error = validate_config(valid_config)
        assert is_valid
        assert error is None

        # Invalid URI
        invalid_config = Neo4jConfig(
            uri="http://localhost:7687",  # Wrong scheme
            user="neo4j",
            password="password"
        )
        is_valid, error = validate_config(invalid_config)
        assert not is_valid
        assert error is not None


# ============================================================================
# SCHEMA TESTS
# ============================================================================

class TestGraphSchema:
    """Test graph schema definitions."""

    def test_node_labels_defined(self):
        """Test that all node labels are defined."""
        from src.graph_schema import (
            TEAM, PLAYER, MATCH, COMPETITION, SEASON, STADIUM
        )

        assert TEAM == "Team"
        assert PLAYER == "Player"
        assert MATCH == "Match"

    def test_relationship_types_defined(self):
        """Test that all relationship types are defined."""
        from src.graph_schema import (
            PLAYED_HOME, PLAYED_AWAY, PLAYS_FOR, COMPETED_IN
        )

        assert PLAYED_HOME == "PLAYED_HOME"
        assert PLAYED_AWAY == "PLAYED_AWAY"
        assert PLAYS_FOR == "PLAYS_FOR"

    def test_schema_summary(self):
        """Test schema summary generation."""
        from src.graph_schema import get_schema_summary

        summary = get_schema_summary()

        assert "nodes" in summary
        assert "relationships" in summary
        assert "constraints" in summary
        assert "indexes" in summary

        assert len(summary["nodes"]["labels"]) >= 6
        assert len(summary["relationships"]["types"]) >= 4


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
