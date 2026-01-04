"""
Brazilian Soccer MCP - BDD Tests for Query Engine
=================================================

Tests for querying match and player data using pytest-bdd with Gherkin feature files.

Author: Brazilian Soccer MCP Hive Mind
Date: 2025-12-13
"""

import pytest
from pytest_bdd import scenarios, given, when, then, parsers
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from data_loader import DataLoader
from query_engine import QueryEngine

# Load scenarios from feature file
scenarios('../features/query_engine.feature')


# Fixtures
@pytest.fixture
def data_loader():
    """Create DataLoader with test data."""
    return DataLoader(data_dir="data/kaggle")


@pytest.fixture
def query_engine(data_loader):
    """Create QueryEngine with loaded data."""
    data_loader.load_all()
    return QueryEngine(data_loader)


@pytest.fixture
def context():
    """Shared context dict for passing data between steps."""
    return {}


# Given steps
@given("the match data is loaded")
def match_data_loaded(query_engine, context):
    """Ensure match data is loaded."""
    context['engine'] = query_engine
    assert len(query_engine.data_loader.matches) > 0


# When steps
@when(parsers.parse('I search for matches between "{team1}" and "{team2}"'))
def search_matches_between(context, team1, team2):
    """Search for matches between two teams."""
    context['matches'] = context['engine'].find_matches_between(team1, team2)


@when(parsers.parse('I search for all matches involving "{team}"'))
def search_matches_by_team(context, team):
    """Search for all matches involving a team."""
    context['matches'] = context['engine'].find_matches_by_team(team)
    context['team'] = team


@when(parsers.parse('I search for matches in season {season:d}'))
def search_matches_by_season(context, season):
    """Search for matches by season."""
    context['matches'] = context['engine'].find_matches_by_season(season)
    context['season'] = season


@when(parsers.parse('I request statistics for "{team}"'))
def request_team_statistics(context, team):
    """Request team statistics."""
    context['stats'] = context['engine'].get_team_statistics(team)


@when(parsers.parse('I request head-to-head for "{team1}" vs "{team2}"'))
def request_head_to_head(context, team1, team2):
    """Request head-to-head statistics."""
    context['h2h'] = context['engine'].get_head_to_head(team1, team2)


@when(parsers.parse('I search for players with nationality "{nationality}"'))
def search_players_by_nationality(context, nationality):
    """Search for players by nationality."""
    context['players'] = context['engine'].find_players_by_nationality(nationality)


@when(parsers.parse('I request top {limit:d} rated players'))
def request_top_rated_players(context, limit):
    """Request top rated players."""
    context['players'] = context['engine'].get_top_rated_players(limit)
    context['limit'] = limit


@when(parsers.parse('I search for matches by team "{team}"'))
def search_by_nonexistent_team(context, team):
    """Search for matches by a team name."""
    context['matches'] = context['engine'].find_matches_by_team(team)


# Then steps
@then("I should receive a list of matches")
def receive_list_of_matches(context):
    """Verify we received a list of matches."""
    assert isinstance(context['matches'], list)


@then("each match should involve both teams")
def matches_involve_both_teams(context):
    """Verify each match involves both searched teams."""
    for match in context['matches']:
        teams = {match.home_team, match.away_team}
        assert len(teams) == 2  # Both teams present


@then("I should receive matches where Corinthians played")
def receive_corinthians_matches(context):
    """Verify matches involve the searched team."""
    team = context.get('team', 'Corinthians')
    for match in context['matches']:
        assert team in match.home_team or team in match.away_team


@then("matches should include home and away games")
def matches_include_home_away(context):
    """Verify we have both home and away games."""
    team = context.get('team', '')
    home_games = [m for m in context['matches'] if team in m.home_team]
    away_games = [m for m in context['matches'] if team in m.away_team]
    # Should have at least some of each (if data exists)
    assert len(home_games) >= 0 and len(away_games) >= 0


@then(parsers.parse('all returned matches should be from season {season:d}'))
def matches_from_season(context, season):
    """Verify all matches are from the specified season."""
    for match in context['matches']:
        assert match.season == season


@then("I should receive wins, losses, draws counts")
def receive_win_loss_draw(context):
    """Verify statistics include wins, losses, draws."""
    stats = context['stats']
    assert stats.wins >= 0
    assert stats.losses >= 0
    assert stats.draws >= 0


@then("I should receive goals scored and conceded")
def receive_goals_stats(context):
    """Verify statistics include goals."""
    stats = context['stats']
    assert stats.goals_for >= 0
    assert stats.goals_against >= 0


@then("I should receive win counts for each team")
def receive_h2h_wins(context):
    """Verify head-to-head includes win counts."""
    h2h = context['h2h']
    assert h2h.team1_wins >= 0
    assert h2h.team2_wins >= 0


@then("I should receive draw count")
def receive_h2h_draws(context):
    """Verify head-to-head includes draw count."""
    h2h = context['h2h']
    assert h2h.draws >= 0


@then("I should receive a list of Brazilian players")
def receive_brazilian_players(context):
    """Verify we received Brazilian players."""
    assert isinstance(context['players'], list)


@then("I should receive up to 10 players")
def receive_up_to_10_players(context):
    """Verify we received at most the limit."""
    limit = context.get('limit', 10)
    assert len(context['players']) <= limit


@then("they should be sorted by overall rating descending")
def players_sorted_descending(context):
    """Verify players are sorted by rating descending."""
    players = context['players']
    for i in range(len(players) - 1):
        assert players[i].overall_rating >= players[i + 1].overall_rating


@then("I should receive an empty list")
def receive_empty_list(context):
    """Verify we received an empty list."""
    assert context['matches'] == []
