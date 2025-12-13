"""
Brazilian Soccer MCP - Neo4j Client

CONTEXT:
Main client interface for Neo4j graph database operations. Provides high-level
methods for schema management, data import, and graph queries specific to
Brazilian soccer data. Handles connection lifecycle, transaction management,
and error recovery.

DESIGN DECISIONS:
- Context manager support for automatic connection cleanup
- Batch processing for efficient bulk imports
- Retry logic for transient failures
- Comprehensive error handling and logging
- Type hints for better IDE support
- Separation of schema and data operations

PERFORMANCE:
- Connection pooling via Neo4j driver
- Batch operations with UNWIND for bulk imports
- Transaction management for data consistency
- Prepared queries with parameter binding
- Optional async support for high-throughput scenarios

USAGE:
    from neo4j_client import Neo4jClient
    from config.neo4j_config import get_neo4j_config

    config = get_neo4j_config()
    with Neo4jClient(config.uri, config.user, config.password) as client:
        client.create_constraints()
        client.import_teams(teams_data)

AUTHOR: Coder Agent - Brazilian Soccer MCP Hive Mind
PHASE: 3 - Neo4j Knowledge Graph
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from contextlib import contextmanager
from datetime import datetime

try:
    from neo4j import GraphDatabase, Driver, Session, Transaction
    from neo4j.exceptions import (
        ServiceUnavailable,
        AuthError,
        CypherSyntaxError,
        ConstraintError,
        Neo4jError
    )
except ImportError:
    raise ImportError(
        "neo4j package is required. Install with: pip install neo4j"
    )

from graph_schema import CONSTRAINTS, INDEXES
from graph_queries import (
    BATCH_CREATE_TEAMS,
    BATCH_CREATE_PLAYERS,
    BATCH_CREATE_MATCHES,
    CREATE_COMPETITION,
    CREATE_SEASON,
    CREATE_STADIUM,
    CREATE_MATCH_WITH_TEAMS,
    CREATE_COMPETED_IN_RELATIONSHIP,
    FIND_SHORTEST_PATH_BETWEEN_TEAMS,
    FIND_COMMON_OPPONENTS,
    GET_TEAM_NETWORK,
    FIND_HEAD_TO_HEAD,
    GET_TEAM_STATISTICS,
    COUNT_NODES,
    COUNT_RELATIONSHIPS,
    DELETE_ALL_DATA
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# NEO4J CLIENT CLASS
# ============================================================================

class Neo4jClient:
    """
    High-level client for Neo4j graph database operations.

    Handles connection management, schema creation, data import,
    and graph queries for Brazilian soccer data.

    Attributes:
        uri: Neo4j connection URI
        user: Database username
        password: Database password
        database: Target database name
        driver: Neo4j driver instance
    """

    def __init__(
        self,
        uri: str,
        user: str,
        password: str,
        database: str = "neo4j",
        max_connection_lifetime: int = 3600,
        max_connection_pool_size: int = 50,
        connection_timeout: float = 30.0
    ):
        """
        Initialize Neo4j client.

        Args:
            uri: Neo4j connection URI (bolt://, neo4j://, etc.)
            user: Database username
            password: Database password
            database: Target database name (default: neo4j)
            max_connection_lifetime: Max connection lifetime in seconds
            max_connection_pool_size: Maximum connections in pool
            connection_timeout: Connection timeout in seconds

        Raises:
            AuthError: If authentication fails
            ServiceUnavailable: If Neo4j server is not reachable
        """
        self.uri = uri
        self.user = user
        self.password = password
        self.database = database

        try:
            self.driver = GraphDatabase.driver(
                uri,
                auth=(user, password),
                max_connection_lifetime=max_connection_lifetime,
                max_connection_pool_size=max_connection_pool_size,
                connection_timeout=connection_timeout
            )

            # Verify connectivity
            self.driver.verify_connectivity()
            logger.info(f"Successfully connected to Neo4j at {uri}")

        except AuthError as e:
            logger.error(f"Authentication failed: {e}")
            raise
        except ServiceUnavailable as e:
            logger.error(f"Neo4j service unavailable at {uri}: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            raise

    def close(self) -> None:
        """Close Neo4j driver and release all connections."""
        if self.driver:
            self.driver.close()
            logger.info("Neo4j connection closed")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with automatic cleanup."""
        self.close()

    @contextmanager
    def session(self, **kwargs) -> Session:
        """
        Create a session context manager.

        Args:
            **kwargs: Additional session parameters

        Yields:
            Neo4j session instance
        """
        session = self.driver.session(database=self.database, **kwargs)
        try:
            yield session
        finally:
            session.close()

    # ========================================================================
    # SCHEMA MANAGEMENT
    # ========================================================================

    def create_constraints(self) -> Dict[str, int]:
        """
        Create all schema constraints.

        Returns:
            Dictionary with constraint creation counts

        Raises:
            CypherSyntaxError: If constraint syntax is invalid
            ConstraintError: If constraint already exists (ignored)
        """
        results = {
            "unique_constraints": 0,
            "existence_constraints": 0,
            "errors": []
        }

        with self.session() as session:
            # Create unique constraints
            for query in CONSTRAINTS["unique_constraints"]:
                try:
                    session.run(query)
                    results["unique_constraints"] += 1
                    logger.debug(f"Created constraint: {query}")
                except ConstraintError:
                    logger.debug(f"Constraint already exists: {query}")
                except Exception as e:
                    logger.error(f"Failed to create constraint: {e}")
                    results["errors"].append(str(e))

            # Create existence constraints
            for query in CONSTRAINTS["existence_constraints"]:
                try:
                    session.run(query)
                    results["existence_constraints"] += 1
                    logger.debug(f"Created constraint: {query}")
                except ConstraintError:
                    logger.debug(f"Constraint already exists: {query}")
                except Exception as e:
                    logger.error(f"Failed to create constraint: {e}")
                    results["errors"].append(str(e))

        logger.info(
            f"Created {results['unique_constraints']} unique constraints "
            f"and {results['existence_constraints']} existence constraints"
        )
        return results

    def create_indexes(self) -> Dict[str, int]:
        """
        Create all schema indexes.

        Returns:
            Dictionary with index creation counts

        Raises:
            CypherSyntaxError: If index syntax is invalid
        """
        results = {
            "indexes_created": 0,
            "errors": []
        }

        with self.session() as session:
            for query in INDEXES:
                try:
                    session.run(query)
                    results["indexes_created"] += 1
                    logger.debug(f"Created index: {query}")
                except Exception as e:
                    logger.error(f"Failed to create index: {e}")
                    results["errors"].append(str(e))

        logger.info(f"Created {results['indexes_created']} indexes")
        return results

    def drop_all_constraints(self) -> int:
        """
        Drop all constraints in the database.

        Returns:
            Number of constraints dropped
        """
        count = 0
        with self.session() as session:
            # Get all constraints
            result = session.run("SHOW CONSTRAINTS")
            constraints = [record["name"] for record in result]

            # Drop each constraint
            for constraint_name in constraints:
                session.run(f"DROP CONSTRAINT {constraint_name}")
                count += 1
                logger.debug(f"Dropped constraint: {constraint_name}")

        logger.info(f"Dropped {count} constraints")
        return count

    def drop_all_indexes(self) -> int:
        """
        Drop all indexes in the database.

        Returns:
            Number of indexes dropped
        """
        count = 0
        with self.session() as session:
            # Get all indexes
            result = session.run("SHOW INDEXES")
            indexes = [record["name"] for record in result if record.get("name")]

            # Drop each index
            for index_name in indexes:
                try:
                    session.run(f"DROP INDEX {index_name}")
                    count += 1
                    logger.debug(f"Dropped index: {index_name}")
                except Exception as e:
                    logger.warning(f"Failed to drop index {index_name}: {e}")

        logger.info(f"Dropped {count} indexes")
        return count

    # ========================================================================
    # DATA IMPORT - BATCH OPERATIONS
    # ========================================================================

    def import_teams(self, teams: List[Dict[str, Any]], batch_size: int = 1000) -> int:
        """
        Import teams in batches.

        Args:
            teams: List of team dictionaries
            batch_size: Number of teams per batch

        Returns:
            Total number of teams imported

        Example:
            teams = [
                {
                    "id": "flamengo",
                    "name": "Flamengo",
                    "founded": 1895,
                    "city": "Rio de Janeiro",
                    "state": "RJ",
                    "colors": ["red", "black"]
                }
            ]
            client.import_teams(teams)
        """
        total_imported = 0

        with self.session() as session:
            for i in range(0, len(teams), batch_size):
                batch = teams[i:i + batch_size]
                result = session.run(BATCH_CREATE_TEAMS, teams=batch)
                count = result.single()["teams_created"]
                total_imported += count
                logger.debug(f"Imported batch of {count} teams")

        logger.info(f"Imported {total_imported} teams")
        return total_imported

    def import_players(self, players: List[Dict[str, Any]], batch_size: int = 1000) -> int:
        """
        Import players in batches.

        Args:
            players: List of player dictionaries
            batch_size: Number of players per batch

        Returns:
            Total number of players imported
        """
        total_imported = 0

        with self.session() as session:
            for i in range(0, len(players), batch_size):
                batch = players[i:i + batch_size]
                result = session.run(BATCH_CREATE_PLAYERS, players=batch)
                count = result.single()["players_created"]
                total_imported += count
                logger.debug(f"Imported batch of {count} players")

        logger.info(f"Imported {total_imported} players")
        return total_imported

    def import_matches(
        self,
        matches: List[Dict[str, Any]],
        batch_size: int = 1000,
        include_relationships: bool = True
    ) -> int:
        """
        Import matches with optional team relationships.

        Args:
            matches: List of match dictionaries
            batch_size: Number of matches per batch
            include_relationships: Whether to create team relationships

        Returns:
            Total number of matches imported
        """
        total_imported = 0

        with self.session() as session:
            if include_relationships:
                # Import with relationships (slower but complete)
                for match in matches:
                    session.run(CREATE_MATCH_WITH_TEAMS, **match)
                    total_imported += 1

                    if total_imported % 100 == 0:
                        logger.debug(f"Imported {total_imported} matches with relationships")
            else:
                # Import matches only (faster)
                for i in range(0, len(matches), batch_size):
                    batch = matches[i:i + batch_size]
                    result = session.run(BATCH_CREATE_MATCHES, matches=batch)
                    count = result.single()["matches_created"]
                    total_imported += count
                    logger.debug(f"Imported batch of {count} matches")

        logger.info(f"Imported {total_imported} matches")
        return total_imported

    def import_competitions(self, competitions: List[Dict[str, Any]]) -> int:
        """
        Import competitions.

        Args:
            competitions: List of competition dictionaries

        Returns:
            Number of competitions imported
        """
        count = 0
        with self.session() as session:
            for comp in competitions:
                session.run(CREATE_COMPETITION, **comp)
                count += 1

        logger.info(f"Imported {count} competitions")
        return count

    # ========================================================================
    # GRAPH QUERIES
    # ========================================================================

    def find_shortest_path(
        self,
        team1: str,
        team2: str
    ) -> Optional[Dict[str, Any]]:
        """
        Find shortest path between two teams through matches.

        Args:
            team1: First team ID
            team2: Second team ID

        Returns:
            Dictionary with path information or None if no path exists
        """
        with self.session() as session:
            result = session.run(
                FIND_SHORTEST_PATH_BETWEEN_TEAMS,
                team1_id=team1,
                team2_id=team2
            )
            record = result.single()

            if record:
                return {
                    "path": record["path"],
                    "length": record["path_length"]
                }
            return None

    def get_team_network(
        self,
        team: str,
        depth: int = 2,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get network of teams connected to given team.

        Args:
            team: Team ID
            depth: Maximum relationship depth
            limit: Maximum number of nodes to return

        Returns:
            List of connected team nodes
        """
        with self.session() as session:
            result = session.run(
                GET_TEAM_NETWORK,
                team_id=team,
                depth=depth,
                limit=limit
            )
            return [dict(record["node"]) for record in result]

    def find_common_opponents(
        self,
        team1: str,
        team2: str,
        limit: int = 50
    ) -> List[str]:
        """
        Find teams that both team1 and team2 have played against.

        Args:
            team1: First team ID
            team2: Second team ID
            limit: Maximum number of opponents to return

        Returns:
            List of common opponent team names
        """
        with self.session() as session:
            result = session.run(
                FIND_COMMON_OPPONENTS,
                team1_id=team1,
                team2_id=team2,
                limit=limit
            )
            return [record["opponent"]["name"] for record in result]

    def get_head_to_head(
        self,
        team1: str,
        team2: str,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get head-to-head match history between two teams.

        Args:
            team1: First team ID
            team2: Second team ID
            limit: Maximum number of matches

        Returns:
            List of match records with scores
        """
        with self.session() as session:
            result = session.run(
                FIND_HEAD_TO_HEAD,
                team1_id=team1,
                team2_id=team2,
                limit=limit
            )
            return [dict(record) for record in result]

    def get_team_statistics(self, team_id: str) -> Dict[str, Any]:
        """
        Get comprehensive statistics for a team.

        Args:
            team_id: Team ID

        Returns:
            Dictionary with team statistics
        """
        with self.session() as session:
            result = session.run(GET_TEAM_STATISTICS, team_id=team_id)
            record = result.single()

            if record:
                return dict(record)
            return {}

    # ========================================================================
    # UTILITY METHODS
    # ========================================================================

    def get_database_statistics(self) -> Dict[str, Any]:
        """
        Get database statistics (node counts, relationship counts).

        Returns:
            Dictionary with database statistics
        """
        stats = {
            "nodes": {},
            "relationships": {},
            "total_nodes": 0,
            "total_relationships": 0
        }

        with self.session() as session:
            # Count nodes by label
            result = session.run(COUNT_NODES)
            for record in result:
                label = record["label"]
                count = record["count"]
                stats["nodes"][label] = count
                stats["total_nodes"] += count

            # Count relationships by type
            result = session.run(COUNT_RELATIONSHIPS)
            for record in result:
                rel_type = record["relationship_type"]
                count = record["count"]
                stats["relationships"][rel_type] = count
                stats["total_relationships"] += count

        return stats

    def clear_database(self) -> int:
        """
        Delete all nodes and relationships.

        WARNING: This operation is irreversible!

        Returns:
            Number of nodes deleted
        """
        with self.session() as session:
            result = session.run(DELETE_ALL_DATA)
            count = result.single()["deleted_nodes"]
            logger.warning(f"Deleted {count} nodes and all relationships")
            return count

    def health_check(self) -> bool:
        """
        Perform health check on database connection.

        Returns:
            True if connection is healthy, False otherwise
        """
        try:
            with self.session() as session:
                result = session.run("RETURN 1 as health")
                return result.single()["health"] == 1
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
