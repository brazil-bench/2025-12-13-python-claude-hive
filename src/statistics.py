"""
Brazilian Soccer MCP - Statistics Data Models

This module defines dataclasses for statistical data returned by query operations.
Provides structured representations of team statistics, head-to-head records,
competition standings, and other analytical data.

Context:
- Part of PHASE 2: Query Engine implementation
- Used by QueryEngine to return structured statistical data
- Designed for easy serialization to JSON for MCP responses

Author: Brazilian Soccer MCP Hive Mind - Coder Agent
Date: 2025-12-13
"""

from dataclasses import dataclass, asdict
from typing import Dict, Any


@dataclass
class TeamStats:
    """
    Comprehensive team statistics for a season or all-time.

    Attributes:
        team: Team name
        matches: Total matches played
        wins: Total wins
        draws: Total draws
        losses: Total losses
        goals_for: Goals scored
        goals_against: Goals conceded
        points: Total points (3 for win, 1 for draw)
        clean_sheets: Matches without conceding
        season: Season year (None for all-time stats)
    """
    team: str
    matches: int
    wins: int
    draws: int
    losses: int
    goals_for: int
    goals_against: int
    points: int
    clean_sheets: int = 0
    season: int = None

    @property
    def goal_difference(self) -> int:
        """Calculate goal difference."""
        return self.goals_for - self.goals_against

    @property
    def win_percentage(self) -> float:
        """Calculate win percentage."""
        return (self.wins / self.matches * 100) if self.matches > 0 else 0.0

    @property
    def average_goals_scored(self) -> float:
        """Calculate average goals scored per match."""
        return self.goals_for / self.matches if self.matches > 0 else 0.0

    @property
    def average_goals_conceded(self) -> float:
        """Calculate average goals conceded per match."""
        return self.goals_against / self.matches if self.matches > 0 else 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with computed properties."""
        data = asdict(self)
        data['goal_difference'] = self.goal_difference
        data['win_percentage'] = round(self.win_percentage, 2)
        data['average_goals_scored'] = round(self.average_goals_scored, 2)
        data['average_goals_conceded'] = round(self.average_goals_conceded, 2)
        return data


@dataclass
class HeadToHeadStats:
    """
    Head-to-head statistics between two teams.

    Attributes:
        team1: First team name
        team2: Second team name
        team1_wins: Number of wins for team1
        team2_wins: Number of wins for team2
        draws: Number of draws
        total_matches: Total matches played
        team1_goals: Total goals scored by team1
        team2_goals: Total goals scored by team2
    """
    team1: str
    team2: str
    team1_wins: int
    team2_wins: int
    draws: int
    total_matches: int
    team1_goals: int = 0
    team2_goals: int = 0

    @property
    def team1_win_percentage(self) -> float:
        """Calculate team1 win percentage."""
        return (self.team1_wins / self.total_matches * 100) if self.total_matches > 0 else 0.0

    @property
    def team2_win_percentage(self) -> float:
        """Calculate team2 win percentage."""
        return (self.team2_wins / self.total_matches * 100) if self.total_matches > 0 else 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with computed properties."""
        data = asdict(self)
        data['team1_win_percentage'] = round(self.team1_win_percentage, 2)
        data['team2_win_percentage'] = round(self.team2_win_percentage, 2)
        return data


@dataclass
class Record:
    """
    Win/draw/loss record for a team.

    Attributes:
        team: Team name
        matches: Total matches
        wins: Total wins
        draws: Total draws
        losses: Total losses
        goals_for: Goals scored
        goals_against: Goals conceded
        context: Description of record (e.g., "Home matches in 2023")
    """
    team: str
    matches: int
    wins: int
    draws: int
    losses: int
    goals_for: int
    goals_against: int
    context: str = ""

    @property
    def points(self) -> int:
        """Calculate total points."""
        return self.wins * 3 + self.draws

    @property
    def win_percentage(self) -> float:
        """Calculate win percentage."""
        return (self.wins / self.matches * 100) if self.matches > 0 else 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with computed properties."""
        data = asdict(self)
        data['points'] = self.points
        data['win_percentage'] = round(self.win_percentage, 2)
        return data


@dataclass
class Standing:
    """
    Competition standing for a team.

    Attributes:
        position: League position
        team: Team name
        points: Total points
        matches: Matches played
        wins: Total wins
        draws: Total draws
        losses: Total losses
        gf: Goals for
        ga: Goals against
        gd: Goal difference
    """
    position: int
    team: str
    points: int
    matches: int
    wins: int
    draws: int
    losses: int
    gf: int
    ga: int
    gd: int

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class TeamGoalStats:
    """
    Team goal statistics for ranking purposes.

    Attributes:
        team: Team name
        goals_scored: Total goals scored
        matches: Matches played
        season: Season year
    """
    team: str
    goals_scored: int
    matches: int
    season: int

    @property
    def goals_per_match(self) -> float:
        """Calculate goals per match."""
        return self.goals_scored / self.matches if self.matches > 0 else 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with computed properties."""
        data = asdict(self)
        data['goals_per_match'] = round(self.goals_per_match, 2)
        return data
