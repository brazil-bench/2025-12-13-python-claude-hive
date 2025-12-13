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

from .models import Team, Player, Match, Competition
from .team_normalizer import TeamNormalizer


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
        file_path = self.data_dir / "brasileirao_matches.csv"
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
                            competition="Brasileirão Série A",
                            season=self._safe_int(row.get('season', match_date.year)),
                            round=self._safe_str(row.get('round')),
                            stadium=self._safe_str(row.get('stadium'))
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
        file_path = self.data_dir / "copa_brasil_matches.csv"
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
                            competition="Copa do Brasil",
                            season=self._safe_int(row.get('season', match_date.year)),
                            round=self._safe_str(row.get('round')),
                            stadium=self._safe_str(row.get('stadium'))
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
        file_path = self.data_dir / "libertadores_matches.csv"
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
                            competition="Copa Libertadores",
                            season=self._safe_int(row.get('season', match_date.year)),
                            round=self._safe_str(row.get('round')),
                            stadium=self._safe_str(row.get('stadium'))
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
        file_path = self.data_dir / "fifa_players.csv"
        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            return []

        players = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        # Build attributes dict from available columns
                        attributes = {}
                        for key, value in row.items():
                            if key not in ['id', 'name', 'nationality', 'club', 'overall', 'position']:
                                if value and value.strip():
                                    try:
                                        attributes[key] = int(value)
                                    except ValueError:
                                        attributes[key] = value

                        player = Player(
                            id=self._safe_int(row.get('id', 0)),
                            name=self._safe_str(row.get('name', 'Unknown')),
                            nationality=self._safe_str(row.get('nationality', 'Unknown')),
                            club=self.normalize_team_name(row.get('club', '')) if row.get('club') else None,
                            overall_rating=self._safe_int(row.get('overall')) if row.get('overall') else None,
                            position=self._safe_str(row.get('position')) if row.get('position') else None,
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
                'brasileirao': List[Match],
                'copa_brasil': List[Match],
                'libertadores': List[Match],
                'extended': List[Match],
                'historical': List[Match],
                'players': List[Player],
                'all_matches': List[Match]
            }
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

        logger.info(f"Total matches loaded: {len(all_matches)}")
        logger.info(f"Total players loaded: {len(players)}")

        return {
            'brasileirao': brasileirao,
            'copa_brasil': copa_brasil,
            'libertadores': libertadores,
            'extended': extended,
            'historical': historical,
            'players': players,
            'all_matches': all_matches,
        }
