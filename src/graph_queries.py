"""
Brazilian Soccer MCP - Cypher Query Templates

CONTEXT:
This module provides pre-built Cypher query templates for common graph
operations on Brazilian soccer data. Includes parameterized queries for
data insertion, retrieval, analysis, and graph traversal operations.

DESIGN DECISIONS:
- Parameterized queries to prevent Cypher injection
- Optimized with proper indexes and constraints
- Support for batch operations
- Reusable templates for common patterns
- Clear separation of read and write operations

PERFORMANCE CONSIDERATIONS:
- Uses MERGE for upsert operations
- Batch processing with UNWIND for bulk imports
- Proper index utilization
- LIMIT clauses to prevent runaway queries
- Optional EXPLAIN/PROFILE support

USAGE:
    from graph_queries import CREATE_TEAM, FIND_TEAM_MATCHES
    session.run(CREATE_TEAM, parameters={"team_data": team_dict})

AUTHOR: Coder Agent - Brazilian Soccer MCP Hive Mind
PHASE: 3 - Neo4j Knowledge Graph
"""

from typing import Dict, List, Any

# ============================================================================
# CREATE QUERIES - Data Insertion
# ============================================================================

CREATE_TEAM = """
MERGE (t:Team {id: $id})
SET t.name = $name,
    t.founded = $founded,
    t.city = $city,
    t.state = $state,
    t.stadium = $stadium,
    t.colors = $colors
RETURN t
"""

CREATE_PLAYER = """
MERGE (p:Player {id: $id})
SET p.name = $name,
    p.birth_date = date($birth_date),
    p.nationality = $nationality,
    p.position = $position,
    p.height = $height,
    p.weight = $weight
RETURN p
"""

CREATE_MATCH = """
MERGE (m:Match {id: $id})
SET m.date = datetime($date),
    m.round = $round,
    m.attendance = $attendance,
    m.home_score = $home_score,
    m.away_score = $away_score,
    m.status = $status
RETURN m
"""

CREATE_COMPETITION = """
MERGE (c:Competition {id: $id})
SET c.name = $name,
    c.type = $type,
    c.level = $level
RETURN c
"""

CREATE_SEASON = """
MERGE (s:Season {id: $id})
SET s.year = $year,
    s.start_date = date($start_date),
    s.end_date = date($end_date)
RETURN s
"""

CREATE_STADIUM = """
MERGE (st:Stadium {id: $id})
SET st.name = $name,
    st.city = $city,
    st.state = $state,
    st.capacity = $capacity,
    st.opened = $opened
RETURN st
"""

# ============================================================================
# BATCH CREATE QUERIES - Bulk Import
# ============================================================================

BATCH_CREATE_TEAMS = """
UNWIND $teams AS team
MERGE (t:Team {id: team.id})
SET t.name = team.name,
    t.founded = team.founded,
    t.city = team.city,
    t.state = team.state,
    t.stadium = team.stadium,
    t.colors = team.colors
RETURN count(t) as teams_created
"""

BATCH_CREATE_PLAYERS = """
UNWIND $players AS player
MERGE (p:Player {id: player.id})
SET p.name = player.name,
    p.birth_date = date(player.birth_date),
    p.nationality = player.nationality,
    p.position = player.position,
    p.height = player.height,
    p.weight = player.weight
RETURN count(p) as players_created
"""

BATCH_CREATE_MATCHES = """
UNWIND $matches AS match
MERGE (m:Match {id: match.id})
SET m.date = datetime(match.date),
    m.round = match.round,
    m.attendance = match.attendance,
    m.home_score = match.home_score,
    m.away_score = match.away_score,
    m.status = match.status
RETURN count(m) as matches_created
"""

# ============================================================================
# RELATIONSHIP CREATION QUERIES
# ============================================================================

CREATE_PLAYED_HOME_RELATIONSHIP = """
MATCH (t:Team {id: $team_id})
MATCH (m:Match {id: $match_id})
MERGE (t)-[r:PLAYED_HOME]->(m)
SET r.score = $score,
    r.formation = $formation
RETURN r
"""

CREATE_PLAYED_AWAY_RELATIONSHIP = """
MATCH (t:Team {id: $team_id})
MATCH (m:Match {id: $match_id})
MERGE (t)-[r:PLAYED_AWAY]->(m)
SET r.score = $score,
    r.formation = $formation
RETURN r
"""

CREATE_PLAYS_FOR_RELATIONSHIP = """
MATCH (p:Player {id: $player_id})
MATCH (t:Team {id: $team_id})
MERGE (p)-[r:PLAYS_FOR]->(t)
SET r.from_date = date($from_date),
    r.to_date = CASE WHEN $to_date IS NOT NULL THEN date($to_date) ELSE null END,
    r.jersey_number = $jersey_number,
    r.is_captain = $is_captain
RETURN r
"""

CREATE_MATCH_WITH_TEAMS = """
MERGE (m:Match {id: $match_id})
SET m.date = datetime($date),
    m.round = $round,
    m.home_score = $home_score,
    m.away_score = $away_score,
    m.status = $status

WITH m
MATCH (home:Team {id: $home_team_id})
MATCH (away:Team {id: $away_team_id})
MERGE (home)-[rh:PLAYED_HOME {score: $home_score}]->(m)
MERGE (away)-[ra:PLAYED_AWAY {score: $away_score}]->(m)
RETURN m, home, away
"""

CREATE_COMPETED_IN_RELATIONSHIP = """
MATCH (m:Match {id: $match_id})
MATCH (c:Competition {id: $competition_id})
MERGE (m)-[r:COMPETED_IN]->(c)
SET r.round = $round,
    r.stage = $stage
RETURN r
"""

CREATE_HOSTED_AT_RELATIONSHIP = """
MATCH (m:Match {id: $match_id})
MATCH (st:Stadium {id: $stadium_id})
MERGE (m)-[r:HOSTED_AT]->(st)
SET r.attendance = $attendance,
    r.weather_conditions = $weather_conditions
RETURN r
"""

# ============================================================================
# FIND/QUERY OPERATIONS
# ============================================================================

FIND_TEAM_BY_NAME = """
MATCH (t:Team)
WHERE toLower(t.name) CONTAINS toLower($name)
RETURN t
LIMIT $limit
"""

FIND_TEAM_BY_ID = """
MATCH (t:Team {id: $id})
RETURN t
"""

FIND_PLAYER_BY_NAME = """
MATCH (p:Player)
WHERE toLower(p.name) CONTAINS toLower($name)
RETURN p
LIMIT $limit
"""

FIND_MATCHES_BY_TEAM = """
MATCH (t:Team {id: $team_id})
MATCH (t)-[r:PLAYED_HOME|PLAYED_AWAY]->(m:Match)
RETURN m, type(r) as match_type, r.score as score
ORDER BY m.date DESC
LIMIT $limit
"""

FIND_MATCHES_BY_DATE_RANGE = """
MATCH (m:Match)
WHERE m.date >= datetime($start_date) AND m.date <= datetime($end_date)
RETURN m
ORDER BY m.date
LIMIT $limit
"""

FIND_CURRENT_SQUAD = """
MATCH (t:Team {id: $team_id})<-[r:PLAYS_FOR]-(p:Player)
WHERE r.to_date IS NULL
RETURN p, r.jersey_number as jersey_number, r.is_captain as is_captain
ORDER BY r.jersey_number
"""

# ============================================================================
# GRAPH TRAVERSAL QUERIES
# ============================================================================

FIND_SHORTEST_PATH_BETWEEN_TEAMS = """
MATCH (t1:Team {id: $team1_id}), (t2:Team {id: $team2_id})
MATCH path = shortestPath((t1)-[*..10]-(t2))
RETURN path, length(path) as path_length
LIMIT 1
"""

GET_TEAM_NETWORK = """
MATCH (t:Team {id: $team_id})
CALL apoc.path.subgraphNodes(t, {
    relationshipFilter: "PLAYED_HOME>|PLAYED_AWAY>",
    minLevel: 1,
    maxLevel: $depth
})
YIELD node
RETURN DISTINCT node
LIMIT $limit
"""

FIND_COMMON_OPPONENTS = """
MATCH (t1:Team {id: $team1_id})-[:PLAYED_HOME|PLAYED_AWAY]->(m1:Match)<-[:PLAYED_HOME|PLAYED_AWAY]-(opponent:Team)
MATCH (t2:Team {id: $team2_id})-[:PLAYED_HOME|PLAYED_AWAY]->(m2:Match)<-[:PLAYED_HOME|PLAYED_AWAY]-(opponent)
WHERE opponent.id <> $team1_id AND opponent.id <> $team2_id
RETURN DISTINCT opponent, count(DISTINCT m1) + count(DISTINCT m2) as total_matches
ORDER BY total_matches DESC
LIMIT $limit
"""

FIND_HEAD_TO_HEAD = """
MATCH (t1:Team {id: $team1_id})-[r1:PLAYED_HOME|PLAYED_AWAY]->(m:Match)<-[r2:PLAYED_HOME|PLAYED_AWAY]-(t2:Team {id: $team2_id})
RETURN m, r1.score as team1_score, r2.score as team2_score,
       type(r1) as team1_match_type
ORDER BY m.date DESC
LIMIT $limit
"""

FIND_PLAYER_TRANSFER_HISTORY = """
MATCH (p:Player {id: $player_id})-[r:PLAYS_FOR]->(t:Team)
RETURN t, r.from_date as from_date, r.to_date as to_date, r.jersey_number as jersey
ORDER BY r.from_date DESC
"""

# ============================================================================
# AGGREGATION QUERIES - Statistics
# ============================================================================

GET_TEAM_STATISTICS = """
MATCH (t:Team {id: $team_id})
OPTIONAL MATCH (t)-[rh:PLAYED_HOME]->(mh:Match)
OPTIONAL MATCH (t)-[ra:PLAYED_AWAY]->(ma:Match)
WITH t,
     count(DISTINCT mh) + count(DISTINCT ma) as total_matches,
     count(DISTINCT mh) as home_matches,
     count(DISTINCT ma) as away_matches,
     sum(rh.score) as home_goals,
     sum(ra.score) as away_goals
RETURN t,
       total_matches,
       home_matches,
       away_matches,
       home_goals,
       away_goals,
       home_goals + away_goals as total_goals
"""

GET_PLAYER_STATISTICS = """
MATCH (p:Player {id: $player_id})
OPTIONAL MATCH (p)-[r:SCORED_IN]->(m:Match)
RETURN p,
       count(DISTINCT m) as matches_played,
       sum(r.goals) as total_goals,
       sum(r.assists) as total_assists,
       sum(r.minutes_played) as total_minutes,
       sum(r.yellow_cards) as yellow_cards,
       sum(r.red_cards) as red_cards
"""

GET_COMPETITION_STANDINGS = """
MATCH (c:Competition {id: $competition_id})<-[:COMPETED_IN]-(m:Match)
MATCH (t:Team)-[r:PLAYED_HOME|PLAYED_AWAY]->(m)
WITH t, m, r,
     CASE WHEN type(r) = 'PLAYED_HOME' THEN m.home_score ELSE m.away_score END as goals_for,
     CASE WHEN type(r) = 'PLAYED_HOME' THEN m.away_score ELSE m.home_score END as goals_against
WITH t,
     count(m) as matches_played,
     sum(CASE
         WHEN goals_for > goals_against THEN 3
         WHEN goals_for = goals_against THEN 1
         ELSE 0
     END) as points,
     sum(CASE WHEN goals_for > goals_against THEN 1 ELSE 0 END) as wins,
     sum(CASE WHEN goals_for = goals_against THEN 1 ELSE 0 END) as draws,
     sum(CASE WHEN goals_for < goals_against THEN 1 ELSE 0 END) as losses,
     sum(goals_for) as goals_for,
     sum(goals_against) as goals_against
RETURN t,
       matches_played,
       points,
       wins,
       draws,
       losses,
       goals_for,
       goals_against,
       goals_for - goals_against as goal_difference
ORDER BY points DESC, goal_difference DESC, goals_for DESC
"""

GET_TOP_SCORERS = """
MATCH (p:Player)-[r:SCORED_IN]->(m:Match)-[:COMPETED_IN]->(c:Competition {id: $competition_id})
RETURN p,
       sum(r.goals) as total_goals,
       count(DISTINCT m) as matches_played,
       toFloat(sum(r.goals)) / count(DISTINCT m) as goals_per_match
ORDER BY total_goals DESC, goals_per_match DESC
LIMIT $limit
"""

# ============================================================================
# DELETE QUERIES
# ============================================================================

DELETE_TEAM = """
MATCH (t:Team {id: $id})
OPTIONAL MATCH (t)-[r]-()
DELETE r, t
RETURN count(t) as deleted
"""

DELETE_PLAYER = """
MATCH (p:Player {id: $id})
OPTIONAL MATCH (p)-[r]-()
DELETE r, p
RETURN count(p) as deleted
"""

DELETE_MATCH = """
MATCH (m:Match {id: $id})
OPTIONAL MATCH (m)-[r]-()
DELETE r, m
RETURN count(m) as deleted
"""

DELETE_ALL_DATA = """
MATCH (n)
DETACH DELETE n
RETURN count(n) as deleted_nodes
"""

# ============================================================================
# UTILITY QUERIES
# ============================================================================

COUNT_NODES = """
MATCH (n)
RETURN labels(n)[0] as label, count(n) as count
ORDER BY count DESC
"""

COUNT_RELATIONSHIPS = """
MATCH ()-[r]->()
RETURN type(r) as relationship_type, count(r) as count
ORDER BY count DESC
"""

GET_GRAPH_STATISTICS = """
CALL apoc.meta.stats()
YIELD nodeCount, relCount, labelCount, relTypeCount, propertyKeyCount
RETURN nodeCount, relCount, labelCount, relTypeCount, propertyKeyCount
"""

# ============================================================================
# QUERY PARAMETER BUILDERS
# ============================================================================

def build_team_params(team_data: Dict[str, Any]) -> Dict[str, Any]:
    """Build parameters for team creation query."""
    return {
        "id": team_data.get("id"),
        "name": team_data.get("name"),
        "founded": team_data.get("founded"),
        "city": team_data.get("city"),
        "state": team_data.get("state"),
        "stadium": team_data.get("stadium"),
        "colors": team_data.get("colors", [])
    }

def build_player_params(player_data: Dict[str, Any]) -> Dict[str, Any]:
    """Build parameters for player creation query."""
    return {
        "id": player_data.get("id"),
        "name": player_data.get("name"),
        "birth_date": player_data.get("birth_date"),
        "nationality": player_data.get("nationality"),
        "position": player_data.get("position"),
        "height": player_data.get("height"),
        "weight": player_data.get("weight")
    }

def build_match_params(match_data: Dict[str, Any]) -> Dict[str, Any]:
    """Build parameters for match creation query."""
    return {
        "id": match_data.get("id"),
        "date": match_data.get("date"),
        "round": match_data.get("round"),
        "attendance": match_data.get("attendance"),
        "home_score": match_data.get("home_score"),
        "away_score": match_data.get("away_score"),
        "status": match_data.get("status", "scheduled")
    }
