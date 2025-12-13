# Neo4j Setup Guide for Brazilian Soccer MCP

This guide provides comprehensive instructions for setting up Neo4j graph database to store and query Brazilian soccer data from multiple competitions.

## Table of Contents
- [Installation](#installation)
- [Graph Schema Design](#graph-schema-design)
- [Data Import](#data-import)
- [Sample Queries](#sample-queries)
- [Performance Optimization](#performance-optimization)

## Installation

### Option 1: Docker (Recommended)

```bash
# Pull the Neo4j Docker image
docker pull neo4j:latest

# Run Neo4j container
docker run \
    --name brazilian-soccer-neo4j \
    -p 7474:7474 -p 7687:7687 \
    -d \
    -v $PWD/neo4j/data:/data \
    -v $PWD/neo4j/logs:/logs \
    -v $PWD/neo4j/import:/var/lib/neo4j/import \
    -v $PWD/neo4j/plugins:/plugins \
    --env NEO4J_AUTH=neo4j/brazilian_soccer_2024 \
    --env NEO4J_apoc_export_file_enabled=true \
    --env NEO4J_apoc_import_file_enabled=true \
    --env NEO4J_apoc_import_file_use__neo4j__config=true \
    neo4j:latest

# Create import directory and copy data files
mkdir -p neo4j/import
cp data/kaggle/*.csv neo4j/import/

# Access Neo4j Browser at http://localhost:7474
# Username: neo4j
# Password: brazilian_soccer_2024
```

### Option 2: Local Installation

1. Download Neo4j Desktop from [neo4j.com/download](https://neo4j.com/download/)
2. Install and create a new database
3. Set password to `brazilian_soccer_2024`
4. Start the database
5. Access Neo4j Browser at http://localhost:7474

### Install APOC Plugin (Required for CSV Import)

```bash
# For Docker
docker exec brazilian-soccer-neo4j sh -c 'cd plugins && wget https://github.com/neo4j/apoc/releases/download/5.15.0/apoc-5.15.0-core.jar'
docker restart brazilian-soccer-neo4j

# For Neo4j Desktop
# Go to Database Settings → Plugins → Install APOC
```

## Graph Schema Design

### Node Types

#### 1. Team
```cypher
(:Team {
    name: STRING,          // e.g., "Flamengo-RJ"
    state: STRING,         // e.g., "RJ"
    display_name: STRING,  // e.g., "Flamengo"
    created_at: DATETIME
})
```

#### 2. Player
```cypher
(:Player {
    id: INTEGER,           // FIFA player ID
    name: STRING,          // Player name
    age: INTEGER,
    nationality: STRING,
    photo: STRING,         // Photo URL
    overall: INTEGER,      // Overall rating (0-100)
    potential: INTEGER,
    position: STRING,      // Primary position
    preferred_foot: STRING,
    height: STRING,
    weight: STRING,
    value: STRING,         // Market value
    wage: STRING,
    club: STRING,
    created_at: DATETIME
})
```

#### 3. Match
```cypher
(:Match {
    id: STRING,            // Unique match identifier
    datetime: DATETIME,
    season: INTEGER,
    round: INTEGER,
    home_goal: INTEGER,
    away_goal: INTEGER,
    competition: STRING,   // 'Brasileirao', 'Copa do Brasil', 'Libertadores'
    stage: STRING,         // For Libertadores: 'group stage', 'knockout', etc.

    // Extended statistics (when available)
    home_corner: INTEGER,
    away_corner: INTEGER,
    home_attack: INTEGER,
    away_attack: INTEGER,
    home_shots: INTEGER,
    away_shots: INTEGER,
    total_corners: INTEGER,

    created_at: DATETIME
})
```

#### 4. Competition
```cypher
(:Competition {
    name: STRING,          // 'Brasileirao', 'Copa do Brasil', 'Copa Libertadores'
    country: STRING,       // 'Brazil', 'CONMEBOL'
    type: STRING,          // 'League', 'Cup', 'International Cup'
    created_at: DATETIME
})
```

#### 5. Season
```cypher
(:Season {
    year: INTEGER,         // e.g., 2012
    competition: STRING,
    created_at: DATETIME
})
```

#### 6. Stadium
```cypher
(:Stadium {
    name: STRING,          // e.g., "Maracanã"
    city: STRING,
    state: STRING,
    capacity: INTEGER,
    created_at: DATETIME
})
```

### Relationship Types

#### 1. PLAYED_HOME
```cypher
(:Team)-[:PLAYED_HOME {
    goals_scored: INTEGER,
    goals_conceded: INTEGER,
    result: STRING,        // 'WIN', 'DRAW', 'LOSS'
    corners: INTEGER,
    attacks: INTEGER,
    shots: INTEGER
}]->(:Match)
```

#### 2. PLAYED_AWAY
```cypher
(:Team)-[:PLAYED_AWAY {
    goals_scored: INTEGER,
    goals_conceded: INTEGER,
    result: STRING,
    corners: INTEGER,
    attacks: INTEGER,
    shots: INTEGER
}]->(:Match)
```

#### 3. BELONGS_TO
```cypher
(:Player)-[:BELONGS_TO {
    jersey_number: INTEGER,
    joined_date: DATE,
    contract_until: INTEGER,
    wage: STRING
}]->(:Team)
```

#### 4. HOSTED_AT
```cypher
(:Match)-[:HOSTED_AT]->(:Stadium)
```

#### 5. IN_COMPETITION
```cypher
(:Match)-[:IN_COMPETITION]->(:Competition)
```

#### 6. IN_SEASON
```cypher
(:Match)-[:IN_SEASON]->(:Season)
```

#### 7. COMPETES_IN
```cypher
(:Team)-[:COMPETES_IN {
    season: INTEGER
}]->(:Competition)
```

### Schema Diagram

```
┌─────────┐     BELONGS_TO      ┌──────┐
│ Player  │────────────────────>│ Team │
└─────────┘                     └──────┘
                                   │ │
                        PLAYED_HOME│ │PLAYED_AWAY
                                   │ │
                                   v v
┌────────────┐  HOSTED_AT    ┌───────┐    IN_COMPETITION    ┌─────────────┐
│  Stadium   │<──────────────│ Match │───────────────────>│ Competition │
└────────────┘               └───────┘                     └─────────────┘
                                  │
                                  │IN_SEASON
                                  v
                             ┌────────┐
                             │ Season │
                             └────────┘
```

## Data Import

### Step 1: Create Constraints and Indexes

```cypher
// Create unique constraints
CREATE CONSTRAINT team_name IF NOT EXISTS
FOR (t:Team) REQUIRE t.name IS UNIQUE;

CREATE CONSTRAINT player_id IF NOT EXISTS
FOR (p:Player) REQUIRE p.id IS UNIQUE;

CREATE CONSTRAINT match_id IF NOT EXISTS
FOR (m:Match) REQUIRE m.id IS UNIQUE;

CREATE CONSTRAINT competition_name IF NOT EXISTS
FOR (c:Competition) REQUIRE c.name IS UNIQUE;

CREATE CONSTRAINT season_composite IF NOT EXISTS
FOR (s:Season) REQUIRE (s.year, s.competition) IS UNIQUE;

CREATE CONSTRAINT stadium_name IF NOT EXISTS
FOR (st:Stadium) REQUIRE st.name IS UNIQUE;

// Create indexes for performance
CREATE INDEX team_state IF NOT EXISTS
FOR (t:Team) ON (t.state);

CREATE INDEX player_nationality IF NOT EXISTS
FOR (p:Player) ON (p.nationality);

CREATE INDEX player_position IF NOT EXISTS
FOR (p:Player) ON (p.position);

CREATE INDEX match_datetime IF NOT EXISTS
FOR (m:Match) ON (m.datetime);

CREATE INDEX match_season IF NOT EXISTS
FOR (m:Match) ON (m.season);

CREATE INDEX match_competition IF NOT EXISTS
FOR (m:Match) ON (m.competition);

// Full-text search indexes
CALL db.index.fulltext.createNodeIndex('teamNameSearch', ['Team'], ['name', 'display_name']);
CALL db.index.fulltext.createNodeIndex('playerNameSearch', ['Player'], ['name']);
CALL db.index.fulltext.createNodeIndex('stadiumNameSearch', ['Stadium'], ['name']);
```

### Step 2: Import Teams from Brasileirao

```cypher
// Import teams from Brasileirao matches
LOAD CSV WITH HEADERS FROM 'file:///Brasileirao_Matches.csv' AS row

// Merge home team
MERGE (home:Team {name: row.home_team})
ON CREATE SET
    home.state = row.home_team_state,
    home.display_name = split(row.home_team, '-')[0],
    home.created_at = datetime()

// Merge away team
MERGE (away:Team {name: row.away_team})
ON CREATE SET
    away.state = row.away_team_state,
    away.display_name = split(row.away_team, '-')[0],
    away.created_at = datetime();
```

### Step 3: Import Competitions

```cypher
// Create competitions
MERGE (c:Competition {name: 'Brasileirao'})
ON CREATE SET
    c.country = 'Brazil',
    c.type = 'League',
    c.created_at = datetime();

MERGE (c:Competition {name: 'Copa do Brasil'})
ON CREATE SET
    c.country = 'Brazil',
    c.type = 'Cup',
    c.created_at = datetime();

MERGE (c:Competition {name: 'Copa Libertadores'})
ON CREATE SET
    c.country = 'CONMEBOL',
    c.type = 'International Cup',
    c.created_at = datetime();
```

### Step 4: Import Brasileirao Matches

```cypher
LOAD CSV WITH HEADERS FROM 'file:///Brasileirao_Matches.csv' AS row

// Create match ID
WITH row, row.datetime + '-' + row.home_team + '-' + row.away_team AS matchId

// Merge season
MERGE (season:Season {year: toInteger(row.season), competition: 'Brasileirao'})
ON CREATE SET season.created_at = datetime()

// Merge competition
MERGE (comp:Competition {name: 'Brasileirao'})

// Create match
MERGE (match:Match {id: matchId})
ON CREATE SET
    match.datetime = datetime(row.datetime),
    match.season = toInteger(row.season),
    match.round = toInteger(row.round),
    match.home_goal = toInteger(row.home_goal),
    match.away_goal = toInteger(row.away_goal),
    match.competition = 'Brasileirao',
    match.created_at = datetime()

// Match relationships
MERGE (match)-[:IN_SEASON]->(season)
MERGE (match)-[:IN_COMPETITION]->(comp)

// Team relationships
WITH match, row
MATCH (home:Team {name: row.home_team})
MATCH (away:Team {name: row.away_team})

// Calculate results
WITH match, home, away, row,
     CASE
        WHEN toInteger(row.home_goal) > toInteger(row.away_goal) THEN 'WIN'
        WHEN toInteger(row.home_goal) = toInteger(row.away_goal) THEN 'DRAW'
        ELSE 'LOSS'
     END AS home_result,
     CASE
        WHEN toInteger(row.away_goal) > toInteger(row.home_goal) THEN 'WIN'
        WHEN toInteger(row.away_goal) = toInteger(row.home_goal) THEN 'DRAW'
        ELSE 'LOSS'
     END AS away_result

MERGE (home)-[h:PLAYED_HOME]->(match)
ON CREATE SET
    h.goals_scored = toInteger(row.home_goal),
    h.goals_conceded = toInteger(row.away_goal),
    h.result = home_result

MERGE (away)-[a:PLAYED_AWAY]->(match)
ON CREATE SET
    a.goals_scored = toInteger(row.away_goal),
    a.goals_conceded = toInteger(row.home_goal),
    a.result = away_result

// Establish competition relationship
MERGE (home)-[:COMPETES_IN {season: toInteger(row.season)}]->(comp)
MERGE (away)-[:COMPETES_IN {season: toInteger(row.season)}]->(comp);
```

### Step 5: Import Brazilian Cup Matches

```cypher
LOAD CSV WITH HEADERS FROM 'file:///Brazilian_Cup_Matches.csv' AS row

WITH row, row.datetime + '-' + row.home_team + '-' + row.away_team AS matchId

// Merge teams (handle teams not in Brasileirao)
MERGE (home:Team {name: row.home_team})
ON CREATE SET
    home.display_name = row.home_team,
    home.created_at = datetime()

MERGE (away:Team {name: row.away_team})
ON CREATE SET
    away.display_name = row.away_team,
    away.created_at = datetime()

// Merge season and competition
MERGE (season:Season {year: toInteger(row.season), competition: 'Copa do Brasil'})
ON CREATE SET season.created_at = datetime()

MERGE (comp:Competition {name: 'Copa do Brasil'})

// Create match
MERGE (match:Match {id: matchId})
ON CREATE SET
    match.datetime = datetime(row.datetime),
    match.season = toInteger(row.season),
    match.round = row.round,
    match.home_goal = toInteger(row.home_goal),
    match.away_goal = toInteger(row.away_goal),
    match.competition = 'Copa do Brasil',
    match.created_at = datetime()

MERGE (match)-[:IN_SEASON]->(season)
MERGE (match)-[:IN_COMPETITION]->(comp)

WITH match, home, away, row,
     CASE
        WHEN toInteger(row.home_goal) > toInteger(row.away_goal) THEN 'WIN'
        WHEN toInteger(row.home_goal) = toInteger(row.away_goal) THEN 'DRAW'
        ELSE 'LOSS'
     END AS home_result,
     CASE
        WHEN toInteger(row.away_goal) > toInteger(row.home_goal) THEN 'WIN'
        WHEN toInteger(row.away_goal) = toInteger(row.home_goal) THEN 'DRAW'
        ELSE 'LOSS'
     END AS away_result

MERGE (home)-[h:PLAYED_HOME]->(match)
ON CREATE SET
    h.goals_scored = toInteger(row.home_goal),
    h.goals_conceded = toInteger(row.away_goal),
    h.result = home_result

MERGE (away)-[a:PLAYED_AWAY]->(match)
ON CREATE SET
    a.goals_scored = toInteger(row.away_goal),
    a.goals_conceded = toInteger(row.home_goal),
    a.result = away_result

MERGE (home)-[:COMPETES_IN {season: toInteger(row.season)}]->(comp)
MERGE (away)-[:COMPETES_IN {season: toInteger(row.season)}]->(comp);
```

### Step 6: Import Libertadores Matches

```cypher
LOAD CSV WITH HEADERS FROM 'file:///Libertadores_Matches.csv' AS row

WITH row, row.datetime + '-' + row.home_team + '-' + row.away_team AS matchId

// Merge teams (international teams)
MERGE (home:Team {name: row.home_team})
ON CREATE SET
    home.display_name = row.home_team,
    home.created_at = datetime()

MERGE (away:Team {name: row.away_team})
ON CREATE SET
    away.display_name = row.away_team,
    away.created_at = datetime()

// Merge season and competition
MERGE (season:Season {year: toInteger(row.season), competition: 'Copa Libertadores'})
ON CREATE SET season.created_at = datetime()

MERGE (comp:Competition {name: 'Copa Libertadores'})

// Create match
MERGE (match:Match {id: matchId})
ON CREATE SET
    match.datetime = datetime(row.datetime),
    match.season = toInteger(row.season),
    match.home_goal = toInteger(row.home_goal),
    match.away_goal = toInteger(row.away_goal),
    match.competition = 'Copa Libertadores',
    match.stage = row.stage,
    match.created_at = datetime()

MERGE (match)-[:IN_SEASON]->(season)
MERGE (match)-[:IN_COMPETITION]->(comp)

WITH match, home, away, row,
     CASE
        WHEN toInteger(row.home_goal) > toInteger(row.away_goal) THEN 'WIN'
        WHEN toInteger(row.home_goal) = toInteger(row.away_goal) THEN 'DRAW'
        ELSE 'LOSS'
     END AS home_result,
     CASE
        WHEN toInteger(row.away_goal) > toInteger(row.home_goal) THEN 'WIN'
        WHEN toInteger(row.away_goal) = toInteger(row.home_goal) THEN 'DRAW'
        ELSE 'LOSS'
     END AS away_result

MERGE (home)-[h:PLAYED_HOME]->(match)
ON CREATE SET
    h.goals_scored = toInteger(row.home_goal),
    h.goals_conceded = toInteger(row.away_goal),
    h.result = home_result

MERGE (away)-[a:PLAYED_AWAY]->(match)
ON CREATE SET
    a.goals_scored = toInteger(row.away_goal),
    a.goals_conceded = toInteger(row.home_goal),
    a.result = away_result

MERGE (home)-[:COMPETES_IN {season: toInteger(row.season)}]->(comp)
MERGE (away)-[:COMPETES_IN {season: toInteger(row.season)}]->(comp);
```

### Step 7: Enrich with Extended Statistics

```cypher
// Load BR-Football-Dataset with extended stats
LOAD CSV WITH HEADERS FROM 'file:///BR-Football-Dataset.csv' AS row

WITH row,
     datetime({date: date(row.date), time: time(row.time)}) AS match_datetime,
     row.home + '-' + row.away AS match_key

// Find matching matches and add extended stats
MATCH (match:Match)
WHERE match.datetime = match_datetime

WITH match, row
MATCH (home:Team)-[:PLAYED_HOME]->(match)
MATCH (away:Team)-[:PLAYED_AWAY]->(match)

WHERE home.display_name = row.home OR home.name CONTAINS row.home

SET match.home_corner = toInteger(toFloat(row.home_corner)),
    match.away_corner = toInteger(toFloat(row.away_corner)),
    match.home_attack = toInteger(toFloat(row.home_attack)),
    match.away_attack = toInteger(toFloat(row.away_attack)),
    match.home_shots = toInteger(toFloat(row.home_shots)),
    match.away_shots = toInteger(toFloat(row.away_shots)),
    match.total_corners = toInteger(toFloat(row.total_corners))

WITH match, row, home, away

MATCH (home)-[h:PLAYED_HOME]->(match)
MATCH (away)-[a:PLAYED_AWAY]->(match)

SET h.corners = toInteger(toFloat(row.home_corner)),
    h.attacks = toInteger(toFloat(row.home_attack)),
    h.shots = toInteger(toFloat(row.home_shots)),
    a.corners = toInteger(toFloat(row.away_corner)),
    a.attacks = toInteger(toFloat(row.away_attack)),
    a.shots = toInteger(toFloat(row.away_shots));
```

### Step 8: Import Stadiums

```cypher
// Load historical matches with stadium info
LOAD CSV WITH HEADERS FROM 'file:///novo_campeonato_brasileiro.csv' AS row

WITH row
WHERE row.Arena IS NOT NULL AND row.Arena <> ''

MERGE (stadium:Stadium {name: row.Arena})
ON CREATE SET
    stadium.created_at = datetime()

WITH stadium, row, row.ID AS matchId

// Link matches to stadiums
MATCH (match:Match)
WHERE match.id CONTAINS matchId OR
      (toString(match.season) = row.Ano AND
       toString(match.round) = row.Rodada)

MERGE (match)-[:HOSTED_AT]->(stadium);
```

### Step 9: Import FIFA Players

```cypher
// Import Brazilian players from FIFA dataset
LOAD CSV WITH HEADERS FROM 'file:///fifa_data.csv' AS row
WITH row
WHERE row.Nationality = 'Brazil' AND row.ID IS NOT NULL

MERGE (player:Player {id: toInteger(row.ID)})
ON CREATE SET
    player.name = row.Name,
    player.age = toInteger(row.Age),
    player.nationality = row.Nationality,
    player.photo = row.Photo,
    player.overall = toInteger(row.Overall),
    player.potential = toInteger(row.Potential),
    player.position = row.Position,
    player.preferred_foot = row.`Preferred Foot`,
    player.height = row.Height,
    player.weight = row.Weight,
    player.value = row.Value,
    player.wage = row.Wage,
    player.club = row.Club,
    player.created_at = datetime()

// Link players to teams
WITH player, row
WHERE row.Club IS NOT NULL

MATCH (team:Team)
WHERE team.display_name CONTAINS split(row.Club, ' ')[0] OR
      team.name CONTAINS split(row.Club, ' ')[0]

MERGE (player)-[b:BELONGS_TO]->(team)
ON CREATE SET
    b.jersey_number = CASE WHEN row.`Jersey Number` <> '' THEN toInteger(row.`Jersey Number`) ELSE NULL END,
    b.joined_date = CASE WHEN row.Joined <> '' THEN date(row.Joined) ELSE NULL END,
    b.contract_until = CASE WHEN row.`Contract Valid Until` <> '' THEN toInteger(row.`Contract Valid Until`) ELSE NULL END,
    b.wage = row.Wage;
```

## Sample Queries

### 1. Team Performance Analysis

```cypher
// Get Flamengo's win rate in Brasileirao 2023
MATCH (team:Team {name: 'Flamengo-RJ'})-[r:PLAYED_HOME|PLAYED_AWAY]->(match:Match)
WHERE match.season = 2023 AND match.competition = 'Brasileirao'
WITH team,
     count(match) AS total_matches,
     sum(CASE WHEN r.result = 'WIN' THEN 1 ELSE 0 END) AS wins,
     sum(CASE WHEN r.result = 'DRAW' THEN 1 ELSE 0 END) AS draws,
     sum(CASE WHEN r.result = 'LOSS' THEN 1 ELSE 0 END) AS losses,
     sum(r.goals_scored) AS goals_scored,
     sum(r.goals_conceded) AS goals_conceded
RETURN team.name AS team,
       total_matches,
       wins,
       draws,
       losses,
       (wins * 3 + draws) AS points,
       goals_scored,
       goals_conceded,
       (goals_scored - goals_conceded) AS goal_difference,
       round(toFloat(wins) / total_matches * 100, 2) AS win_percentage;
```

### 2. Head-to-Head Records

```cypher
// Flamengo vs Palmeiras all-time record
MATCH (team1:Team {name: 'Flamengo-RJ'})-[r1:PLAYED_HOME|PLAYED_AWAY]->(match:Match)<-[r2:PLAYED_HOME|PLAYED_AWAY]-(team2:Team {name: 'Palmeiras-SP'})
WITH team1, team2, match, r1, r2
RETURN team1.name AS team1,
       team2.name AS team2,
       count(match) AS total_matches,
       sum(CASE WHEN r1.result = 'WIN' THEN 1 ELSE 0 END) AS team1_wins,
       sum(CASE WHEN r2.result = 'WIN' THEN 1 ELSE 0 END) AS team2_wins,
       sum(CASE WHEN r1.result = 'DRAW' THEN 1 ELSE 0 END) AS draws,
       sum(r1.goals_scored) AS team1_goals,
       sum(r2.goals_scored) AS team2_goals;
```

### 3. Top Scorers by Competition

```cypher
// Find matches with highest total goals in Brasileirao
MATCH (match:Match {competition: 'Brasileirao'})
WITH match, (match.home_goal + match.away_goal) AS total_goals
ORDER BY total_goals DESC
LIMIT 10

MATCH (home:Team)-[:PLAYED_HOME]->(match)<-[:PLAYED_AWAY]-(away:Team)
RETURN match.datetime AS date,
       home.name AS home_team,
       match.home_goal AS home_goals,
       away.name AS away_team,
       match.away_goal AS away_goals,
       total_goals,
       match.season AS season,
       match.round AS round
ORDER BY total_goals DESC;
```

### 4. Home vs Away Performance

```cypher
// Compare team's home and away performance
MATCH (team:Team {name: 'Sao Paulo-SP'})
WITH team

// Home stats
OPTIONAL MATCH (team)-[h:PLAYED_HOME]->(home_match:Match)
WHERE home_match.season = 2023
WITH team,
     count(home_match) AS home_matches,
     sum(CASE WHEN h.result = 'WIN' THEN 1 ELSE 0 END) AS home_wins,
     sum(h.goals_scored) AS home_goals_scored,
     sum(h.goals_conceded) AS home_goals_conceded

// Away stats
OPTIONAL MATCH (team)-[a:PLAYED_AWAY]->(away_match:Match)
WHERE away_match.season = 2023
WITH team, home_matches, home_wins, home_goals_scored, home_goals_conceded,
     count(away_match) AS away_matches,
     sum(CASE WHEN a.result = 'WIN' THEN 1 ELSE 0 END) AS away_wins,
     sum(a.goals_scored) AS away_goals_scored,
     sum(a.goals_conceded) AS away_goals_conceded

RETURN team.name AS team,
       home_matches,
       home_wins,
       round(toFloat(home_wins) / home_matches * 100, 2) AS home_win_pct,
       home_goals_scored,
       home_goals_conceded,
       away_matches,
       away_wins,
       round(toFloat(away_wins) / away_matches * 100, 2) AS away_win_pct,
       away_goals_scored,
       away_goals_conceded;
```

### 5. Competition Success Rate

```cypher
// Which teams have played in multiple competitions?
MATCH (team:Team)-[:COMPETES_IN]->(comp:Competition)
WITH team, collect(DISTINCT comp.name) AS competitions
WHERE size(competitions) >= 2
RETURN team.name AS team,
       team.state AS state,
       competitions,
       size(competitions) AS num_competitions
ORDER BY num_competitions DESC, team.name;
```

### 6. Season Trends

```cypher
// Goal scoring trends by season in Brasileirao
MATCH (match:Match {competition: 'Brasileirao'})
WITH match.season AS season,
     avg(match.home_goal + match.away_goal) AS avg_goals_per_match,
     sum(match.home_goal + match.away_goal) AS total_goals,
     count(match) AS total_matches
RETURN season,
       total_matches,
       total_goals,
       round(avg_goals_per_match, 2) AS avg_goals
ORDER BY season DESC;
```

### 7. Player Analysis

```cypher
// Find Brazilian players in top clubs by overall rating
MATCH (player:Player {nationality: 'Brazil'})
WHERE player.overall >= 85
RETURN player.name AS player,
       player.age AS age,
       player.overall AS rating,
       player.potential AS potential,
       player.position AS position,
       player.club AS club,
       player.value AS value
ORDER BY player.overall DESC, player.potential DESC
LIMIT 20;
```

### 8. Players by Team

```cypher
// Get all Brazilian players for a specific team
MATCH (player:Player)-[b:BELONGS_TO]->(team:Team)
WHERE team.name = 'Flamengo-RJ'
RETURN player.name AS player,
       player.position AS position,
       player.overall AS rating,
       player.age AS age,
       b.jersey_number AS number,
       player.value AS market_value
ORDER BY player.overall DESC;
```

### 9. Stadium Analysis

```cypher
// Most used stadiums with match statistics
MATCH (match:Match)-[:HOSTED_AT]->(stadium:Stadium)
WITH stadium,
     count(match) AS matches_hosted,
     avg(match.home_goal + match.away_goal) AS avg_goals
WHERE matches_hosted >= 10
RETURN stadium.name AS stadium,
       matches_hosted,
       round(avg_goals, 2) AS avg_goals_per_match
ORDER BY matches_hosted DESC
LIMIT 15;
```

### 10. Advanced: Recent Form

```cypher
// Get last 5 matches for a team
MATCH (team:Team {name: 'Palmeiras-SP'})-[r:PLAYED_HOME|PLAYED_AWAY]->(match:Match)
WHERE match.competition = 'Brasileirao'
WITH team, match, r
ORDER BY match.datetime DESC
LIMIT 5

MATCH (opponent:Team)-[:PLAYED_HOME|PLAYED_AWAY]->(match)
WHERE opponent <> team

RETURN match.datetime AS date,
       CASE WHEN type(r) = 'PLAYED_HOME' THEN 'Home' ELSE 'Away' END AS venue,
       opponent.name AS opponent,
       r.goals_scored AS goals_for,
       r.goals_conceded AS goals_against,
       r.result AS result
ORDER BY match.datetime DESC;
```

### 11. Complex: Championship Standings

```cypher
// Calculate Brasileirao 2023 standings
MATCH (team:Team)-[r:PLAYED_HOME|PLAYED_AWAY]->(match:Match)
WHERE match.season = 2023 AND match.competition = 'Brasileirao'
WITH team,
     count(match) AS played,
     sum(CASE WHEN r.result = 'WIN' THEN 1 ELSE 0 END) AS wins,
     sum(CASE WHEN r.result = 'DRAW' THEN 1 ELSE 0 END) AS draws,
     sum(CASE WHEN r.result = 'LOSS' THEN 1 ELSE 0 END) AS losses,
     sum(r.goals_scored) AS gf,
     sum(r.goals_conceded) AS ga
WITH team, played, wins, draws, losses, gf, ga,
     (wins * 3 + draws) AS points,
     (gf - ga) AS gd
RETURN team.name AS team,
       played,
       wins,
       draws,
       losses,
       gf,
       ga,
       gd,
       points
ORDER BY points DESC, gd DESC, gf DESC
LIMIT 20;
```

### 12. Path Finding: Competition Paths

```cypher
// Find teams that have competed together in multiple competitions
MATCH path = (team1:Team)-[:COMPETES_IN]->(comp:Competition)<-[:COMPETES_IN]-(team2:Team)
WHERE team1.state = 'SP' AND team2.state = 'RJ'
WITH team1, team2, collect(DISTINCT comp.name) AS shared_competitions
WHERE size(shared_competitions) >= 2
RETURN team1.name AS team1,
       team2.name AS team2,
       shared_competitions,
       size(shared_competitions) AS num_shared
ORDER BY num_shared DESC, team1.name
LIMIT 20;
```

## Performance Optimization

### Index Recommendations

The indexes created in Step 1 cover most use cases. Monitor query performance with:

```cypher
// Check index usage
:schema

// Profile a query to see index usage
PROFILE
MATCH (team:Team {name: 'Flamengo-RJ'})-[r:PLAYED_HOME]->(match:Match)
WHERE match.season = 2023
RETURN count(match);

// Show query execution plan
EXPLAIN
MATCH (team:Team)-[:PLAYED_HOME]->(match:Match)
WHERE match.datetime >= datetime('2023-01-01')
RETURN team.name, count(match);
```

### Additional Performance Indexes

```cypher
// Composite index for common query patterns
CREATE INDEX match_season_competition IF NOT EXISTS
FOR (m:Match) ON (m.season, m.competition);

// Range index for datetime queries
CREATE INDEX match_datetime_range IF NOT EXISTS
FOR (m:Match) ON (m.datetime);

// Index for relationship properties (Neo4j 5.x+)
CREATE INDEX played_home_result IF NOT EXISTS
FOR ()-[r:PLAYED_HOME]-() ON (r.result);

CREATE INDEX played_away_result IF NOT EXISTS
FOR ()-[r:PLAYED_AWAY]-() ON (r.result);
```

### Query Optimization Tips

1. **Use Parameters**: Always use parameterized queries to enable query plan caching
```cypher
// Good
MATCH (team:Team {name: $teamName})
RETURN team;

// Avoid
MATCH (team:Team {name: 'Flamengo-RJ'})
RETURN team;
```

2. **Limit Early**: Apply LIMIT as early as possible
```cypher
// Good
MATCH (match:Match)
WHERE match.season = 2023
WITH match
ORDER BY match.datetime DESC
LIMIT 10
MATCH (home:Team)-[:PLAYED_HOME]->(match)
RETURN home, match;

// Avoid
MATCH (home:Team)-[:PLAYED_HOME]->(match:Match)
WHERE match.season = 2023
RETURN home, match
ORDER BY match.datetime DESC
LIMIT 10;
```

3. **Use WHERE Instead of Filtering in WITH**
```cypher
// Good
MATCH (team:Team)
WHERE team.state = 'SP'
RETURN team;

// Avoid
MATCH (team:Team)
WITH team WHERE team.state = 'SP'
RETURN team;
```

### Database Configuration

For optimal performance, configure Neo4j memory settings:

```bash
# neo4j.conf or via environment variables
NEO4J_dbms_memory_heap_initial__size=2g
NEO4J_dbms_memory_heap_max__size=4g
NEO4J_dbms_memory_pagecache_size=2g

# For Docker
docker run \
    --env NEO4J_dbms_memory_heap_initial__size=2g \
    --env NEO4J_dbms_memory_heap_max__size=4g \
    --env NEO4J_dbms_memory_pagecache_size=2g \
    neo4j:latest
```

### Monitoring and Maintenance

```cypher
// Database statistics
CALL db.stats.retrieve('GRAPH COUNTS');

// Query slow queries (if query logging enabled)
CALL dbms.listQueries();

// Kill long-running queries
CALL dbms.listQueries() YIELD queryId, elapsedTimeMillis
WHERE elapsedTimeMillis > 10000
CALL dbms.killQuery(queryId) YIELD queryId as killed
RETURN killed;

// Rebuild indexes if performance degrades
DROP INDEX index_name IF EXISTS;
CREATE INDEX index_name FOR (n:Label) ON (n.property);
```

## Data Validation

After import, validate the data:

```cypher
// Count nodes by type
MATCH (n)
RETURN labels(n) AS type, count(n) AS count
ORDER BY count DESC;

// Count relationships by type
MATCH ()-[r]->()
RETURN type(r) AS relationship, count(r) AS count
ORDER BY count DESC;

// Check for orphaned nodes
MATCH (n)
WHERE NOT (n)--()
RETURN labels(n) AS type, count(n) AS orphans;

// Verify match data integrity
MATCH (match:Match)
WHERE NOT (match)-[:IN_SEASON]->()
   OR NOT (match)-[:IN_COMPETITION]->()
RETURN match.id AS incomplete_match;

// Check for missing relationships
MATCH (team:Team)
WHERE NOT (team)-[:COMPETES_IN]->()
RETURN team.name AS team_without_competition;
```

## Backup and Restore

### Backup

```bash
# Using Neo4j Admin (requires database stop)
neo4j-admin database dump neo4j --to-path=/backups

# Using APOC (online backup)
CALL apoc.export.cypher.all('/backups/brazilian-soccer-backup.cypher', {
    format: 'cypher-shell'
});
```

### Restore

```bash
# From dump
neo4j-admin database load neo4j --from-path=/backups

# From Cypher export
cat /backups/brazilian-soccer-backup.cypher | cypher-shell
```

## Next Steps

1. **Extend the Schema**: Add more node types (Coach, Referee, etc.)
2. **Import More Data**: Historical seasons, player transfers, injuries
3. **Build Applications**: REST API, GraphQL endpoint, web dashboard
4. **Machine Learning**: Predict match outcomes using graph features
5. **Real-time Updates**: Integrate with live match data feeds

## Troubleshooting

### Common Issues

**Issue**: CSV files not found
```
Solution: Ensure CSV files are in neo4j/import directory
docker exec brazilian-soccer-neo4j ls /var/lib/neo4j/import
```

**Issue**: Datetime parsing errors
```cypher
// Use datetime() with different formats
datetime({epochMillis: timestamp})
datetime('2023-05-20T16:00:00')
```

**Issue**: Memory errors during large imports
```
Solution: Increase heap size or use USING PERIODIC COMMIT
USING PERIODIC COMMIT 500
LOAD CSV WITH HEADERS FROM 'file:///large-file.csv' AS row
...
```

**Issue**: Duplicate nodes
```cypher
// Clean up duplicates
MATCH (n:Team)
WITH n.name AS name, collect(n) AS nodes
WHERE size(nodes) > 1
UNWIND tail(nodes) AS duplicate
DETACH DELETE duplicate;
```

## Resources

- [Neo4j Documentation](https://neo4j.com/docs/)
- [Cypher Query Language](https://neo4j.com/docs/cypher-manual/current/)
- [APOC Library](https://neo4j.com/labs/apoc/)
- [Graph Data Science Library](https://neo4j.com/docs/graph-data-science/current/)

## Support

For issues with this setup, please check:
1. Neo4j logs: `docker logs brazilian-soccer-neo4j`
2. Query execution with EXPLAIN/PROFILE
3. Database constraints and indexes with `:schema`
