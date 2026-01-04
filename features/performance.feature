Feature: Query Performance
  As a user of the Brazilian Soccer MCP
  I want queries to execute quickly
  So that I can get results without timeout errors

  Background:
    Given all datasets are loaded

  Scenario: Simple player lookup responds quickly
    When I search for player "Neymar"
    Then the query should complete in less than 2 seconds

  Scenario: Team statistics calculation responds quickly
    When I calculate statistics for "Flamengo"
    Then the query should complete in less than 2 seconds

  Scenario: Match search responds quickly
    When I search for matches between "Flamengo" and "Palmeiras"
    Then the query should complete in less than 2 seconds

  Scenario: Aggregate query responds within limit
    When I calculate league standings for season 2023
    Then the query should complete in less than 5 seconds

  Scenario: Head to head query responds quickly
    When I calculate head-to-head for "Santos" vs "Corinthians"
    Then the query should complete in less than 2 seconds
