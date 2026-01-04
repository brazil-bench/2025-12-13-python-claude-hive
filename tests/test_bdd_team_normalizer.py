"""
Brazilian Soccer MCP - BDD Tests for Team Name Normalization
============================================================

Tests for normalizing team names using pytest-bdd with Gherkin feature files.

Author: Brazilian Soccer MCP Hive Mind
Date: 2025-12-13
"""

import pytest
from pytest_bdd import scenarios, given, when, then, parsers
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from team_normalizer import TeamNormalizer

# Load scenarios from feature file
scenarios('../features/team_normalizer.feature')


# Fixtures
@pytest.fixture
def normalizer():
    """Create TeamNormalizer instance."""
    return TeamNormalizer()


@pytest.fixture
def context():
    """Shared context dict for passing data between steps."""
    return {}


# Given steps
@given(parsers.parse('a team name "{team_name}"'))
def team_name_input(context, team_name):
    """Store team name input in context."""
    context['input'] = team_name


# When steps
@when("I normalize the team name")
def normalize_team_name(normalizer, context):
    """Normalize the team name."""
    context['result'] = normalizer.normalize(context['input'])


# Then steps
@then(parsers.parse('I should get "{expected}"'))
def should_get_expected(context, expected):
    """Verify normalized result matches expected."""
    assert context['result'] == expected, f"Expected '{expected}', got '{context['result']}'"
