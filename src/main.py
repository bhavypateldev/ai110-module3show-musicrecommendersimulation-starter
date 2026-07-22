"""
Command-line runner for the Music Recommender Simulation.

Loads songs from the CSV catalog, applies the scoring algorithm
against multiple user profiles, and prints formatted recommendation lists.
"""

try:
    from src.recommender import load_songs, recommend_songs, BalancedScorer, GenreFirstScorer, EnergyFocusedScorer
except ImportError:
    from recommender import load_songs, recommend_songs, BalancedScorer, GenreFirstScorer, EnergyFocusedScorer


def print_table_divider():
    print("+" + "-"*4 + "+" + "-"*30 + "+" + "-"*20 + "+" + "-"*8 + "+" + "-"*60 + "+")

def print_recommendations(label: str, user_prefs: dict, songs: list, k: int = 5, strategy=None) -> None:
    """Run the recommender for one profile and print formatted results."""
    strategy_name = strategy.__class__.__name__ if strategy else "BalancedScorer"
    recommendations = recommend_songs(user_prefs, songs, k=k, strategy=strategy)

    print("\n" + "=" * 127)
    print(f"  PROFILE: {label} | STRATEGY: {strategy_name}")
    print("=" * 127)
    prefs_str = ", ".join(f"{key}={val}" for key, val in user_prefs.items())
    print(f"  Prefs: {prefs_str}")
    
    print_table_divider()
    print(f"| {'#':<2} | {'Title':<28} | {'Artist':<18} | {'Score':<6} | {'Why (Reasons & Penalties)':<58} |")
    print_table_divider()

    for rank, (song, score, explanation) in enumerate(recommendations, 1):
        title = song['title']
        if len(title) > 28:
            title = title[:25] + "..."
        artist = song['artist']
        if len(artist) > 18:
            artist = artist[:15] + "..."
            
        # Hardwrap explanations for the table cell
        words = explanation.split("; ")
        lines = []
        current_line = ""
        for word in words:
            if len(current_line) + len(word) + 2 <= 58:
                current_line += (word + "; ")
            else:
                lines.append(current_line)
                current_line = word + "; "
        if current_line:
            lines.append(current_line)
            
        print(f"| {rank:<2} | {title:<28} | {artist:<18} | {score:>5.2f}  | {lines[0]:<58} |")
        for line in lines[1:]:
            print(f"| {'':<2} | {'':<28} | {'':<18} | {'':<6} | {line:<58} |")
            
        print_table_divider()

    print("\n")


def main() -> None:
    """Run the recommender across multiple user profiles for evaluation."""
    songs = load_songs("data/songs.csv")

    profiles = {
        "High-Energy Pop Fan": {
            "genre": "pop",
            "mood": "happy",
            "energy": 0.8,
            "valence": 0.7,
            "likes_acoustic": False,
            "popularity": 90,
            "release_decade": 2020
        },
        "Chill Lofi Listener": {
            "genre": "lofi",
            "mood": "chill",
            "energy": 0.35,
            "valence": 0.6,
            "likes_acoustic": True,
            "popularity": 50,
            "release_decade": 2020
        },
        "Deep Intense Rock": {
            "genre": "rock",
            "mood": "intense",
            "energy": 0.9,
            "valence": 0.4,
            "likes_acoustic": False,
            "popularity": 70,
            "release_decade": 1990
        }
    }

    # Challenge 2: Test multiple scoring strategies
    strategies = [BalancedScorer(), GenreFirstScorer(), EnergyFocusedScorer()]

    # Demonstrate normal profile with BalancedScorer
    print_recommendations("High-Energy Pop Fan", profiles["High-Energy Pop Fan"], songs, strategy=BalancedScorer())
    
    # Demonstrate the SAME profile but with EnergyFocusedScorer to show how Strategy Pattern changes results
    print_recommendations("High-Energy Pop Fan", profiles["High-Energy Pop Fan"], songs, strategy=EnergyFocusedScorer())

    # Demonstrate Chill Lofi
    print_recommendations("Chill Lofi Listener", profiles["Chill Lofi Listener"], songs, strategy=BalancedScorer())

if __name__ == "__main__":
    main()
