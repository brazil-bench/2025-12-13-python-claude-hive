"""
Brazilian Soccer MCP Server - Data Models

Purpose: Define core data structures for soccer matches, teams, and players
Author: Claude Code - CODER Agent
Date: 2025-12-13
Dependencies: dataclasses, datetime, typing
Key Functions: Team, Player, Match, Competition dataclasses

These models represent the fundamental entities in Brazilian soccer:
- Team: Represents a soccer club with name, state, and aliases
- Player: FIFA player data with ratings and attributes
- Match: Game results with teams, scores, and metadata
- Competition: Tournament/league information (Brasileirão, Copa do Brasil, etc.)
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any


@dataclass
class Team:
    """
    Represents a Brazilian soccer team

    Attributes:
        name: Official team name (normalized)
        state: Brazilian state abbreviation (SP, RJ, MG, etc.)
        aliases: Common variations of team name
    """
    name: str
    state: Optional[str] = None
    aliases: List[str] = field(default_factory=list)

    def __str__(self) -> str:
        return f"{self.name} ({self.state})" if self.state else self.name

    def __hash__(self) -> int:
        return hash(self.name)


@dataclass
class Player:
    """
    Represents a soccer player with FIFA ratings

    Attributes:
        id: Unique player identifier
        name: Player's full name
        nationality: Country of origin
        club: Current team name
        overall_rating: FIFA overall rating (0-100)
        position: Playing position (GK, CB, ST, etc.)
        attributes: Additional player stats (pace, shooting, passing, etc.)
    """
    id: int
    name: str
    nationality: str
    club: Optional[str] = None
    overall_rating: Optional[int] = None
    position: Optional[str] = None
    attributes: Dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        return f"{self.name} ({self.club or 'No Club'}) - {self.overall_rating or 'N/A'}"

    def __hash__(self) -> int:
        return hash(self.id)


@dataclass
class Match:
    """
    Represents a soccer match result

    Attributes:
        datetime: Match date and time
        home_team: Home team name (normalized)
        away_team: Away team name (normalized)
        home_goals: Goals scored by home team
        away_goals: Goals scored by away team
        competition: Competition name (Brasileirão Série A, Copa do Brasil, etc.)
        season: Year of the season
        round: Round/matchday number or description
        stadium: Stadium name where match was played
    """
    datetime: datetime
    home_team: str
    away_team: str
    home_goals: int
    away_goals: int
    competition: str
    season: int
    round: Optional[str] = None
    stadium: Optional[str] = None

    @property
    def result(self) -> str:
        """Returns match result from home team perspective (Win/Draw/Loss)"""
        if self.home_goals > self.away_goals:
            return "Win"
        elif self.home_goals < self.away_goals:
            return "Loss"
        return "Draw"

    @property
    def total_goals(self) -> int:
        """Returns total goals scored in the match"""
        return self.home_goals + self.away_goals

    def __str__(self) -> str:
        return f"{self.home_team} {self.home_goals}-{self.away_goals} {self.away_team} ({self.competition} {self.season})"


@dataclass
class Competition:
    """
    Represents a soccer competition/tournament

    Attributes:
        name: Official competition name
        type: Competition type (league or cup)
    """
    name: str
    type: str  # "league" or "cup"

    def __str__(self) -> str:
        return f"{self.name} ({self.type})"

    def __hash__(self) -> int:
        return hash(self.name)

    @property
    def is_league(self) -> bool:
        """Returns True if competition is a league format"""
        return self.type.lower() == "league"

    @property
    def is_cup(self) -> bool:
        """Returns True if competition is a cup/knockout format"""
        return self.type.lower() == "cup"


# Predefined competition constants
BRASILEIRAO_SERIE_A = Competition("Brasileirão Série A", "league")
COPA_DO_BRASIL = Competition("Copa do Brasil", "cup")
COPA_LIBERTADORES = Competition("Copa Libertadores", "cup")
