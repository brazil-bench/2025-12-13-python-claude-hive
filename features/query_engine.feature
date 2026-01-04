Feature: Query Engine
  As a user of the Brazilian Soccer MCP
  I want to query match and team data
  So that I can get statistics about Brazilian soccer

  Background:
    Given the match data is loaded

  Scenario: Find matches between two teams
    When I search for matches between "Flamengo" and "Palmeiras"
    Then I should receive a list of matches
    And each match should involve both teams

  Scenario: Find matches by team
    When I search for all matches involving "Corinthians"
    Then I should receive matches where Corinthians played
    And matches should include home and away games

  Scenario: Find matches by season
    When I search for matches in season 2023
    Then all returned matches should be from season 2023

  Scenario: Get team statistics
    When I request statistics for "Flamengo"
    Then I should receive wins, losses, draws counts
    And I should receive goals scored and conceded

  Scenario: Get head to head statistics
    When I request head-to-head for "Flamengo" vs "Fluminense"
    Then I should receive win counts for each team
    And I should receive draw count

  Scenario: Find players by nationality
    When I search for players with nationality "Brazil"
    Then I should receive a list of Brazilian players

  Scenario: Get top rated players
    When I request top 10 rated players
    Then I should receive up to 10 players
    And they should be sorted by overall rating descending

  Scenario: Handle non-existent team
    When I search for matches by team "NonExistentTeam"
    Then I should receive an empty list
