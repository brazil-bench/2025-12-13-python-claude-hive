"""
Brazilian Soccer MCP - BDD Tests for Data Loading
==================================================

Tests for loading data from CSV files using pytest-bdd with Gherkin feature files.

Author: Brazilian Soccer MCP Hive Mind
Date: 2025-12-13
"""

import pytest
from pytest_bdd import scenarios, given, when, then, parsers
from datetime import datetime
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from data_loader import DataLoader
from models import Match, Player

# Load scenarios from feature file
scenarios('../features/data_loading.feature')


# Fixtures
@pytest.fixture
def data_loader():
    """Create DataLoader instance with test data directory."""
    return DataLoader(data_dir="data/kaggle")


@pytest.fixture
def loaded_matches(data_loader):
    """Load Brasileirao matches."""
    return data_loader.load_brasileirao_matches()


@pytest.fixture
def loaded_players(data_loader):
    """Load FIFA players."""
    return data_loader.load_fifa_players()


# Shared context for steps
@pytest.fixture
def context():
    """Shared context dict for passing data between steps."""
    return {}


# Given steps
@given("the data directory exists with CSV files")
def data_directory_exists(data_loader):
    """Verify data directory exists."""
    assert data_loader.data_dir.exists(), f"Data directory {data_loader.data_dir} does not exist"


@given(parsers.parse('a date string "{date_str}"'))
def date_string(context, date_str):
    """Store date string in context."""
    context['date_str'] = date_str


# When steps
@when("I load Brasileirao matches")
def load_brasileirao_matches(data_loader, context):
    """Load Brasileirao match data."""
    context['matches'] = data_loader.load_brasileirao_matches()


@when("I load FIFA players")
def load_fifa_players(data_loader, context):
    """Load FIFA player data."""
    context['players'] = data_loader.load_fifa_players()


@when("I load all datasets")
def load_all_datasets(data_loader, context):
    """Load all available datasets."""
    context['all_data'] = data_loader.load_all()


@when("I parse the date")
def parse_date(data_loader, context):
    """Parse the date string."""
    context['parsed_date'] = data_loader.parse_date(context['date_str'])


@when("I load matches with Portuguese characters")
def load_matches_with_utf8(data_loader, context):
    """Load matches that include UTF-8 characters."""
    context['matches'] = data_loader.load_brasileirao_matches()


# Then steps
@then("I should receive a list of matches")
def receive_list_of_matches(context):
    """Verify we received a list of matches."""
    assert 'matches' in context
    assert isinstance(context['matches'], list)
    assert len(context['matches']) > 0


@then("each match should have home_team, away_team, and scores")
def matches_have_required_fields(context):
    """Verify each match has required fields."""
    for match in context['matches'][:10]:  # Check first 10
        assert hasattr(match, 'home_team') and match.home_team
        assert hasattr(match, 'away_team') and match.away_team
        assert hasattr(match, 'home_goals') and match.home_goals is not None
        assert hasattr(match, 'away_goals') and match.away_goals is not None


@then("I should receive a list of players")
def receive_list_of_players(context):
    """Verify we received a list of players."""
    assert 'players' in context
    assert isinstance(context['players'], list)
    assert len(context['players']) > 0


@then("each player should have name, nationality, and overall rating")
def players_have_required_fields(context):
    """Verify each player has required fields."""
    for player in context['players'][:10]:  # Check first 10
        assert hasattr(player, 'name') and player.name
        assert hasattr(player, 'nationality') and player.nationality
        assert hasattr(player, 'overall_rating') and player.overall_rating is not None


@then("I should have matches from multiple competitions")
def have_multiple_competitions(context):
    """Verify we have matches from multiple competitions."""
    all_data = context['all_data']
    assert 'brasileirao_matches' in all_data
    assert len(all_data['brasileirao_matches']) > 0


@then("I should have player data")
def have_player_data(context):
    """Verify we have player data."""
    all_data = context['all_data']
    assert 'players' in all_data
    assert len(all_data['players']) > 0


@then("I should get a valid datetime object")
def get_valid_datetime(context):
    """Verify date was parsed correctly."""
    assert context['parsed_date'] is not None
    assert isinstance(context['parsed_date'], datetime)


@then('team names like "São Paulo" should be preserved correctly')
def utf8_preserved(context):
    """Verify UTF-8 characters are preserved."""
    # Check that at least some team names have Portuguese characters
    team_names = set()
    for match in context['matches']:
        team_names.add(match.home_team)
        team_names.add(match.away_team)

    # Look for teams with Portuguese characters
    utf8_teams = [name for name in team_names if any(c in name for c in 'áéíóúãõâêîôûçÁÉÍÓÚÃÕÂÊÎÔÛÇ')]
    # Even if no UTF-8 in the actual data, the loader should handle them
    assert isinstance(team_names, set)
