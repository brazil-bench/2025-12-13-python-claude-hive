Feature: Data Loading
  As a user of the Brazilian Soccer MCP
  I want to load match and player data from CSV files
  So that I can query Brazilian soccer information

  Background:
    Given the data directory exists with CSV files

  Scenario: Load Brasileirao matches
    When I load Brasileirao matches
    Then I should receive a list of matches
    And each match should have home_team, away_team, and scores

  Scenario: Load FIFA players
    When I load FIFA players
    Then I should receive a list of players
    And each player should have name, nationality, and overall rating

  Scenario: Load all datasets
    When I load all datasets
    Then I should have matches from multiple competitions
    And I should have player data

  Scenario: Parse multiple date formats
    Given a date string "2023-05-15 19:30:00"
    When I parse the date
    Then I should get a valid datetime object

  Scenario: Handle UTF-8 team names
    When I load matches with Portuguese characters
    Then team names like "São Paulo" should be preserved correctly
