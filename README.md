# Brazilian Soccer MCP Server with Neo4j Knowledge Graph

A comprehensive Python implementation for querying Brazilian soccer data through a knowledge graph interface. This project provides tools to load, query, and visualize data from multiple Brazilian soccer competitions.

## Project Overview

This MCP (Model Context Protocol) server enables natural language queries about Brazilian soccer, including:
- Match results and statistics
- Team performance analysis
- Player information from FIFA database
- Head-to-head comparisons
- Competition standings

## Implementation Status

### Completed Phases

#### Phase 1: Data Layer
- **Models** (`src/models.py`): Core data structures for Team, Player, Match, Competition
- **Data Loader** (`src/data_loader.py`): CSV parsing for all 6 datasets with UTF-8 support
- **Team Normalizer** (`src/team_normalizer.py`): 60+ team name mappings for consistent matching

#### Phase 2: Query Engine
- **Statistics** (`src/statistics.py`): TeamStats, HeadToHeadStats, Standing dataclasses
- **Query Engine** (`src/query_engine.py`): Comprehensive query methods for matches, teams, players

#### Phase 3: Neo4j Knowledge Graph
- **Graph Schema** (`src/graph_schema.py`): Node/relationship definitions (6 nodes, 8 relationships)
- **Graph Queries** (`src/graph_queries.py`): Pre-built Cypher query templates
- **Neo4j Client** (`src/neo4j_client.py`): Full-featured database client with batch imports
- **Configuration** (`config/neo4j_config.py`): Environment-based settings

### Testing

Comprehensive BDD-style tests using PyTest:
- `tests/test_data_loader.py` - Data loading tests
- `tests/test_query_engine.py` - Query engine tests
- `tests/test_neo4j_client.py` - Neo4j integration tests
- `tests/test_team_normalizer.py` - Team name normalization tests
- `tests/test_integration.py` - End-to-end integration tests

## Data Sources

All datasets are included in `data/kaggle/`:

| File | Records | Source | License |
|------|---------|--------|---------|
| `Brasileirao_Matches.csv` | 4,180 | Kaggle | CC BY 4.0 |
| `Brazilian_Cup_Matches.csv` | 1,337 | Kaggle | CC BY 4.0 |
| `Libertadores_Matches.csv` | 1,255 | Kaggle | CC BY 4.0 |
| `BR-Football-Dataset.csv` | 10,296 | Kaggle | CC0 |
| `novo_campeonato_brasileiro.csv` | 6,886 | Kaggle | CC BY 4.0 |
| `fifa_data.csv` | 18,207 | Kaggle | Apache 2.0 |

## Installation

### Prerequisites
- Python 3.9+
- Neo4j 4.x+ (optional, for graph features)

### Setup

```bash
# Clone the repository
git clone https://github.com/your-repo/brazilian-soccer-mcp.git
cd brazilian-soccer-mcp

# Install dependencies
pip install -r requirements.txt

# For testing
pip install -r requirements-test.txt
```

### Neo4j Setup (Optional)

See [docs/NEO4J_SETUP.md](docs/NEO4J_SETUP.md) for detailed Neo4j installation and configuration.

Quick start with Docker:
```bash
docker run \
    --name brazilian-soccer-neo4j \
    -p 7474:7474 -p 7687:7687 \
    -d \
    --env NEO4J_AUTH=neo4j/brazilian_soccer_2024 \
    neo4j:latest
```

## Usage

### Basic Data Loading

```python
from src.data_loader import DataLoader

# Load all data
loader = DataLoader()
data = loader.load_all()

print(f"Loaded {len(data['brasileirao_matches'])} Brasileirao matches")
print(f"Loaded {len(data['players'])} FIFA players")
```

### Query Engine

```python
from src.query_engine import QueryEngine
from src.data_loader import DataLoader

# Initialize
loader = DataLoader()
engine = QueryEngine(loader)

# Find matches between teams
matches = engine.find_matches_between("Flamengo", "Fluminense")
for match in matches[:5]:
    print(f"{match.datetime}: {match.home_team} {match.home_goals}-{match.away_goals} {match.away_team}")

# Get team statistics
stats = engine.get_team_statistics("Palmeiras", season=2023)
print(f"Palmeiras 2023: {stats.wins}W {stats.draws}D {stats.losses}L")

# Find top-rated Brazilian players
players = engine.get_brazilian_players_at_brazilian_clubs()
for player in players[:10]:
    print(f"{player.name} - {player.club} - Overall: {player.overall_rating}")
```

### Neo4j Graph Queries

```python
from src.neo4j_client import Neo4jClient
from config.neo4j_config import get_neo4j_config

config = get_neo4j_config()

with Neo4jClient(config.uri, config.user, config.password) as client:
    # Find path between teams
    path = client.find_shortest_path("Flamengo", "Palmeiras")

    # Get team network
    network = client.get_team_network("Corinthians", depth=2)

    # Head-to-head statistics
    h2h = client.get_head_to_head("Santos", "Sao Paulo")
```

## Project Structure

```
brazilian-soccer-mcp/
├── src/
│   ├── __init__.py
│   ├── models.py           # Data models (Team, Player, Match, Competition)
│   ├── data_loader.py      # CSV data loading
│   ├── team_normalizer.py  # Team name normalization
│   ├── query_engine.py     # Query methods
│   ├── statistics.py       # Statistical dataclasses
│   ├── neo4j_client.py     # Neo4j database client
│   ├── graph_schema.py     # Graph schema definitions
│   └── graph_queries.py    # Cypher query templates
├── tests/
│   ├── conftest.py         # PyTest fixtures
│   ├── test_data_loader.py
│   ├── test_query_engine.py
│   ├── test_neo4j_client.py
│   ├── test_team_normalizer.py
│   └── test_integration.py
├── config/
│   └── neo4j_config.py     # Neo4j configuration
├── data/
│   └── kaggle/             # CSV datasets
├── docs/
│   └── NEO4J_SETUP.md      # Neo4j setup guide
├── examples/
│   └── basic_usage.py      # Usage examples
├── requirements.txt
├── requirements-test.txt
└── README.md
```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_query_engine.py -v

# Run BDD-style tests only
pytest -k "Given" -v
```

## Key Features

- **UTF-8 Support**: Full support for Portuguese characters (São Paulo, Grêmio, Avaí)
- **Team Name Normalization**: Handles 60+ team name variations
- **Multiple Date Formats**: Parses ISO, Brazilian, and timestamp formats
- **Type Safety**: Complete type hints throughout codebase
- **BDD Testing**: Given-When-Then structured tests
- **Graph Database**: Neo4j integration for relationship queries
- **Performance**: Indexed lookups and caching

## API Reference

### QueryEngine Methods

#### Match Queries
- `find_matches_between(team1, team2)` - All matches between two teams
- `find_matches_by_team(team)` - Team's match history
- `find_matches_by_date_range(start, end)` - Matches in date range
- `find_matches_by_competition(competition)` - Competition matches
- `find_matches_by_season(season)` - Season matches

#### Team Queries
- `get_team_statistics(team, season)` - Team statistics
- `get_head_to_head(team1, team2)` - Head-to-head comparison
- `get_team_home_record(team, season)` - Home performance
- `get_top_teams_by_goals(season, limit)` - Goal rankings

#### Player Queries
- `find_players_by_name(name)` - Search by name
- `find_players_by_nationality(nationality)` - Filter by country
- `find_players_by_club(club)` - Club roster
- `get_top_rated_players(limit)` - Highest-rated players

#### Statistical Queries
- `get_competition_standings(competition, season)` - League tables
- `get_biggest_wins(competition, limit)` - Largest margins
- `get_average_goals_per_match(competition, season)` - Goal averages

## Development

This project was developed using the **Hive Mind** collective intelligence approach with specialized agents:
- **Researcher Agent**: Data analysis and documentation
- **Coder Agents**: Phase 1-3 implementation
- **Tester Agent**: BDD test suite creation

### Built With
- Python 3.9+
- Neo4j Graph Database
- PyTest for testing
- Claude Code Hive Mind orchestration

## License

This project uses datasets with the following licenses:
- CC BY 4.0 (Attribution required)
- CC0 (Public Domain)
- Apache 2.0

## References

- [MCP Protocol Documentation](https://modelcontextprotocol.io)
- [Neo4j Documentation](https://neo4j.com/docs/)
- [Kaggle Brazilian Soccer Datasets](https://www.kaggle.com/datasets/ricardomattos05/jogos-do-campeonato-brasileiro)

## Contributing

Contributions are welcome! Please ensure all tests pass before submitting a PR:

```bash
pytest --cov=src --cov-fail-under=80
```
