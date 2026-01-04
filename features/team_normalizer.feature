Feature: Team Name Normalization
  As a user of the Brazilian Soccer MCP
  I want team names to be normalized consistently
  So that I can query teams regardless of name variations

  Scenario Outline: Normalize team name with state suffix
    Given a team name "<input>"
    When I normalize the team name
    Then I should get "<expected>"

    Examples:
      | input           | expected    |
      | Palmeiras-SP    | Palmeiras   |
      | Flamengo-RJ     | Flamengo    |
      | Corinthians-SP  | Corinthians |
      | Gremio-RS       | Grêmio      |

  Scenario Outline: Normalize full official names
    Given a team name "<input>"
    When I normalize the team name
    Then I should get "<expected>"

    Examples:
      | input                              | expected     |
      | Clube de Regatas do Flamengo       | Flamengo     |
      | Sociedade Esportiva Palmeiras      | Palmeiras    |
      | Sport Club Corinthians Paulista    | Corinthians  |

  Scenario: Normalize case insensitive
    Given a team name "FLAMENGO"
    When I normalize the team name
    Then I should get "Flamengo"

  Scenario: Handle unknown team names
    Given a team name "Unknown FC"
    When I normalize the team name
    Then I should get "Unknown FC"
