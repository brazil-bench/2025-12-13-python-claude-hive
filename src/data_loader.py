"""
Brazilian Soccer MCP Server - Data Loader

Purpose: Load and parse CSV datasets for Brazilian soccer matches and players
Author: Claude Code - CODER Agent
Date: 2025-12-13
Dependencies: csv, datetime, pathlib, typing, models, team_normalizer
Key Functions: DataLoader class with methods for each dataset

Handles 6 CSV datasets:
1. brasileirao_matches.csv - Brasileirão Série A matches
2. copa_brasil_matches.csv - Copa do Brasil matches
3. libertadores_matches.csv - Copa Libertadores matches
4. extended_matches.csv - Extended match history
5. historical_matches.csv - Historical match data
6. fifa_players.csv - Player ratings and attributes

Features:
- UTF-8 encoding for Portuguese characters
- Multiple date format parsing
- Team name normalization
- Null/missing value handling
- Type-safe data structures
"""

import csv
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any
import logging

try:
    from .models import Team, Player, Match, Competition
    from .team_normalizer import TeamNormalizer
except ImportError:
    from models import Team, Player, Match, Competition
    from team_normalizer import TeamNormalizer


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataLoader:
    """
    Loads and parses Brazilian soccer data from CSV files

    Attributes:
        data_dir: Directory containing CSV data files
        normalizer: Team name normalizer instance
    """

    # Date format patterns to try
    DATE_FORMATS = [
        "%Y-%m-%d %H:%M:%S",  # 2023-05-15 19:30:00
        "%Y-%m-%d",            # 2023-05-15
        "%d/%m/%Y %H:%M",      # 15/05/2023 19:30
        "%d/%m/%Y",            # 15/05/2023
        "%d-%m-%Y",            # 15-05-2023
        "%Y/%m/%d",            # 2023/05/15
    ]

    def __init__(self, data_dir: str = "data"):
        """
        Initialize data loader

        Args:
            data_dir: Directory path containing CSV files
        """
        self.data_dir = Path(data_dir)
        self.normalizer = TeamNormalizer()

        if not self.data_dir.exists():
            logger.warning(f"Data directory does not exist: {self.data_dir}")

    def parse_date(self, date_str: str) -> Optional[datetime]:
        """
        Parse date string using multiple format attempts

        Args:
            date_str: Date string in various formats

        Returns:
            datetime object or None if parsing fails
        """
        if not date_str or date_str.strip() == "":
            return None

        date_str = date_str.strip()

        for fmt in self.DATE_FORMATS:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue

        logger.warning(f"Could not parse date: {date_str}")
        return None

    def normalize_team_name(self, name: str) -> str:
        """
        Normalize team name using TeamNormalizer

        Args:
            name: Raw team name

        Returns:
            Normalized team name
        """
        return self.normalizer.normalize(name)

    def _safe_int(self, value: Any, default: int = 0) -> int:
        """
        Safely convert value to integer

        Args:
            value: Value to convert
            default: Default value if conversion fails

        Returns:
            Integer value or default
        """
        if value is None or value == "":
            return default
        try:
            return int(value)
        except (ValueError, TypeError):
            logger.warning(f"Could not convert to int: {value}")
            return default

    def _safe_str(self, value: Any, default: str = "") -> str:
        """
        Safely convert value to string

        Args:
            value: Value to convert
            default: Default value if None

        Returns:
            String value or default
        """
        if value is None:
            return default
        return str(value).strip()

    def load_brasileirao_matches(self) -> List[Match]:
        """
        Load Brasileirão Série A matches

        Returns:
            List of Match objects
        """
        # Try multiple file names that might exist
        possible_files = [
            "Brasileirao_Matches.csv",
            "brasileirao_matches.csv",
            "novo_campeonato_brasileiro.csv"
        ]

        file_path = None
        for fname in possible_files:
            fp = self.data_dir / fname
            if fp.exists():
                file_path = fp
                break

        if not file_path:
            logger.error(f"No Brasileirão matches file found in {self.data_dir}")
            return []

        matches = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        # Handle different column names for date
                        date_str = row.get('datetime', row.get('date', row.get('Data', '')))
                        match_date = self.parse_date(date_str)
                        if not match_date:
                            continue

                        # Handle different column names for teams
                        home_team = row.get('home_team', row.get('home', row.get('Equipe_mandante', '')))
                        away_team = row.get('away_team', row.get('away', row.get('Equipe_visitante', '')))

                        # Handle different column names for goals (home_goal vs home_goals)
                        home_goals = self._safe_int(row.get('home_goal', row.get('home_goals', row.get('Gols_mandante', 0))))
                        away_goals = self._safe_int(row.get('away_goal', row.get('away_goals', row.get('Gols_visitante', 0))))

                        match = Match(
                            datetime=match_date,
                            home_team=self.normalize_team_name(home_team),
                            away_team=self.normalize_team_name(away_team),
                            home_goals=home_goals,
                            away_goals=away_goals,
                            competition="Brasileirão Série A",
                            season=self._safe_int(row.get('season', row.get('Ano', match_date.year))),
                            round=self._safe_str(row.get('round', row.get('Rodada', ''))),
                            stadium=self._safe_str(row.get('stadium', row.get('Arena', '')))
                        )
                        matches.append(match)
                    except Exception as e:
                        logger.error(f"Error parsing row: {e}")
                        continue

        except Exception as e:
            logger.error(f"Error loading Brasileirão matches: {e}")

        logger.info(f"Loaded {len(matches)} Brasileirão matches")
        return matches

    def load_copa_brasil_matches(self) -> List[Match]:
        """
        Load Copa do Brasil matches

        Returns:
            List of Match objects
        """
        possible_files = [
            "Brazilian_Cup_Matches.csv",
            "copa_brasil_matches.csv"
        ]

        file_path = None
        for fname in possible_files:
            fp = self.data_dir / fname
            if fp.exists():
                file_path = fp
                break

        if not file_path:
            logger.warning(f"No Copa do Brasil matches file found in {self.data_dir}")
            return []

        matches = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        date_str = row.get('datetime', row.get('date', ''))
                        match_date = self.parse_date(date_str)
                        if not match_date:
                            continue

                        home_goals = self._safe_int(row.get('home_goal', row.get('home_goals', 0)))
                        away_goals = self._safe_int(row.get('away_goal', row.get('away_goals', 0)))

                        match = Match(
                            datetime=match_date,
                            home_team=self.normalize_team_name(row.get('home_team', '')),
                            away_team=self.normalize_team_name(row.get('away_team', '')),
                            home_goals=home_goals,
                            away_goals=away_goals,
                            competition="Copa do Brasil",
                            season=self._safe_int(row.get('season', match_date.year)),
                            round=self._safe_str(row.get('round', '')),
                            stadium=self._safe_str(row.get('stadium', ''))
                        )
                        matches.append(match)
                    except Exception as e:
                        logger.error(f"Error parsing row: {e}")
                        continue

        except Exception as e:
            logger.error(f"Error loading Copa do Brasil matches: {e}")

        logger.info(f"Loaded {len(matches)} Copa do Brasil matches")
        return matches

    def load_libertadores_matches(self) -> List[Match]:
        """
        Load Copa Libertadores matches

        Returns:
            List of Match objects
        """
        possible_files = [
            "Libertadores_Matches.csv",
            "libertadores_matches.csv"
        ]

        file_path = None
        for fname in possible_files:
            fp = self.data_dir / fname
            if fp.exists():
                file_path = fp
                break

        if not file_path:
            logger.warning(f"No Libertadores matches file found in {self.data_dir}")
            return []

        matches = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        date_str = row.get('datetime', row.get('date', ''))
                        match_date = self.parse_date(date_str)
                        if not match_date:
                            continue

                        home_goals = self._safe_int(row.get('home_goal', row.get('home_goals', 0)))
                        away_goals = self._safe_int(row.get('away_goal', row.get('away_goals', 0)))

                        match = Match(
                            datetime=match_date,
                            home_team=self.normalize_team_name(row.get('home_team', '')),
                            away_team=self.normalize_team_name(row.get('away_team', '')),
                            home_goals=home_goals,
                            away_goals=away_goals,
                            competition="Copa Libertadores",
                            season=self._safe_int(row.get('season', match_date.year)),
                            round=self._safe_str(row.get('round', row.get('stage', ''))),
                            stadium=self._safe_str(row.get('stadium', ''))
                        )
                        matches.append(match)
                    except Exception as e:
                        logger.error(f"Error parsing row: {e}")
                        continue

        except Exception as e:
            logger.error(f"Error loading Libertadores matches: {e}")

        logger.info(f"Loaded {len(matches)} Libertadores matches")
        return matches

    def load_extended_matches(self) -> List[Match]:
        """
        Load extended match history

        Returns:
            List of Match objects
        """
        file_path = self.data_dir / "extended_matches.csv"
        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            return []

        matches = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        match_date = self.parse_date(row.get('date', ''))
                        if not match_date:
                            continue

                        match = Match(
                            datetime=match_date,
                            home_team=self.normalize_team_name(row.get('home_team', '')),
                            away_team=self.normalize_team_name(row.get('away_team', '')),
                            home_goals=self._safe_int(row.get('home_goals', 0)),
                            away_goals=self._safe_int(row.get('away_goals', 0)),
                            competition=self._safe_str(row.get('competition', 'Unknown')),
                            season=self._safe_int(row.get('season', match_date.year)),
                            round=self._safe_str(row.get('round')),
                            stadium=self._safe_str(row.get('stadium'))
                        )
                        matches.append(match)
                    except Exception as e:
                        logger.error(f"Error parsing row: {e}")
                        continue

        except Exception as e:
            logger.error(f"Error loading extended matches: {e}")

        logger.info(f"Loaded {len(matches)} extended matches")
        return matches

    def load_historical_matches(self) -> List[Match]:
        """
        Load historical match data

        Returns:
            List of Match objects
        """
        file_path = self.data_dir / "historical_matches.csv"
        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            return []

        matches = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        match_date = self.parse_date(row.get('date', ''))
                        if not match_date:
                            continue

                        match = Match(
                            datetime=match_date,
                            home_team=self.normalize_team_name(row.get('home_team', '')),
                            away_team=self.normalize_team_name(row.get('away_team', '')),
                            home_goals=self._safe_int(row.get('home_goals', 0)),
                            away_goals=self._safe_int(row.get('away_goals', 0)),
                            competition=self._safe_str(row.get('competition', 'Historical')),
                            season=self._safe_int(row.get('season', match_date.year)),
                            round=self._safe_str(row.get('round')),
                            stadium=self._safe_str(row.get('stadium'))
                        )
                        matches.append(match)
                    except Exception as e:
                        logger.error(f"Error parsing row: {e}")
                        continue

        except Exception as e:
            logger.error(f"Error loading historical matches: {e}")

        logger.info(f"Loaded {len(matches)} historical matches")
        return matches

    def load_fifa_players(self) -> List[Player]:
        """
        Load FIFA player data

        Returns:
            List of Player objects
        """
        possible_files = [
            "fifa_data.csv",
            "fifa_players.csv"
        ]

        file_path = None
        for fname in possible_files:
            fp = self.data_dir / fname
            if fp.exists():
                file_path = fp
                break

        if not file_path:
            logger.warning(f"No FIFA players file found in {self.data_dir}")
            return []

        players = []

        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:  # utf-8-sig handles BOM
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        # Build attributes dict from available columns
                        attributes = {}
                        for key, value in row.items():
                            if key not in ['ID', 'id', 'Name', 'name', 'Nationality', 'nationality',
                                          'Club', 'club', 'Overall', 'overall', 'Position', 'position']:
                                if value and str(value).strip():
                                    try:
                                        attributes[key] = int(value)
                                    except ValueError:
                                        attributes[key] = value

                        # Handle different column names (FIFA data uses capitals)
                        player_id = row.get('ID', row.get('id', 0))
                        player_name = row.get('Name', row.get('name', 'Unknown'))
                        nationality = row.get('Nationality', row.get('nationality', 'Unknown'))
                        club = row.get('Club', row.get('club', ''))
                        overall = row.get('Overall', row.get('overall', None))
                        position = row.get('Position', row.get('position', None))

                        player = Player(
                            id=self._safe_int(player_id) if player_id else 0,
                            name=self._safe_str(player_name),
                            nationality=self._safe_str(nationality),
                            club=self.normalize_team_name(club) if club else None,
                            overall_rating=self._safe_int(overall) if overall else None,
                            position=self._safe_str(position) if position else None,
                            attributes=attributes
                        )
                        players.append(player)
                    except Exception as e:
                        logger.error(f"Error parsing player row: {e}")
                        continue

        except Exception as e:
            logger.error(f"Error loading FIFA players: {e}")

        logger.info(f"Loaded {len(players)} FIFA players")
        return players

    def load_all(self) -> Dict[str, Any]:
        """
        Load all datasets

        Returns:
            Dictionary containing all loaded data:
            {
                'brasileirao_matches': List[Match],
                'copa_brasil': List[Match],
                'libertadores': List[Match],
                'extended': List[Match],
                'historical': List[Match],
                'players': List[Player],
                'all_matches': List[Match]
            }

        Also sets self.matches and self.players as instance attributes for QueryEngine
        """
        logger.info("Loading all datasets...")

        brasileirao = self.load_brasileirao_matches()
        copa_brasil = self.load_copa_brasil_matches()
        libertadores = self.load_libertadores_matches()
        extended = self.load_extended_matches()
        historical = self.load_historical_matches()
        players = self.load_fifa_players()

        # Combine all matches
        all_matches = brasileirao + copa_brasil + libertadores + extended + historical

        # Store as instance attributes for QueryEngine access
        self.matches = all_matches
        self.players = players

        logger.info(f"Total matches loaded: {len(all_matches)}")
        logger.info(f"Total players loaded: {len(players)}")

        return {
            'brasileirao_matches': brasileirao,
            'copa_brasil': copa_brasil,
            'libertadores': libertadores,
            'extended': extended,
            'historical': historical,
            'players': players,
            'all_matches': all_matches,
        }
