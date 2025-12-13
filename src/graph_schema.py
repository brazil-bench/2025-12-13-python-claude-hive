"""
Brazilian Soccer MCP - Neo4j Graph Schema Definition

CONTEXT:
This module defines the complete graph schema for Brazilian soccer data storage
in Neo4j. It establishes node labels, relationship types, and property structures
that represent teams, players, matches, competitions, and their interconnections.

DESIGN DECISIONS:
- Separate node types for each entity to enable efficient querying
- Rich relationship types to capture different interaction patterns
- Property-based relationships to store match details and statistics
- Temporal connections via SEASON nodes for historical analysis

USAGE:
    from graph_schema import TEAM, PLAYER, PLAYED_HOME
    # Use constants in Cypher queries for consistency

DEPENDENCIES:
- None (schema definition only)

AUTHOR: Coder Agent - Brazilian Soccer MCP Hive Mind
PHASE: 3 - Neo4j Knowledge Graph
"""

from typing import Dict, List, Set

# ============================================================================
# NODE LABELS
# ============================================================================

TEAM = "Team"
"""
Team node represents a Brazilian soccer club.
Properties:
    - id: str (unique identifier)
    - name: str (official team name)
    - founded: int (year founded)
    - city: str (home city)
    - state: str (state abbreviation)
    - stadium: str (home stadium name)
    - colors: List[str] (team colors)
"""

PLAYER = "Player"
"""
Player node represents an individual soccer player.
Properties:
    - id: str (unique identifier)
    - name: str (full name)
    - birth_date: str (ISO format)
    - nationality: str (country code)
    - position: str (primary position)
    - height: float (in cm)
    - weight: float (in kg)
"""

MATCH = "Match"
"""
Match node represents a single soccer match.
Properties:
    - id: str (unique identifier)
    - date: str (ISO format)
    - round: int (match round number)
    - attendance: int (number of spectators)
    - home_score: int
    - away_score: int
    - status: str (scheduled, completed, cancelled)
"""

COMPETITION = "Competition"
"""
Competition node represents a tournament or league.
Properties:
    - id: str (unique identifier)
    - name: str (competition name)
    - type: str (league, cup, championship)
    - level: str (national, state, international)
"""

SEASON = "Season"
"""
Season node represents a specific year or time period.
Properties:
    - id: str (unique identifier, e.g., "2024")
    - year: int
    - start_date: str (ISO format)
    - end_date: str (ISO format)
"""

STADIUM = "Stadium"
"""
Stadium node represents a soccer venue.
Properties:
    - id: str (unique identifier)
    - name: str (stadium name)
    - city: str
    - state: str
    - capacity: int (maximum capacity)
    - opened: int (year opened)
"""

# ============================================================================
# RELATIONSHIP TYPES
# ============================================================================

PLAYED_HOME = "PLAYED_HOME"
"""
Relationship from Team to Match (as home team).
Properties:
    - score: int (goals scored)
    - formation: str (tactical formation)
"""

PLAYED_AWAY = "PLAYED_AWAY"
"""
Relationship from Team to Match (as away team).
Properties:
    - score: int (goals scored)
    - formation: str (tactical formation)
"""

PLAYS_FOR = "PLAYS_FOR"
"""
Relationship from Player to Team.
Properties:
    - from_date: str (ISO format)
    - to_date: str (ISO format, null if current)
    - jersey_number: int
    - is_captain: bool
"""

COMPETED_IN = "COMPETED_IN"
"""
Relationship from Match to Competition.
Properties:
    - round: int
    - stage: str (group, knockout, final, etc.)
"""

HOSTED_AT = "HOSTED_AT"
"""
Relationship from Match to Stadium.
Properties:
    - attendance: int
    - weather_conditions: str (optional)
"""

PART_OF_SEASON = "PART_OF_SEASON"
"""
Relationship from Match/Competition to Season.
Properties:
    - match_day: int (day number in season)
"""

SCORED_IN = "SCORED_IN"
"""
Relationship from Player to Match.
Properties:
    - goals: int
    - assists: int
    - minutes_played: int
    - yellow_cards: int
    - red_cards: int
"""

MANAGES = "MANAGES"
"""
Relationship from Coach (Player node with special flag) to Team.
Properties:
    - from_date: str (ISO format)
    - to_date: str (ISO format, null if current)
"""

# ============================================================================
# SCHEMA CONSTRAINTS AND INDEXES
# ============================================================================

CONSTRAINTS: Dict[str, List[str]] = {
    "unique_constraints": [
        f"CREATE CONSTRAINT team_id_unique IF NOT EXISTS FOR (t:{TEAM}) REQUIRE t.id IS UNIQUE",
        f"CREATE CONSTRAINT player_id_unique IF NOT EXISTS FOR (p:{PLAYER}) REQUIRE p.id IS UNIQUE",
        f"CREATE CONSTRAINT match_id_unique IF NOT EXISTS FOR (m:{MATCH}) REQUIRE m.id IS UNIQUE",
        f"CREATE CONSTRAINT competition_id_unique IF NOT EXISTS FOR (c:{COMPETITION}) REQUIRE c.id IS UNIQUE",
        f"CREATE CONSTRAINT season_id_unique IF NOT EXISTS FOR (s:{SEASON}) REQUIRE s.id IS UNIQUE",
        f"CREATE CONSTRAINT stadium_id_unique IF NOT EXISTS FOR (st:{STADIUM}) REQUIRE st.id IS UNIQUE",
    ],
    "existence_constraints": [
        f"CREATE CONSTRAINT team_name_exists IF NOT EXISTS FOR (t:{TEAM}) REQUIRE t.name IS NOT NULL",
        f"CREATE CONSTRAINT player_name_exists IF NOT EXISTS FOR (p:{PLAYER}) REQUIRE p.name IS NOT NULL",
        f"CREATE CONSTRAINT match_date_exists IF NOT EXISTS FOR (m:{MATCH}) REQUIRE m.date IS NOT NULL",
    ]
}

INDEXES: List[str] = [
    # Performance indexes for common queries
    f"CREATE INDEX team_name_idx IF NOT EXISTS FOR (t:{TEAM}) ON (t.name)",
    f"CREATE INDEX team_city_idx IF NOT EXISTS FOR (t:{TEAM}) ON (t.city)",
    f"CREATE INDEX player_name_idx IF NOT EXISTS FOR (p:{PLAYER}) ON (p.name)",
    f"CREATE INDEX player_position_idx IF NOT EXISTS FOR (p:{PLAYER}) ON (p.position)",
    f"CREATE INDEX match_date_idx IF NOT EXISTS FOR (m:{MATCH}) ON (m.date)",
    f"CREATE INDEX competition_name_idx IF NOT EXISTS FOR (c:{COMPETITION}) ON (c.name)",
    f"CREATE INDEX season_year_idx IF NOT EXISTS FOR (s:{SEASON}) ON (s.year)",
    f"CREATE INDEX stadium_city_idx IF NOT EXISTS FOR (st:{STADIUM}) ON (st.city)",

    # Composite indexes for complex queries
    f"CREATE INDEX match_date_status_idx IF NOT EXISTS FOR (m:{MATCH}) ON (m.date, m.status)",
]

# ============================================================================
# NODE PROPERTY SCHEMAS
# ============================================================================

NODE_PROPERTIES: Dict[str, Dict[str, str]] = {
    TEAM: {
        "id": "STRING (required, unique)",
        "name": "STRING (required)",
        "founded": "INTEGER",
        "city": "STRING",
        "state": "STRING",
        "stadium": "STRING",
        "colors": "LIST<STRING>",
    },
    PLAYER: {
        "id": "STRING (required, unique)",
        "name": "STRING (required)",
        "birth_date": "DATE",
        "nationality": "STRING",
        "position": "STRING",
        "height": "FLOAT",
        "weight": "FLOAT",
    },
    MATCH: {
        "id": "STRING (required, unique)",
        "date": "DATETIME (required)",
        "round": "INTEGER",
        "attendance": "INTEGER",
        "home_score": "INTEGER",
        "away_score": "INTEGER",
        "status": "STRING",
    },
    COMPETITION: {
        "id": "STRING (required, unique)",
        "name": "STRING (required)",
        "type": "STRING",
        "level": "STRING",
    },
    SEASON: {
        "id": "STRING (required, unique)",
        "year": "INTEGER (required)",
        "start_date": "DATE",
        "end_date": "DATE",
    },
    STADIUM: {
        "id": "STRING (required, unique)",
        "name": "STRING (required)",
        "city": "STRING",
        "state": "STRING",
        "capacity": "INTEGER",
        "opened": "INTEGER",
    }
}

# ============================================================================
# RELATIONSHIP PROPERTY SCHEMAS
# ============================================================================

RELATIONSHIP_PROPERTIES: Dict[str, Dict[str, str]] = {
    PLAYED_HOME: {
        "score": "INTEGER",
        "formation": "STRING",
    },
    PLAYED_AWAY: {
        "score": "INTEGER",
        "formation": "STRING",
    },
    PLAYS_FOR: {
        "from_date": "DATE",
        "to_date": "DATE",
        "jersey_number": "INTEGER",
        "is_captain": "BOOLEAN",
    },
    COMPETED_IN: {
        "round": "INTEGER",
        "stage": "STRING",
    },
    HOSTED_AT: {
        "attendance": "INTEGER",
        "weather_conditions": "STRING",
    },
    PART_OF_SEASON: {
        "match_day": "INTEGER",
    },
    SCORED_IN: {
        "goals": "INTEGER",
        "assists": "INTEGER",
        "minutes_played": "INTEGER",
        "yellow_cards": "INTEGER",
        "red_cards": "INTEGER",
    },
    MANAGES: {
        "from_date": "DATE",
        "to_date": "DATE",
    }
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_all_node_labels() -> Set[str]:
    """Return all defined node labels."""
    return {TEAM, PLAYER, MATCH, COMPETITION, SEASON, STADIUM}

def get_all_relationship_types() -> Set[str]:
    """Return all defined relationship types."""
    return {
        PLAYED_HOME, PLAYED_AWAY, PLAYS_FOR, COMPETED_IN,
        HOSTED_AT, PART_OF_SEASON, SCORED_IN, MANAGES
    }

def get_schema_summary() -> Dict:
    """Return a complete summary of the graph schema."""
    return {
        "nodes": {
            "labels": list(get_all_node_labels()),
            "properties": NODE_PROPERTIES
        },
        "relationships": {
            "types": list(get_all_relationship_types()),
            "properties": RELATIONSHIP_PROPERTIES
        },
        "constraints": CONSTRAINTS,
        "indexes": INDEXES
    }
