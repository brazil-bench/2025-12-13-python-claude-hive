"""
Brazilian Soccer MCP Server - Data Layer Package

Purpose: Main package initialization for Brazilian soccer data analysis
Author: Claude Code - CODER Agent
Date: 2025-12-13
Dependencies: None (package initializer)
Key Functions: Package exports for external use

This package provides data loading, normalization, and model definitions
for analyzing Brazilian soccer match and player data from multiple datasets.
"""

from .models import Team, Player, Match, Competition
from .data_loader import DataLoader
from .team_normalizer import TeamNormalizer

__all__ = [
    'Team',
    'Player',
    'Match',
    'Competition',
    'DataLoader',
    'TeamNormalizer',
]

__version__ = '1.0.0'
