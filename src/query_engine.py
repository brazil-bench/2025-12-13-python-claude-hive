"""
Brazilian Soccer MCP - Query Engine

This module implements the core query engine for answering questions about
Brazilian soccer matches, teams, players, and statistics. Provides efficient
data retrieval through indexed lookups and fuzzy matching.

Context:
- Part of PHASE 2: Query Engine implementation
- Uses DataLoader to access match and player data
- Implements fuzzy team name matching for flexible queries
- Optimized with indexes for fast lookups

Key Features:
- Match queries (by team, date, competition, season)
- Team statistics (records, head-to-head, rankings)
- Player queries (by name, nationality, club, rating)
- Statistical analysis (standings, biggest wins, averages)

Author: Brazilian Soccer MCP Hive Mind - Coder Agent
Date: 2025-12-13
"""

from typing import List, Optional, Dict, Set
from datetime import datetime
from collections import defaultdict
from difflib import get_close_matches

from models import Match, Player
from data_loader import DataLoader
from statistics import (
    TeamStats, HeadToHeadStats, Record, Standing, TeamGoalStats
)


class QueryEngine:
    """
    Main query engine for Brazilian soccer data.

    Provides efficient querying of matches, teams, and players with
    fuzzy matching support for team names and optimized indexes.
    """

    def __init__(self, data_loader: DataLoader):
        """
        Initialize query engine with data loader.

        Args:
            data_loader: DataLoader instance with loaded data
        """
        self.data_loader = data_loader
        self._build_indexes()

    def _build_indexes(self):
        """Build indexes for efficient querying."""
        # Team name index for fuzzy matching
        self.team_names: Set[str] = set()

        # Match indexes
        self.matches_by_team: Dict[str, List[Match]] = defaultdict(list)
        self.matches_by_competition: Dict[str, List[Match]] = defaultdict(list)
        self.matches_by_season: Dict[int, List[Match]] = defaultdict(list)

        # Build indexes from matches
        for match in self.data_loader.matches:
            # Team names
            self.team_names.add(match.home_team)
            self.team_names.add(match.away_team)

            # Team index
            self.matches_by_team[match.home_team].append(match)
            self.matches_by_team[match.away_team].append(match)

            # Competition index
            self.matches_by_competition[match.competition].append(match)

            # Season index
            self.matches_by_season[match.season].append(match)

    def _fuzzy_match_team(self, team_name: str, cutoff: float = 0.6) -> Optional[str]:
        """
        Find closest matching team name using fuzzy matching.

        Args:
            team_name: Team name to match
            cutoff: Minimum similarity ratio (0.0 to 1.0)

        Returns:
            Matched team name or None if no match found
        """
        matches = get_close_matches(team_name, self.team_names, n=1, cutoff=cutoff)
        return matches[0] if matches else None

    # ==================== MATCH QUERIES ====================

    def find_matches_between(self, team1: str, team2: str) -> List[Match]:
        """
        Find all matches between two teams.

        Args:
            team1: First team name
            team2: Second team name

        Returns:
            List of matches between the teams
        """
        # Fuzzy match team names
        t1 = self._fuzzy_match_team(team1)
        t2 = self._fuzzy_match_team(team2)

        if not t1 or not t2:
            return []

        matches = []
        for match in self.matches_by_team[t1]:
            if (match.home_team == t2 or match.away_team == t2):
                matches.append(match)

        return sorted(matches, key=lambda m: m.date)

    def find_matches_by_team(
        self,
        team: str,
        home_only: bool = False,
        away_only: bool = False
    ) -> List[Match]:
        """
        Find all matches for a team.

        Args:
            team: Team name
            home_only: Only return home matches
            away_only: Only return away matches

        Returns:
            List of matches for the team
        """
        team_name = self._fuzzy_match_team(team)
        if not team_name:
            return []

        matches = self.matches_by_team[team_name]

        if home_only:
            matches = [m for m in matches if m.home_team == team_name]
        elif away_only:
            matches = [m for m in matches if m.away_team == team_name]

        return sorted(matches, key=lambda m: m.date)

    def find_matches_by_date_range(
        self,
        start: datetime,
        end: datetime
    ) -> List[Match]:
        """
        Find matches within a date range.

        Args:
            start: Start date
            end: End date

        Returns:
            List of matches in date range
        """
        matches = [
            m for m in self.data_loader.matches
            if start <= m.date <= end
        ]
        return sorted(matches, key=lambda m: m.date)

    def find_matches_by_competition(self, competition: str) -> List[Match]:
        """
        Find all matches in a competition.

        Args:
            competition: Competition name

        Returns:
            List of matches in competition
        """
        return sorted(
            self.matches_by_competition.get(competition, []),
            key=lambda m: m.date
        )

    def find_matches_by_season(self, season: int) -> List[Match]:
        """
        Find all matches in a season.

        Args:
            season: Season year

        Returns:
            List of matches in season
        """
        return sorted(
            self.matches_by_season.get(season, []),
            key=lambda m: m.date
        )

    # ==================== TEAM QUERIES ====================

    def get_team_statistics(
        self,
        team: str,
        season: int = None
    ) -> Optional[TeamStats]:
        """
        Get comprehensive statistics for a team.

        Args:
            team: Team name
            season: Season year (None for all-time)

        Returns:
            TeamStats object or None if team not found
        """
        team_name = self._fuzzy_match_team(team)
        if not team_name:
            return None

        matches = self.find_matches_by_team(team_name)

        if season:
            matches = [m for m in matches if m.season == season]

        if not matches:
            return TeamStats(
                team=team_name,
                matches=0,
                wins=0,
                draws=0,
                losses=0,
                goals_for=0,
                goals_against=0,
                points=0,
                season=season
            )

        wins = draws = losses = 0
        goals_for = goals_against = 0
        clean_sheets = 0

        for match in matches:
            is_home = match.home_team == team_name
            team_goals = match.home_score if is_home else match.away_score
            opponent_goals = match.away_score if is_home else match.home_score

            goals_for += team_goals
            goals_against += opponent_goals

            if opponent_goals == 0:
                clean_sheets += 1

            if team_goals > opponent_goals:
                wins += 1
            elif team_goals == opponent_goals:
                draws += 1
            else:
                losses += 1

        return TeamStats(
            team=team_name,
            matches=len(matches),
            wins=wins,
            draws=draws,
            losses=losses,
            goals_for=goals_for,
            goals_against=goals_against,
            points=wins * 3 + draws,
            clean_sheets=clean_sheets,
            season=season
        )

    def get_head_to_head(self, team1: str, team2: str) -> Optional[HeadToHeadStats]:
        """
        Get head-to-head statistics between two teams.

        Args:
            team1: First team name
            team2: Second team name

        Returns:
            HeadToHeadStats object or None if teams not found
        """
        t1 = self._fuzzy_match_team(team1)
        t2 = self._fuzzy_match_team(team2)

        if not t1 or not t2:
            return None

        matches = self.find_matches_between(t1, t2)

        if not matches:
            return HeadToHeadStats(
                team1=t1,
                team2=t2,
                team1_wins=0,
                team2_wins=0,
                draws=0,
                total_matches=0
            )

        t1_wins = t2_wins = draws = 0
        t1_goals = t2_goals = 0

        for match in matches:
            is_t1_home = match.home_team == t1
            t1_score = match.home_score if is_t1_home else match.away_score
            t2_score = match.away_score if is_t1_home else match.home_score

            t1_goals += t1_score
            t2_goals += t2_score

            if t1_score > t2_score:
                t1_wins += 1
            elif t2_score > t1_score:
                t2_wins += 1
            else:
                draws += 1

        return HeadToHeadStats(
            team1=t1,
            team2=t2,
            team1_wins=t1_wins,
            team2_wins=t2_wins,
            draws=draws,
            total_matches=len(matches),
            team1_goals=t1_goals,
            team2_goals=t2_goals
        )

    def get_team_home_record(
        self,
        team: str,
        season: int = None
    ) -> Optional[Record]:
        """
        Get home record for a team.

        Args:
            team: Team name
            season: Season year (None for all-time)

        Returns:
            Record object or None if team not found
        """
        team_name = self._fuzzy_match_team(team)
        if not team_name:
            return None

        matches = self.find_matches_by_team(team_name, home_only=True)

        if season:
            matches = [m for m in matches if m.season == season]

        wins = draws = losses = 0
        goals_for = goals_against = 0

        for match in matches:
            goals_for += match.home_score
            goals_against += match.away_score

            if match.home_score > match.away_score:
                wins += 1
            elif match.home_score == match.away_score:
                draws += 1
            else:
                losses += 1

        context = f"Home matches"
        if season:
            context += f" in {season}"

        return Record(
            team=team_name,
            matches=len(matches),
            wins=wins,
            draws=draws,
            losses=losses,
            goals_for=goals_for,
            goals_against=goals_against,
            context=context
        )

    def get_top_teams_by_goals(
        self,
        season: int,
        limit: int = 10
    ) -> List[TeamGoalStats]:
        """
        Get top teams by goals scored in a season.

        Args:
            season: Season year
            limit: Maximum number of teams to return

        Returns:
            List of TeamGoalStats ordered by goals scored
        """
        team_goals: Dict[str, Dict[str, int]] = defaultdict(lambda: {'goals': 0, 'matches': 0})

        for match in self.matches_by_season.get(season, []):
            team_goals[match.home_team]['goals'] += match.home_score
            team_goals[match.home_team]['matches'] += 1

            team_goals[match.away_team]['goals'] += match.away_score
            team_goals[match.away_team]['matches'] += 1

        rankings = [
            TeamGoalStats(
                team=team,
                goals_scored=stats['goals'],
                matches=stats['matches'],
                season=season
            )
            for team, stats in team_goals.items()
        ]

        return sorted(rankings, key=lambda x: x.goals_scored, reverse=True)[:limit]

    # ==================== PLAYER QUERIES ====================

    def find_players_by_name(self, name: str) -> List[Player]:
        """
        Find players by name (case-insensitive partial match).

        Args:
            name: Player name or partial name

        Returns:
            List of matching players
        """
        name_lower = name.lower()
        return [
            p for p in self.data_loader.players
            if name_lower in p.name.lower()
        ]

    def find_players_by_nationality(self, nationality: str) -> List[Player]:
        """
        Find players by nationality.

        Args:
            nationality: Nationality name

        Returns:
            List of players with matching nationality
        """
        nationality_lower = nationality.lower()
        return [
            p for p in self.data_loader.players
            if p.nationality and nationality_lower in p.nationality.lower()
        ]

    def find_players_by_club(self, club: str) -> List[Player]:
        """
        Find players by club.

        Args:
            club: Club name

        Returns:
            List of players at the club
        """
        club_match = self._fuzzy_match_team(club)
        if not club_match:
            return []

        return [
            p for p in self.data_loader.players
            if p.club == club_match
        ]

    def get_top_rated_players(self, limit: int = 10) -> List[Player]:
        """
        Get top-rated players.

        Args:
            limit: Maximum number of players to return

        Returns:
            List of top-rated players
        """
        players_with_rating = [
            p for p in self.data_loader.players
            if p.overall_rating is not None
        ]
        return sorted(
            players_with_rating,
            key=lambda p: p.overall_rating,
            reverse=True
        )[:limit]

    def get_brazilian_players_at_brazilian_clubs(self) -> List[Player]:
        """
        Get Brazilian players playing at Brazilian clubs.

        Returns:
            List of Brazilian players at Brazilian clubs
        """
        return [
            p for p in self.data_loader.players
            if p.nationality and 'brazil' in p.nationality.lower()
            and p.club in self.team_names
        ]

    # ==================== STATISTICAL QUERIES ====================

    def get_competition_standings(
        self,
        competition: str,
        season: int
    ) -> List[Standing]:
        """
        Calculate competition standings.

        Args:
            competition: Competition name
            season: Season year

        Returns:
            List of standings ordered by points
        """
        matches = [
            m for m in self.matches_by_competition.get(competition, [])
            if m.season == season
        ]

        if not matches:
            return []

        team_records: Dict[str, Dict[str, int]] = defaultdict(
            lambda: {
                'points': 0, 'matches': 0, 'wins': 0,
                'draws': 0, 'losses': 0, 'gf': 0, 'ga': 0
            }
        )

        for match in matches:
            # Home team
            home_record = team_records[match.home_team]
            home_record['matches'] += 1
            home_record['gf'] += match.home_score
            home_record['ga'] += match.away_score

            # Away team
            away_record = team_records[match.away_team]
            away_record['matches'] += 1
            away_record['gf'] += match.away_score
            away_record['ga'] += match.home_score

            # Determine winner
            if match.home_score > match.away_score:
                home_record['wins'] += 1
                home_record['points'] += 3
                away_record['losses'] += 1
            elif match.away_score > match.home_score:
                away_record['wins'] += 1
                away_record['points'] += 3
                home_record['losses'] += 1
            else:
                home_record['draws'] += 1
                home_record['points'] += 1
                away_record['draws'] += 1
                away_record['points'] += 1

        standings = [
            Standing(
                position=0,  # Will be set after sorting
                team=team,
                points=record['points'],
                matches=record['matches'],
                wins=record['wins'],
                draws=record['draws'],
                losses=record['losses'],
                gf=record['gf'],
                ga=record['ga'],
                gd=record['gf'] - record['ga']
            )
            for team, record in team_records.items()
        ]

        # Sort by points, then goal difference, then goals for
        standings.sort(
            key=lambda s: (s.points, s.gd, s.gf),
            reverse=True
        )

        # Assign positions
        for i, standing in enumerate(standings, 1):
            standing.position = i

        return standings

    def get_biggest_wins(
        self,
        competition: str = None,
        limit: int = 10
    ) -> List[Match]:
        """
        Get matches with biggest goal margins.

        Args:
            competition: Competition name (None for all competitions)
            limit: Maximum number of matches to return

        Returns:
            List of matches ordered by goal margin
        """
        matches = self.data_loader.matches

        if competition:
            matches = self.matches_by_competition.get(competition, [])

        return sorted(
            matches,
            key=lambda m: abs(m.home_score - m.away_score),
            reverse=True
        )[:limit]

    def get_average_goals_per_match(
        self,
        competition: str = None,
        season: int = None
    ) -> float:
        """
        Calculate average goals per match.

        Args:
            competition: Competition name (None for all)
            season: Season year (None for all)

        Returns:
            Average goals per match
        """
        matches = self.data_loader.matches

        if competition:
            matches = self.matches_by_competition.get(competition, [])

        if season:
            matches = [m for m in matches if m.season == season]

        if not matches:
            return 0.0

        total_goals = sum(m.home_score + m.away_score for m in matches)
        return total_goals / len(matches)
