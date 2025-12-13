"""
Brazilian Soccer MCP Hive Mind - Test Fixtures and Configuration
=================================================================

This module provides shared pytest fixtures for all test modules.

Fixtures:
- sample_matches: Pre-defined match data for testing
- sample_players: Pre-defined player data for testing
- sample_teams: Pre-defined team data for testing
- data_loader: DataLoader instance with sample data
- query_engine: QueryEngine instance with sample data
- neo4j_client: Neo4j client (skip if not available)
- mock_neo4j: Mocked Neo4j driver for unit tests

Usage:
    def test_something(sample_matches, query_engine):
        # Test implementation
"""

import pytest
from datetime import datetime
from typing import List, Dict, Any
from unittest.mock import Mock, MagicMock
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


@pytest.fixture
def sample_teams() -> List[str]:
    """
    Given: A list of Brazilian soccer teams
    Returns: List of team names for testing
    """
    return [
        "Flamengo",
        "Palmeiras",
        "Corinthians",
        "São Paulo",
        "Fluminense",
        "Santos",
        "Grêmio",
        "Internacional",
        "Atlético Mineiro",
        "Botafogo"
    ]


@pytest.fixture
def sample_matches() -> List[Dict[str, Any]]:
    """
    Given: Sample Brasileirão match data
    Returns: List of match dictionaries with complete information

    Match Structure:
    - date: Match date (ISO format or datetime)
    - home_team: Home team name
    - away_team: Away team name
    - home_score: Home team goals
    - away_score: Away team goals
    - season: Season year
    - round: Match round number
    """
    return [
        {
            "date": "2023-05-14",
            "home_team": "Flamengo",
            "away_team": "Fluminense",
            "home_score": 2,
            "away_score": 1,
            "season": "2023",
            "round": 1
        },
        {
            "date": "2023-05-21",
            "home_team": "Palmeiras",
            "away_team": "Corinthians",
            "home_score": 1,
            "away_score": 1,
            "season": "2023",
            "round": 2
        },
        {
            "date": "2023-05-28",
            "home_team": "Fluminense",
            "away_team": "Flamengo",
            "home_score": 0,
            "away_score": 2,
            "season": "2023",
            "round": 3
        },
        {
            "date": "2023-06-04",
            "home_team": "São Paulo",
            "away_team": "Palmeiras",
            "home_score": 1,
            "away_score": 3,
            "season": "2023",
            "round": 4
        },
        {
            "date": "2023-06-11",
            "home_team": "Corinthians",
            "away_team": "Santos",
            "home_score": 2,
            "away_score": 0,
            "season": "2023",
            "round": 5
        },
    ]


@pytest.fixture
def sample_players() -> List[Dict[str, Any]]:
    """
    Given: Sample player data
    Returns: List of player dictionaries

    Player Structure:
    - name: Player full name
    - team: Current team
    - position: Playing position
    - nationality: Player nationality
    - age: Player age
    """
    return [
        {
            "name": "Gabriel Barbosa",
            "team": "Flamengo",
            "position": "Forward",
            "nationality": "Brazilian",
            "age": 27
        },
        {
            "name": "Raphael Veiga",
            "team": "Palmeiras",
            "position": "Midfielder",
            "nationality": "Brazilian",
            "age": 28
        },
        {
            "name": "Germán Cano",
            "team": "Fluminense",
            "position": "Forward",
            "nationality": "Argentine",
            "age": 35
        },
        {
            "name": "Yuri Alberto",
            "team": "Corinthians",
            "position": "Forward",
            "nationality": "Brazilian",
            "age": 23
        },
    ]


@pytest.fixture
def data_loader(sample_matches):
    """
    Given: A DataLoader instance
    When: Initialized with sample match data
    Then: Returns a configured DataLoader for testing

    Note: This fixture attempts to import DataLoader.
    If not available, it returns a mock object.
    """
    try:
        from data_loader import DataLoader
        loader = DataLoader()
        # Pre-load with sample data
        loader._matches = sample_matches
        return loader
    except ImportError:
        # Return a mock if DataLoader not yet implemented
        mock_loader = Mock()
        mock_loader.load_matches.return_value = sample_matches
        mock_loader.get_matches.return_value = sample_matches
        return mock_loader


@pytest.fixture
def query_engine(sample_matches):
    """
    Given: A QueryEngine instance
    When: Initialized with sample match data
    Then: Returns a configured QueryEngine for testing

    Note: This fixture attempts to import QueryEngine.
    If not available, it returns a mock object.
    """
    try:
        from query_engine import QueryEngine
        engine = QueryEngine()
        engine._matches = sample_matches
        return engine
    except ImportError:
        # Return a mock if QueryEngine not yet implemented
        mock_engine = Mock()
        mock_engine.find_matches_between_teams.return_value = [sample_matches[0], sample_matches[2]]
        mock_engine.get_team_statistics.return_value = {
            "wins": 5,
            "losses": 2,
            "draws": 3,
            "goals_scored": 15,
            "goals_conceded": 8
        }
        return mock_engine


@pytest.fixture
def mock_neo4j_driver():
    """
    Given: A mocked Neo4j driver
    Returns: Mock Neo4j driver for unit testing without database

    Mocked Methods:
    - session(): Returns mock session
    - close(): Mock close method
    """
    mock_driver = MagicMock()
    mock_session = MagicMock()
    mock_driver.session.return_value.__enter__.return_value = mock_session
    mock_driver.session.return_value.__exit__.return_value = None
    return mock_driver


@pytest.fixture
def neo4j_client(mock_neo4j_driver):
    """
    Given: A Neo4j client instance
    When: Initialized with mocked driver
    Then: Returns a Neo4jClient for testing (or skip if not available)

    This fixture uses a mocked Neo4j driver to avoid requiring
    a running Neo4j instance for unit tests.
    """
    try:
        from neo4j_client import Neo4jClient
        client = Neo4jClient(uri="bolt://localhost:7687", user="neo4j", password="test")
        # Replace real driver with mock
        client._driver = mock_neo4j_driver
        return client
    except ImportError:
        # Return a mock if Neo4jClient not yet implemented
        mock_client = Mock()
        mock_client.create_team.return_value = True
        mock_client.create_match.return_value = True
        mock_client.find_matches_between_teams.return_value = []
        return mock_client


@pytest.fixture
def neo4j_client_integration():
    """
    Given: A real Neo4j connection
    When: Neo4j is available
    Then: Returns a real Neo4jClient for integration testing

    Skips if:
    - Neo4j is not installed
    - Neo4j server is not running
    - Connection credentials are invalid
    """
    pytest.importorskip("neo4j")

    try:
        from neo4j_client import Neo4jClient
        client = Neo4jClient(
            uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
            user=os.getenv("NEO4J_USER", "neo4j"),
            password=os.getenv("NEO4J_PASSWORD", "password")
        )
        # Test connection
        client.verify_connectivity()
        yield client
        # Cleanup
        client.close()
    except Exception as e:
        pytest.skip(f"Neo4j not available: {e}")


@pytest.fixture
def temp_data_file(tmp_path, sample_matches):
    """
    Given: A temporary CSV file with match data
    Returns: Path to temporary test data file

    Used for testing data loading from files.
    """
    import csv

    data_file = tmp_path / "matches.csv"

    with open(data_file, 'w', newline='', encoding='utf-8') as f:
        if sample_matches:
            writer = csv.DictWriter(f, fieldnames=sample_matches[0].keys())
            writer.writeheader()
            writer.writerows(sample_matches)

    return str(data_file)


@pytest.fixture(autouse=True)
def reset_singletons():
    """
    Given: Tests that may modify singleton state
    When: Each test runs
    Then: Reset any singleton instances to avoid test pollution
    """
    yield
    # Cleanup code after each test
    # Add any singleton reset logic here if needed
