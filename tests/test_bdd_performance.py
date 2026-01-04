"""
Brazilian Soccer MCP - BDD Tests for Performance
=================================================

Tests for verifying query performance meets requirements:
- Simple lookups < 2 seconds
- Aggregate queries < 5 seconds

Author: Brazilian Soccer MCP Hive Mind
Date: 2025-12-13
"""

import pytest
from pytest_bdd import scenarios, given, when, then, parsers
import time
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from data_loader import DataLoader
from query_engine import QueryEngine

# Load scenarios from feature file
scenarios('../features/performance.feature')


# Fixtures
@pytest.fixture
def data_loader():
    """Create DataLoader with test data."""
    loader = DataLoader(data_dir="data/kaggle")
    loader.load_all()
    return loader


@pytest.fixture
def query_engine(data_loader):
    """Create QueryEngine with loaded data."""
    return QueryEngine(data_loader)


@pytest.fixture
def context():
    """Shared context dict for passing data between steps."""
    return {}


# Given steps
@given("all datasets are loaded")
def all_datasets_loaded(data_loader, query_engine, context):
    """Ensure all datasets are loaded."""
    context['loader'] = data_loader
    context['engine'] = query_engine
    assert len(data_loader.matches) > 0


# When steps
@when(parsers.parse('I search for player "{player_name}"'))
def search_player_timed(context, player_name):
    """Search for player and time it."""
    start = time.time()
    context['result'] = context['engine'].find_players_by_name(player_name)
    context['elapsed'] = time.time() - start


@when(parsers.parse('I calculate statistics for "{team}"'))
def calculate_stats_timed(context, team):
    """Calculate team statistics and time it."""
    start = time.time()
    context['result'] = context['engine'].get_team_statistics(team)
    context['elapsed'] = time.time() - start


@when(parsers.parse('I search for matches between "{team1}" and "{team2}"'))
def search_matches_timed(context, team1, team2):
    """Search for matches and time it."""
    start = time.time()
    context['result'] = context['engine'].find_matches_between(team1, team2)
    context['elapsed'] = time.time() - start


@when(parsers.parse('I calculate league standings for season {season:d}'))
def calculate_standings_timed(context, season):
    """Calculate standings and time it."""
    start = time.time()
    context['result'] = context['engine'].get_competition_standings("Brasileirão", season)
    context['elapsed'] = time.time() - start


@when(parsers.parse('I calculate head-to-head for "{team1}" vs "{team2}"'))
def calculate_h2h_timed(context, team1, team2):
    """Calculate head-to-head and time it."""
    start = time.time()
    context['result'] = context['engine'].get_head_to_head(team1, team2)
    context['elapsed'] = time.time() - start


# Then steps
@then("the query should complete in less than 2 seconds")
def query_under_2_seconds(context):
    """Verify query completed in under 2 seconds."""
    elapsed = context['elapsed']
    assert elapsed < 2.0, f"Query took {elapsed:.2f}s, expected < 2s"


@then("the query should complete in less than 5 seconds")
def query_under_5_seconds(context):
    """Verify query completed in under 5 seconds."""
    elapsed = context['elapsed']
    assert elapsed < 5.0, f"Query took {elapsed:.2f}s, expected < 5s"
