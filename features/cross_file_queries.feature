Feature: Cross-File Queries
  As a user of the Brazilian Soccer MCP
  I want to query data across multiple CSV files
  So that I can correlate match data with player data

  Background:
    Given all datasets are loaded

  Scenario: Query team across multiple competitions
    When I search for "Flamengo" matches across all competitions
    Then I should find matches from Brasileirao
    And I should find matches from Copa do Brasil
    And I should find matches from Libertadores

  Scenario: Correlate player club with team matches
    Given a player "Neymar Jr" plays for a club
    When I search for that club's matches
    Then I should find matches involving the player's club

  Scenario: Query players at Brazilian clubs
    When I search for Brazilian players at Brazilian clubs
    Then I should find players with Brazilian nationality
    And their clubs should be Brazilian teams

  Scenario: Aggregate statistics across competitions
    When I calculate total goals for "Palmeiras" across all competitions
    Then the total should include Brasileirao goals
    And the total should include cup competition goals
