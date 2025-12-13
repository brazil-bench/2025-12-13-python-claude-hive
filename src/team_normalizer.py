"""
Brazilian Soccer MCP Server - Team Name Normalizer

Purpose: Normalize team names across different data sources and formats
Author: Claude Code - CODER Agent
Date: 2025-12-13
Dependencies: typing
Key Functions: TeamNormalizer class with normalize() method

Brazilian team names appear in various formats across datasets:
- "Palmeiras-SP" vs "Palmeiras" vs "SE Palmeiras"
- "Sport Club Corinthians Paulista" vs "Corinthians"
- UTF-8 characters: "Grêmio", "São Paulo", "Avaí"

This normalizer provides consistent team identification across all datasets.
"""

from typing import Dict, Set, Optional


class TeamNormalizer:
    """
    Normalizes team names to canonical forms

    Handles common variations including:
    - State suffixes (e.g., "-SP", "-RJ")
    - Full official names vs common names
    - Portuguese special characters
    - Different spelling variations
    """

    # Mapping of variations to canonical names
    TEAM_MAPPINGS: Dict[str, str] = {
        # Palmeiras variations
        "palmeiras-sp": "Palmeiras",
        "se palmeiras": "Palmeiras",
        "sociedade esportiva palmeiras": "Palmeiras",
        "palmeiras": "Palmeiras",

        # Corinthians variations
        "corinthians-sp": "Corinthians",
        "sport club corinthians paulista": "Corinthians",
        "sc corinthians paulista": "Corinthians",
        "corinthians": "Corinthians",

        # São Paulo variations
        "sao paulo-sp": "São Paulo",
        "sao paulo": "São Paulo",
        "são paulo fc": "São Paulo",
        "são paulo": "São Paulo",
        "spfc": "São Paulo",

        # Flamengo variations
        "flamengo-rj": "Flamengo",
        "clube de regatas do flamengo": "Flamengo",
        "cr flamengo": "Flamengo",
        "flamengo": "Flamengo",

        # Fluminense variations
        "fluminense-rj": "Fluminense",
        "fluminense football club": "Fluminense",
        "fluminense fc": "Fluminense",
        "fluminense": "Fluminense",

        # Botafogo variations
        "botafogo-rj": "Botafogo",
        "botafogo de futebol e regatas": "Botafogo",
        "botafogo fr": "Botafogo",
        "botafogo": "Botafogo",

        # Vasco variations
        "vasco-rj": "Vasco da Gama",
        "vasco da gama-rj": "Vasco da Gama",
        "club de regatas vasco da gama": "Vasco da Gama",
        "cr vasco da gama": "Vasco da Gama",
        "vasco da gama": "Vasco da Gama",
        "vasco": "Vasco da Gama",

        # Grêmio variations
        "gremio-rs": "Grêmio",
        "grêmio-rs": "Grêmio",
        "gremio fbpa": "Grêmio",
        "grêmio fbpa": "Grêmio",
        "gremio": "Grêmio",
        "grêmio": "Grêmio",

        # Internacional variations
        "internacional-rs": "Internacional",
        "sport club internacional": "Internacional",
        "sc internacional": "Internacional",
        "internacional": "Internacional",
        "inter": "Internacional",

        # Atlético Mineiro variations
        "atletico-mg": "Atlético Mineiro",
        "atlético-mg": "Atlético Mineiro",
        "atletico mineiro": "Atlético Mineiro",
        "atlético mineiro": "Atlético Mineiro",
        "clube atletico mineiro": "Atlético Mineiro",
        "atletico-mg": "Atlético Mineiro",
        "galo": "Atlético Mineiro",

        # Cruzeiro variations
        "cruzeiro-mg": "Cruzeiro",
        "cruzeiro esporte clube": "Cruzeiro",
        "cruzeiro ec": "Cruzeiro",
        "cruzeiro": "Cruzeiro",

        # Santos variations
        "santos-sp": "Santos",
        "santos fc": "Santos",
        "santos futebol clube": "Santos",
        "santos": "Santos",

        # Atlético Paranaense variations
        "atletico-pr": "Atlético Paranaense",
        "atlético-pr": "Atlético Paranaense",
        "atletico paranaense": "Atlético Paranaense",
        "atlético paranaense": "Atlético Paranaense",
        "club athletico paranaense": "Atlético Paranaense",
        "cap": "Atlético Paranaense",

        # Bahia variations
        "bahia-ba": "Bahia",
        "esporte clube bahia": "Bahia",
        "ec bahia": "Bahia",
        "bahia": "Bahia",

        # Vitória variations
        "vitoria-ba": "Vitória",
        "vitória-ba": "Vitória",
        "esporte clube vitoria": "Vitória",
        "vitoria": "Vitória",
        "vitória": "Vitória",

        # Sport Recife variations
        "sport-pe": "Sport Recife",
        "sport club do recife": "Sport Recife",
        "sport recife": "Sport Recife",
        "sport": "Sport Recife",

        # Ceará variations
        "ceara-ce": "Ceará",
        "ceará-ce": "Ceará",
        "ceara sporting club": "Ceará",
        "ceara": "Ceará",
        "ceará": "Ceará",

        # Fortaleza variations
        "fortaleza-ce": "Fortaleza",
        "fortaleza esporte clube": "Fortaleza",
        "fortaleza ec": "Fortaleza",
        "fortaleza": "Fortaleza",

        # Coritiba variations
        "coritiba-pr": "Coritiba",
        "coritiba foot ball club": "Coritiba",
        "coritiba fc": "Coritiba",
        "coritiba": "Coritiba",

        # Avaí variations
        "avai-sc": "Avaí",
        "avaí-sc": "Avaí",
        "avai futebol clube": "Avaí",
        "avai": "Avaí",
        "avaí": "Avaí",

        # Chapecoense variations
        "chapecoense-sc": "Chapecoense",
        "associacao chapecoense de futebol": "Chapecoense",
        "chapecoense": "Chapecoense",
        "chape": "Chapecoense",

        # Goiás variations
        "goias-go": "Goiás",
        "goiás-go": "Goiás",
        "goias esporte clube": "Goiás",
        "goias": "Goiás",
        "goiás": "Goiás",
    }

    # State abbreviations for extraction
    STATES: Set[str] = {
        "SP", "RJ", "MG", "RS", "PR", "SC", "BA", "PE", "CE", "GO",
        "DF", "ES", "AM", "PA", "MT", "MS", "AL", "SE", "RN", "PB",
        "PI", "MA", "TO", "RO", "AC", "RR", "AP"
    }

    def __init__(self):
        """Initialize the team normalizer"""
        self._cache: Dict[str, str] = {}

    def normalize(self, team_name: str) -> str:
        """
        Normalize a team name to its canonical form

        Args:
            team_name: Raw team name from data source

        Returns:
            Normalized canonical team name

        Examples:
            >>> normalizer = TeamNormalizer()
            >>> normalizer.normalize("Palmeiras-SP")
            'Palmeiras'
            >>> normalizer.normalize("Sport Club Corinthians Paulista")
            'Corinthians'
            >>> normalizer.normalize("Grêmio FBPA")
            'Grêmio'
        """
        if not team_name:
            return ""

        # Check cache first
        if team_name in self._cache:
            return self._cache[team_name]

        # Normalize to lowercase for comparison
        normalized_lower = team_name.lower().strip()

        # Remove extra whitespace
        normalized_lower = " ".join(normalized_lower.split())

        # Check direct mapping
        if normalized_lower in self.TEAM_MAPPINGS:
            result = self.TEAM_MAPPINGS[normalized_lower]
            self._cache[team_name] = result
            return result

        # Try removing state suffix (e.g., "Team-SP" -> "Team")
        for state in self.STATES:
            suffix = f"-{state.lower()}"
            if normalized_lower.endswith(suffix):
                without_suffix = normalized_lower[:-len(suffix)]
                if without_suffix in self.TEAM_MAPPINGS:
                    result = self.TEAM_MAPPINGS[without_suffix]
                    self._cache[team_name] = result
                    return result

        # If no mapping found, return title-cased original
        result = team_name.strip()
        self._cache[team_name] = result
        return result

    def extract_state(self, team_name: str) -> Optional[str]:
        """
        Extract state abbreviation from team name

        Args:
            team_name: Raw team name (e.g., "Palmeiras-SP")

        Returns:
            State abbreviation or None if not found

        Examples:
            >>> normalizer = TeamNormalizer()
            >>> normalizer.extract_state("Palmeiras-SP")
            'SP'
            >>> normalizer.extract_state("Flamengo-RJ")
            'RJ'
        """
        for state in self.STATES:
            if team_name.upper().endswith(f"-{state}"):
                return state
        return None

    def get_aliases(self, canonical_name: str) -> List[str]:
        """
        Get all known aliases for a canonical team name

        Args:
            canonical_name: Canonical team name

        Returns:
            List of known aliases
        """
        aliases = []
        for variation, canonical in self.TEAM_MAPPINGS.items():
            if canonical == canonical_name and variation != canonical_name.lower():
                aliases.append(variation)
        return aliases
