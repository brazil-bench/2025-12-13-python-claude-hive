"""
Brazilian Soccer MCP Server - Basic Usage Examples

Purpose: Demonstrate how to use the data layer components
Author: Claude Code - CODER Agent
Date: 2025-12-13
Dependencies: src.models, src.data_loader, src.team_normalizer
Key Functions: Example usage patterns for the data layer

This file shows practical examples of:
- Loading CSV data
- Normalizing team names
- Working with matches and players
- Filtering and analyzing data
"""

from pathlib import Path
from src import DataLoader, TeamNormalizer, Match, Player


def example_load_all_data():
    """Example: Load all datasets"""
    print("=" * 60)
    print("EXAMPLE 1: Loading All Data")
    print("=" * 60)

    # Initialize loader with data directory
    loader = DataLoader(data_dir="data")

    # Load all datasets
    data = loader.load_all()

    # Print summary
    print(f"\n📊 Data Summary:")
    print(f"  Brasileirão matches: {len(data['brasileirao'])}")
    print(f"  Copa Brasil matches: {len(data['copa_brasil'])}")
    print(f"  Libertadores matches: {len(data['libertadores'])}")
    print(f"  Extended matches: {len(data['extended'])}")
    print(f"  Historical matches: {len(data['historical'])}")
    print(f"  Total matches: {len(data['all_matches'])}")
    print(f"  FIFA players: {len(data['players'])}")

    return data


def example_team_normalization():
    """Example: Team name normalization"""
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Team Name Normalization")
    print("=" * 60)

    normalizer = TeamNormalizer()

    test_names = [
        "Palmeiras-SP",
        "Sport Club Corinthians Paulista",
        "Grêmio FBPA",
        "São Paulo FC",
        "Flamengo-RJ",
        "Club de Regatas Vasco da Gama",
        "Atlético-MG",
    ]

    print("\n🔄 Team Name Normalization:")
    for name in test_names:
        normalized = normalizer.normalize(name)
        state = normalizer.extract_state(name)
        print(f"  {name:<40} → {normalized} ({state or 'N/A'})")


def example_filter_matches():
    """Example: Filter matches by criteria"""
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Filter Matches")
    print("=" * 60)

    loader = DataLoader(data_dir="data")
    data = loader.load_all()

    if not data['all_matches']:
        print("  ⚠️  No match data available")
        return

    # Filter: Palmeiras home matches
    palmeiras_home = [
        m for m in data['all_matches']
        if m.home_team == "Palmeiras"
    ]

    # Filter: High-scoring matches (4+ goals)
    high_scoring = [
        m for m in data['all_matches']
        if m.total_goals >= 4
    ]

    # Filter: Copa do Brasil matches
    copa_matches = [
        m for m in data['all_matches']
        if m.competition == "Copa do Brasil"
    ]

    print(f"\n🔍 Filter Results:")
    print(f"  Palmeiras home matches: {len(palmeiras_home)}")
    print(f"  High-scoring matches (4+ goals): {len(high_scoring)}")
    print(f"  Copa do Brasil matches: {len(copa_matches)}")

    # Show sample match
    if palmeiras_home:
        print(f"\n  Sample match: {palmeiras_home[0]}")


def example_player_analysis():
    """Example: Analyze player data"""
    print("\n" + "=" * 60)
    print("EXAMPLE 4: Player Analysis")
    print("=" * 60)

    loader = DataLoader(data_dir="data")
    players = loader.load_fifa_players()

    if not players:
        print("  ⚠️  No player data available")
        return

    # Filter Brazilian players
    brazilian_players = [p for p in players if p.nationality == "Brazil"]

    # Filter players by club (example: Palmeiras)
    palmeiras_players = [p for p in players if p.club == "Palmeiras"]

    # Top-rated players (if overall_rating available)
    rated_players = [p for p in players if p.overall_rating is not None]
    if rated_players:
        top_players = sorted(rated_players, key=lambda p: p.overall_rating, reverse=True)[:10]

        print(f"\n⭐ Top 10 Players by Rating:")
        for i, player in enumerate(top_players, 1):
            print(f"  {i:2d}. {player.name:<30} {player.overall_rating} ({player.club or 'N/A'})")

    print(f"\n📊 Player Statistics:")
    print(f"  Total players: {len(players)}")
    print(f"  Brazilian players: {len(brazilian_players)}")
    print(f"  Palmeiras players: {len(palmeiras_players)}")


def example_match_statistics():
    """Example: Calculate match statistics"""
    print("\n" + "=" * 60)
    print("EXAMPLE 5: Match Statistics")
    print("=" * 60)

    loader = DataLoader(data_dir="data")
    data = loader.load_all()

    if not data['all_matches']:
        print("  ⚠️  No match data available")
        return

    matches = data['all_matches']

    # Calculate basic stats
    total_goals = sum(m.total_goals for m in matches)
    avg_goals = total_goals / len(matches) if matches else 0

    # Result distribution
    wins_home = len([m for m in matches if m.result == "Win"])
    draws = len([m for m in matches if m.result == "Draw"])
    wins_away = len([m for m in matches if m.result == "Loss"])

    # Competition breakdown
    competitions = {}
    for match in matches:
        competitions[match.competition] = competitions.get(match.competition, 0) + 1

    print(f"\n📈 Match Statistics:")
    print(f"  Total matches: {len(matches)}")
    print(f"  Total goals: {total_goals}")
    print(f"  Average goals per match: {avg_goals:.2f}")
    print(f"\n  Results (from home team perspective):")
    print(f"    Home wins: {wins_home} ({wins_home/len(matches)*100:.1f}%)")
    print(f"    Draws: {draws} ({draws/len(matches)*100:.1f}%)")
    print(f"    Away wins: {wins_away} ({wins_away/len(matches)*100:.1f}%)")

    print(f"\n  Matches by competition:")
    for comp, count in sorted(competitions.items(), key=lambda x: x[1], reverse=True):
        print(f"    {comp}: {count}")


def example_date_parsing():
    """Example: Date parsing with multiple formats"""
    print("\n" + "=" * 60)
    print("EXAMPLE 6: Date Parsing")
    print("=" * 60)

    loader = DataLoader(data_dir="data")

    test_dates = [
        "2023-05-15 19:30:00",
        "2023-05-15",
        "15/05/2023 19:30",
        "15/05/2023",
        "15-05-2023",
        "2023/05/15",
    ]

    print("\n📅 Date Parsing Examples:")
    for date_str in test_dates:
        parsed = loader.parse_date(date_str)
        if parsed:
            print(f"  {date_str:<25} → {parsed.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            print(f"  {date_str:<25} → ❌ Failed to parse")


def main():
    """Run all examples"""
    print("\n" + "🇧🇷 " * 20)
    print("Brazilian Soccer MCP Server - Data Layer Examples")
    print("🇧🇷 " * 20)

    try:
        # Run examples
        example_load_all_data()
        example_team_normalization()
        example_filter_matches()
        example_player_analysis()
        example_match_statistics()
        example_date_parsing()

        print("\n" + "=" * 60)
        print("✅ All examples completed successfully!")
        print("=" * 60 + "\n")

    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
