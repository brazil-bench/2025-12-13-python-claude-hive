"""
Brazilian Soccer MCP Server - MCP Protocol Implementation
=========================================================

Purpose: Expose query engine as MCP (Model Context Protocol) tools
Author: Brazilian Soccer MCP Hive Mind
Date: 2025-12-13
Dependencies: fastmcp, data_loader, query_engine

This server exposes the Brazilian soccer query engine as MCP tools
that can be called by AI assistants to answer questions about:
- Match results and history
- Team statistics and comparisons
- Player information and ratings
- Competition standings

MCP Tools Exposed:
- search_matches: Find matches between teams
- get_team_stats: Get team statistics
- search_players: Find players by criteria
- get_standings: Get competition standings
- get_head_to_head: Compare two teams
"""

from typing import Optional, List, Dict, Any
import json
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.dirname(__file__))

from data_loader import DataLoader
from query_engine import QueryEngine
from models import Match, Player


class BrazilianSoccerMCP:
    """
    MCP Server for Brazilian Soccer data.

    Provides tool handlers that wrap the query engine functionality
    and expose it through the MCP protocol.
    """

    def __init__(self, data_dir: str = "data/kaggle"):
        """
        Initialize MCP server with data.

        Args:
            data_dir: Directory containing CSV data files
        """
        self.data_loader = DataLoader(data_dir=data_dir)
        self.data_loader.load_all()
        self.query_engine = QueryEngine(self.data_loader)

    def _match_to_dict(self, match: Match) -> Dict[str, Any]:
        """Convert Match object to dictionary for JSON response."""
        return {
            "date": str(match.datetime) if match.datetime else None,
            "home_team": match.home_team,
            "away_team": match.away_team,
            "home_goals": match.home_goals,
            "away_goals": match.away_goals,
            "competition": match.competition,
            "season": match.season,
            "round": match.round,
            "stadium": match.stadium
        }

    def _player_to_dict(self, player: Player) -> Dict[str, Any]:
        """Convert Player object to dictionary for JSON response."""
        return {
            "id": player.id,
            "name": player.name,
            "age": player.age,
            "nationality": player.nationality,
            "club": player.club,
            "position": player.position,
            "overall_rating": player.overall_rating,
            "potential": player.potential
        }

    # ==================== MCP TOOL HANDLERS ====================

    def search_matches(
        self,
        team1: Optional[str] = None,
        team2: Optional[str] = None,
        team: Optional[str] = None,
        season: Optional[int] = None,
        competition: Optional[str] = None,
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        Search for matches based on various criteria.

        Args:
            team1: First team for head-to-head search
            team2: Second team for head-to-head search
            team: Single team to find all their matches
            season: Filter by season year
            competition: Filter by competition name
            limit: Maximum number of results

        Returns:
            Dictionary with matches list and count
        """
        matches = []

        if team1 and team2:
            # Head-to-head search
            matches = self.query_engine.find_matches_between(team1, team2)
        elif team:
            # Single team search
            matches = self.query_engine.find_matches_by_team(team)
        elif season:
            # Season search
            matches = self.query_engine.find_matches_by_season(season)
        elif competition:
            # Competition search
            matches = self.query_engine.find_matches_by_competition(competition)
        else:
            # Return recent matches
            matches = self.query_engine.data_loader.matches[:limit]

        # Apply limit and convert to dict
        result_matches = [self._match_to_dict(m) for m in matches[:limit]]

        return {
            "matches": result_matches,
            "count": len(result_matches),
            "total_found": len(matches)
        }

    def get_team_stats(
        self,
        team: str,
        season: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get statistics for a team.

        Args:
            team: Team name
            season: Optional season to filter by

        Returns:
            Dictionary with team statistics
        """
        stats = self.query_engine.get_team_statistics(team, season)

        return {
            "team": team,
            "season": season,
            "matches": stats.matches,
            "wins": stats.wins,
            "draws": stats.draws,
            "losses": stats.losses,
            "goals_for": stats.goals_for,
            "goals_against": stats.goals_against,
            "goal_difference": stats.goal_difference,
            "points": stats.points,
            "win_percentage": stats.win_percentage
        }

    def search_players(
        self,
        name: Optional[str] = None,
        nationality: Optional[str] = None,
        club: Optional[str] = None,
        min_rating: Optional[int] = None,
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        Search for players based on various criteria.

        Args:
            name: Player name (partial match)
            nationality: Filter by nationality
            club: Filter by club
            min_rating: Minimum overall rating
            limit: Maximum number of results

        Returns:
            Dictionary with players list and count
        """
        players = []

        if name:
            players = self.query_engine.find_players_by_name(name)
        elif nationality:
            players = self.query_engine.find_players_by_nationality(nationality)
        elif club:
            players = self.query_engine.find_players_by_club(club)
        else:
            players = self.query_engine.get_top_rated_players(limit)

        # Apply min_rating filter if specified
        if min_rating:
            players = [p for p in players if p.overall_rating >= min_rating]

        # Convert to dict
        result_players = [self._player_to_dict(p) for p in players[:limit]]

        return {
            "players": result_players,
            "count": len(result_players)
        }

    def get_head_to_head(
        self,
        team1: str,
        team2: str
    ) -> Dict[str, Any]:
        """
        Get head-to-head statistics between two teams.

        Args:
            team1: First team name
            team2: Second team name

        Returns:
            Dictionary with head-to-head statistics
        """
        h2h = self.query_engine.get_head_to_head(team1, team2)
        matches = self.query_engine.find_matches_between(team1, team2)

        return {
            "team1": team1,
            "team2": team2,
            "team1_wins": h2h.team1_wins,
            "team2_wins": h2h.team2_wins,
            "draws": h2h.draws,
            "total_matches": h2h.total_matches,
            "recent_matches": [self._match_to_dict(m) for m in matches[:5]]
        }

    def get_standings(
        self,
        competition: str,
        season: int
    ) -> Dict[str, Any]:
        """
        Get competition standings for a season.

        Args:
            competition: Competition name
            season: Season year

        Returns:
            Dictionary with standings table
        """
        standings = self.query_engine.get_competition_standings(competition, season)

        return {
            "competition": competition,
            "season": season,
            "standings": [
                {
                    "position": i + 1,
                    "team": s.team,
                    "matches": s.matches,
                    "wins": s.wins,
                    "draws": s.draws,
                    "losses": s.losses,
                    "goals_for": s.gf,
                    "goals_against": s.ga,
                    "goal_difference": s.gd,
                    "points": s.points
                }
                for i, s in enumerate(standings)
            ]
        }

    def get_biggest_wins(
        self,
        competition: Optional[str] = None,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Get the biggest wins in history.

        Args:
            competition: Optional competition filter
            limit: Maximum results

        Returns:
            Dictionary with biggest wins
        """
        matches = self.query_engine.get_biggest_wins(competition, limit)

        return {
            "biggest_wins": [
                {
                    **self._match_to_dict(m),
                    "goal_difference": abs(m.home_goals - m.away_goals)
                }
                for m in matches
            ]
        }

    def get_top_scorers(
        self,
        season: Optional[int] = None,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Get teams with most goals.

        Args:
            season: Optional season filter
            limit: Maximum results

        Returns:
            Dictionary with top scoring teams
        """
        top_teams = self.query_engine.get_top_teams_by_goals(season, limit)

        return {
            "season": season,
            "top_scorers": [
                {
                    "team": t.team,
                    "goals": t.goals_scored,
                    "matches": t.matches
                }
                for t in top_teams
            ]
        }


def create_mcp_server(data_dir: str = "data/kaggle") -> BrazilianSoccerMCP:
    """
    Factory function to create MCP server instance.

    Args:
        data_dir: Directory containing CSV data files

    Returns:
        Configured BrazilianSoccerMCP instance
    """
    return BrazilianSoccerMCP(data_dir=data_dir)


# Main entry point for running as MCP server
if __name__ == "__main__":
    try:
        from mcp.server import Server
        from mcp.server.stdio import stdio_server

        # Create server
        server = Server("brazilian-soccer-mcp")
        mcp = create_mcp_server()

        @server.list_tools()
        async def list_tools():
            return [
                {
                    "name": "search_matches",
                    "description": "Search for Brazilian soccer matches",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "team1": {"type": "string", "description": "First team for head-to-head"},
                            "team2": {"type": "string", "description": "Second team for head-to-head"},
                            "team": {"type": "string", "description": "Single team to search"},
                            "season": {"type": "integer", "description": "Season year"},
                            "competition": {"type": "string", "description": "Competition name"},
                            "limit": {"type": "integer", "description": "Max results", "default": 20}
                        }
                    }
                },
                {
                    "name": "get_team_stats",
                    "description": "Get statistics for a team",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "team": {"type": "string", "description": "Team name"},
                            "season": {"type": "integer", "description": "Season year"}
                        },
                        "required": ["team"]
                    }
                },
                {
                    "name": "search_players",
                    "description": "Search for FIFA players",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "Player name"},
                            "nationality": {"type": "string", "description": "Nationality"},
                            "club": {"type": "string", "description": "Club name"},
                            "min_rating": {"type": "integer", "description": "Min overall rating"},
                            "limit": {"type": "integer", "description": "Max results", "default": 20}
                        }
                    }
                },
                {
                    "name": "get_head_to_head",
                    "description": "Get head-to-head stats between two teams",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "team1": {"type": "string", "description": "First team"},
                            "team2": {"type": "string", "description": "Second team"}
                        },
                        "required": ["team1", "team2"]
                    }
                },
                {
                    "name": "get_standings",
                    "description": "Get competition standings",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "competition": {"type": "string", "description": "Competition name"},
                            "season": {"type": "integer", "description": "Season year"}
                        },
                        "required": ["competition", "season"]
                    }
                }
            ]

        @server.call_tool()
        async def call_tool(name: str, arguments: dict):
            if name == "search_matches":
                return mcp.search_matches(**arguments)
            elif name == "get_team_stats":
                return mcp.get_team_stats(**arguments)
            elif name == "search_players":
                return mcp.search_players(**arguments)
            elif name == "get_head_to_head":
                return mcp.get_head_to_head(**arguments)
            elif name == "get_standings":
                return mcp.get_standings(**arguments)
            else:
                raise ValueError(f"Unknown tool: {name}")

        # Run server
        stdio_server(server)

    except ImportError:
        print("MCP package not installed. Install with: pip install mcp")
        print("Running in standalone mode...")

        # Standalone test
        mcp = create_mcp_server()
        print(json.dumps(mcp.search_matches(team="Flamengo", limit=5), indent=2))
