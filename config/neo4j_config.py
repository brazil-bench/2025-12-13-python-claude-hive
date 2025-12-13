"""
Brazilian Soccer MCP - Neo4j Configuration

CONTEXT:
Configuration module for Neo4j database connections. Manages connection
parameters, authentication, and environment-specific settings. Supports
both local development and production deployments with secure credential
management.

DESIGN DECISIONS:
- Environment variables for sensitive data (no hardcoded credentials)
- Multiple configuration profiles (dev, test, prod)
- Connection pooling and timeout settings
- SSL/TLS support for production environments
- Fallback defaults for development

SECURITY:
- Never commit credentials to version control
- Use .env files for local development
- Use secrets management in production
- Support for encrypted connections

USAGE:
    from config.neo4j_config import get_neo4j_config
    config = get_neo4j_config()
    driver = GraphDatabase.driver(config.uri, auth=config.auth)

AUTHOR: Coder Agent - Brazilian Soccer MCP Hive Mind
PHASE: 3 - Neo4j Knowledge Graph
"""

import os
from dataclasses import dataclass
from typing import Optional, Dict, Any
from pathlib import Path

# ============================================================================
# CONFIGURATION DATACLASS
# ============================================================================

@dataclass
class Neo4jConfig:
    """
    Neo4j database configuration.

    Attributes:
        uri: Neo4j connection URI (bolt://, neo4j://, bolt+s://, neo4j+s://)
        user: Database username
        password: Database password
        database: Target database name (default: neo4j)
        max_connection_lifetime: Max connection lifetime in seconds
        max_connection_pool_size: Maximum number of connections in pool
        connection_timeout: Connection timeout in seconds
        encrypted: Whether to use encrypted connection
        trust: SSL trust strategy (TRUST_ALL_CERTIFICATES, TRUST_SYSTEM_CA_SIGNED_CERTIFICATES)
    """
    uri: str
    user: str
    password: str
    database: str = "neo4j"
    max_connection_lifetime: int = 3600
    max_connection_pool_size: int = 50
    connection_timeout: float = 30.0
    encrypted: bool = False
    trust: str = "TRUST_ALL_CERTIFICATES"

    @property
    def auth(self) -> tuple:
        """Return authentication tuple for Neo4j driver."""
        return (self.user, self.password)

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary (excludes sensitive data)."""
        return {
            "uri": self.uri,
            "user": self.user,
            "database": self.database,
            "max_connection_lifetime": self.max_connection_lifetime,
            "max_connection_pool_size": self.max_connection_pool_size,
            "connection_timeout": self.connection_timeout,
            "encrypted": self.encrypted,
        }

# ============================================================================
# ENVIRONMENT VARIABLE NAMES
# ============================================================================

ENV_NEO4J_URI = "NEO4J_URI"
ENV_NEO4J_USER = "NEO4J_USER"
ENV_NEO4J_PASSWORD = "NEO4J_PASSWORD"
ENV_NEO4J_DATABASE = "NEO4J_DATABASE"
ENV_NEO4J_ENCRYPTED = "NEO4J_ENCRYPTED"
ENV_NEO4J_MAX_POOL_SIZE = "NEO4J_MAX_POOL_SIZE"
ENV_NEO4J_CONNECTION_TIMEOUT = "NEO4J_CONNECTION_TIMEOUT"

# ============================================================================
# DEFAULT CONFIGURATIONS BY ENVIRONMENT
# ============================================================================

DEFAULT_DEV_CONFIG = Neo4jConfig(
    uri="bolt://localhost:7687",
    user="neo4j",
    password="password",  # Change in production!
    database="neo4j",
    encrypted=False,
    max_connection_pool_size=10,
    connection_timeout=10.0
)

DEFAULT_TEST_CONFIG = Neo4jConfig(
    uri="bolt://localhost:7688",  # Different port for test instance
    user="neo4j",
    password="testpassword",
    database="test",
    encrypted=False,
    max_connection_pool_size=5,
    connection_timeout=5.0
)

DEFAULT_PROD_CONFIG = Neo4jConfig(
    uri="neo4j+s://production.neo4j.io:7687",
    user="neo4j",
    password="",  # Must be set via environment variable
    database="neo4j",
    encrypted=True,
    trust="TRUST_SYSTEM_CA_SIGNED_CERTIFICATES",
    max_connection_pool_size=50,
    connection_timeout=30.0
)

# ============================================================================
# CONFIGURATION LOADER
# ============================================================================

def load_env_file(env_file: Optional[Path] = None) -> None:
    """
    Load environment variables from .env file.

    Args:
        env_file: Path to .env file (default: .env in project root)
    """
    if env_file is None:
        env_file = Path(__file__).parent.parent / ".env"

    if not env_file.exists():
        return

    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                key, value = line.split('=', 1)
                os.environ.setdefault(key.strip(), value.strip())

def get_neo4j_config(
    environment: str = "dev",
    load_env: bool = True
) -> Neo4jConfig:
    """
    Get Neo4j configuration based on environment.

    Args:
        environment: Environment name (dev, test, prod)
        load_env: Whether to load .env file

    Returns:
        Neo4jConfig instance with appropriate settings

    Raises:
        ValueError: If required environment variables are missing in production
    """
    if load_env:
        load_env_file()

    # Select base configuration
    if environment == "test":
        base_config = DEFAULT_TEST_CONFIG
    elif environment == "prod":
        base_config = DEFAULT_PROD_CONFIG
    else:
        base_config = DEFAULT_DEV_CONFIG

    # Override with environment variables
    config = Neo4jConfig(
        uri=os.getenv(ENV_NEO4J_URI, base_config.uri),
        user=os.getenv(ENV_NEO4J_USER, base_config.user),
        password=os.getenv(ENV_NEO4J_PASSWORD, base_config.password),
        database=os.getenv(ENV_NEO4J_DATABASE, base_config.database),
        encrypted=os.getenv(ENV_NEO4J_ENCRYPTED, str(base_config.encrypted)).lower() == "true",
        max_connection_pool_size=int(os.getenv(ENV_NEO4J_MAX_POOL_SIZE, str(base_config.max_connection_pool_size))),
        connection_timeout=float(os.getenv(ENV_NEO4J_CONNECTION_TIMEOUT, str(base_config.connection_timeout))),
        trust=base_config.trust
    )

    # Validate production configuration
    if environment == "prod":
        if not config.password:
            raise ValueError(
                f"Production environment requires {ENV_NEO4J_PASSWORD} "
                "environment variable to be set"
            )
        if "localhost" in config.uri or "127.0.0.1" in config.uri:
            raise ValueError(
                "Production environment should not use localhost URI"
            )

    return config

# ============================================================================
# CONFIGURATION VALIDATION
# ============================================================================

def validate_config(config: Neo4jConfig) -> tuple[bool, Optional[str]]:
    """
    Validate Neo4j configuration.

    Args:
        config: Neo4jConfig to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check URI format
    valid_schemes = ["bolt://", "neo4j://", "bolt+s://", "neo4j+s://"]
    if not any(config.uri.startswith(scheme) for scheme in valid_schemes):
        return False, f"Invalid URI scheme. Must be one of: {valid_schemes}"

    # Check credentials
    if not config.user or not config.password:
        return False, "Username and password are required"

    # Check pool size
    if config.max_connection_pool_size < 1:
        return False, "Max connection pool size must be at least 1"

    # Check timeout
    if config.connection_timeout <= 0:
        return False, "Connection timeout must be positive"

    return True, None

# ============================================================================
# EXAMPLE .env FILE TEMPLATE
# ============================================================================

ENV_TEMPLATE = """
# Neo4j Configuration
# Copy this to .env and update with your actual values

# Connection URI (bolt://, neo4j://, bolt+s://, neo4j+s://)
NEO4J_URI=bolt://localhost:7687

# Authentication
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_secure_password_here

# Database name (default: neo4j)
NEO4J_DATABASE=neo4j

# Connection settings
NEO4J_ENCRYPTED=false
NEO4J_MAX_POOL_SIZE=50
NEO4J_CONNECTION_TIMEOUT=30.0

# For production with Neo4j Aura:
# NEO4J_URI=neo4j+s://xxxxx.databases.neo4j.io
# NEO4J_ENCRYPTED=true
# NEO4J_USER=neo4j
# NEO4J_PASSWORD=your_aura_password
"""

def create_env_template(output_path: Optional[Path] = None) -> None:
    """
    Create .env.template file with configuration examples.

    Args:
        output_path: Path for template file (default: .env.template in project root)
    """
    if output_path is None:
        output_path = Path(__file__).parent.parent / ".env.template"

    with open(output_path, 'w') as f:
        f.write(ENV_TEMPLATE)

    print(f"Created environment template at: {output_path}")

# ============================================================================
# TESTING HELPER
# ============================================================================

if __name__ == "__main__":
    # Create .env template
    create_env_template()

    # Test configuration loading
    for env in ["dev", "test", "prod"]:
        try:
            print(f"\n{env.upper()} Configuration:")
            config = get_neo4j_config(environment=env)
            is_valid, error = validate_config(config)
            if is_valid:
                print(f"  ✓ Valid configuration")
                print(f"  URI: {config.uri}")
                print(f"  Database: {config.database}")
                print(f"  Encrypted: {config.encrypted}")
            else:
                print(f"  ✗ Invalid: {error}")
        except ValueError as e:
            print(f"  ✗ Error: {e}")
