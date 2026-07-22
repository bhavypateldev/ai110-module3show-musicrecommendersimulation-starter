"""
Music Recommender Simulation — Core Logic.

Implements a content-based recommender that scores songs against
a user taste profile using weighted feature matching.
Supports advanced features, multiple scoring strategies, and diversity logic.
"""

import csv
import logging
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class Song:
    """Represents a song and its audio/mood attributes."""
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float
    # New features for Challenge 1 (with defaults so tests don't break)
    popularity: int = 50
    release_decade: int = 2020
    instrumentalness: float = 0.0
    speechiness: float = 0.0
    liveness: float = 0.0


@dataclass
class UserProfile:
    """Represents a user's taste preferences."""
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool
    # New features for Challenge 1 (with defaults so tests don't break)
    target_popularity: int = 50
    target_decade: int = 2020
    prefers_instrumental: bool = False
    max_speechiness: float = 1.0
    prefers_live: bool = False


# ---------------------------------------------------------------------------
# Scoring Strategy Pattern (Challenge 2)
# ---------------------------------------------------------------------------

class ScoringStrategy(ABC):
    """Base class for all scoring strategies."""
    
    @abstractmethod
    def score_song(self, user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
        """Score a single song against user preferences."""
        pass


class BalancedScorer(ScoringStrategy):
    """The standard scoring strategy with balanced weights."""
    
    def __init__(self):
        self.weights = {
            "genre": 3.0,
            "mood": 2.0,
            "energy": 1.5,
            "valence": 1.0,
            "acousticness": 0.5,
            "popularity": 0.5,
            "release_decade": 1.0,
            "instrumentalness": 0.5,
            "speechiness": 0.3,
            "liveness": 0.2,
        }

    def score_song(self, user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
        score = 0.0
        reasons: List[str] = []

        # --- Genre match ---
        if song["genre"] == user_prefs.get("genre", "").lower():
            pts = self.weights["genre"]
            score += pts
            reasons.append(f"genre match (+{pts:.1f})")

        # --- Mood match ---
        if song["mood"] == user_prefs.get("mood", "").lower():
            pts = self.weights["mood"]
            score += pts
            reasons.append(f"mood match (+{pts:.1f})")

        # --- Energy proximity ---
        target_energy = float(user_prefs.get("energy", 0.5))
        energy_proximity = 1.0 - abs(target_energy - song["energy"])
        pts = self.weights["energy"] * energy_proximity
        score += pts
        reasons.append(f"energy prox {energy_proximity:.2f} (+{pts:.1f})")

        # --- Valence proximity ---
        target_valence = float(user_prefs.get("valence", 0.7))
        valence_proximity = 1.0 - abs(target_valence - song["valence"])
        pts = self.weights["valence"] * valence_proximity
        score += pts
        reasons.append(f"valence prox {valence_proximity:.2f} (+{pts:.1f})")

        # --- Acousticness ---
        likes_acoustic = user_prefs.get("likes_acoustic", False)
        acoustic_score = song["acousticness"] if likes_acoustic else 1.0 - song["acousticness"]
        pts = self.weights["acousticness"] * acoustic_score
        score += pts
        reasons.append(f"acousticness fit {acoustic_score:.2f} (+{pts:.1f})")
        
        # --- Popularity proximity (Challenge 1) ---
        target_popularity = float(user_prefs.get("popularity", 50))
        # Normalize popularity 0-100 to 0-1 range
        pop_proximity = 1.0 - abs((target_popularity / 100.0) - (song.get("popularity", 50) / 100.0))
        pts = self.weights["popularity"] * pop_proximity
        score += pts
        reasons.append(f"popularity prox {pop_proximity:.2f} (+{pts:.1f})")
        
        # --- Release Decade match (Challenge 1) ---
        if song.get("release_decade") == user_prefs.get("release_decade"):
            pts = self.weights["release_decade"]
            score += pts
            reasons.append(f"decade match (+{pts:.1f})")

        # --- Instrumentalness (Challenge 1) ---
        prefers_instrumental = user_prefs.get("prefers_instrumental", False)
        inst_value = song.get("instrumentalness", 0.0)
        inst_score = inst_value if prefers_instrumental else 1.0 - inst_value
        pts = self.weights["instrumentalness"] * inst_score
        score += pts
        reasons.append(f"instrumental fit {inst_score:.2f} (+{pts:.1f})")

        # --- Speechiness penalty (Challenge 1) ---
        max_speech = float(user_prefs.get("max_speechiness", 1.0))
        speech_value = song.get("speechiness", 0.0)
        # Songs within the user's tolerance score higher
        speech_score = 1.0 - max(0.0, speech_value - max_speech)
        pts = self.weights["speechiness"] * speech_score
        score += pts
        reasons.append(f"speechiness fit {speech_score:.2f} (+{pts:.1f})")

        # --- Liveness (Challenge 1) ---
        prefers_live = user_prefs.get("prefers_live", False)
        live_value = song.get("liveness", 0.0)
        live_score = live_value if prefers_live else 1.0 - live_value
        pts = self.weights["liveness"] * live_score
        score += pts
        reasons.append(f"liveness fit {live_score:.2f} (+{pts:.1f})")

        return (score, reasons)


class GenreFirstScorer(BalancedScorer):
    """A strategy that prioritizes genre over everything else."""
    def __init__(self):
        super().__init__()
        self.weights["genre"] = 6.0
        self.weights["mood"] = 1.0


class EnergyFocusedScorer(BalancedScorer):
    """A strategy that prioritizes the energy level above all."""
    def __init__(self):
        super().__init__()
        self.weights["energy"] = 5.0
        self.weights["genre"] = 1.5


# We keep a functional wrapper to not break existing code dependencies
def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Legacy wrapper for the scoring logic (defaults to BalancedScorer)."""
    scorer = BalancedScorer()
    return scorer.score_song(user_prefs, song)


# ---------------------------------------------------------------------------
# Functional API (used by src/main.py)
# ---------------------------------------------------------------------------

def load_songs(csv_path: str) -> List[Dict]:
    """Load songs from a CSV file and return a list of dictionaries with proper types.
    
    Handles missing columns gracefully by falling back to defaults, and skips
    rows that contain malformed data rather than crashing the entire load.
    """
    songs = []
    try:
        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row_num, row in enumerate(reader, start=2):
                try:
                    song = {
                        "id": int(row["id"]),
                        "title": row["title"],
                        "artist": row["artist"],
                        "genre": row["genre"].strip().lower(),
                        "mood": row["mood"].strip().lower(),
                        "energy": float(row["energy"]),
                        "tempo_bpm": int(row["tempo_bpm"]),
                        "valence": float(row["valence"]),
                        "danceability": float(row["danceability"]),
                        "acousticness": float(row["acousticness"]),
                        "popularity": int(row.get("popularity", 50)),
                        "release_decade": int(row.get("release_decade", 2020)),
                        "instrumentalness": float(row.get("instrumentalness", 0.0)),
                        "speechiness": float(row.get("speechiness", 0.0)),
                        "liveness": float(row.get("liveness", 0.0)),
                    }
                    songs.append(song)
                except (ValueError, TypeError, KeyError) as e:
                    logger.warning(f"Skipping row {row_num}: {e}")
                    continue
    except FileNotFoundError:
        logger.error(f"Song catalog not found at '{csv_path}'")
        return []

    return songs


def recommend_songs(
    user_prefs: Dict, songs: List[Dict], k: int = 5, strategy: ScoringStrategy = None
) -> List[Tuple[Dict, float, str]]:
    """
    Rank all songs by score and return the top k as (song, score, explanation) tuples.
    Includes Diversity and Fairness Logic (Challenge 3).

    Handles edge cases:
      - Empty song list returns []
      - k larger than catalog size returns all songs ranked
      - k <= 0 returns []
    """
    if not songs or k <= 0:
        return []

    # Clamp k to the size of the catalog
    k = min(k, len(songs))

    if strategy is None:
        strategy = BalancedScorer()
        
    # First, get the raw scores for all songs
    scored = []
    for song in songs:
        total_score, reasons = strategy.score_song(user_prefs, song)
        scored.append({"song": song, "score": total_score, "reasons": reasons})

    # Sort initially by score
    scored.sort(key=lambda item: item["score"], reverse=True)
    
    # Challenge 3: Diversity Logic (Greedy Selection with Penalty)
    final_recommendations = []
    seen_artists = set()
    seen_genres = set()
    
    while len(final_recommendations) < k and scored:
        # Sort current remaining items to pop the best one
        scored.sort(key=lambda item: item["score"], reverse=True)
        best = scored.pop(0)
        
        # Format the explanation
        explanation = "; ".join(best["reasons"])
        final_recommendations.append((best["song"], best["score"], explanation))
        
        # Track artist and genre
        seen_artists.add(best["song"]["artist"])
        seen_genres.add(best["song"]["genre"])
        
        # Apply diversity penalty to remaining songs
        for item in scored:
            penalty_pts = 0.0
            penalty_reasons = []
            
            if item["song"]["artist"] in seen_artists:
                penalty_pts += 1.5
                penalty_reasons.append("artist diversity penalty (-1.5)")
                
            if item["song"]["genre"] in seen_genres:
                penalty_pts += 1.0
                penalty_reasons.append("genre diversity penalty (-1.0)")
                
            if penalty_pts > 0:
                item["score"] -= penalty_pts
                item["reasons"].extend(penalty_reasons)

    return final_recommendations


# ---------------------------------------------------------------------------
# OOP API (used by tests/test_recommender.py)
# ---------------------------------------------------------------------------

class Recommender:
    """OOP wrapper around the recommendation logic for the test suite."""

    def __init__(self, songs: List[Song]):
        self.songs = songs

    def _profile_to_prefs(self, user: UserProfile) -> Dict:
        return {
            "genre": user.favorite_genre,
            "mood": user.favorite_mood,
            "energy": user.target_energy,
            "valence": 0.7,  # default target
            "likes_acoustic": user.likes_acoustic,
            "popularity": getattr(user, "target_popularity", 50),
            "release_decade": getattr(user, "target_decade", 2020),
            "prefers_instrumental": getattr(user, "prefers_instrumental", False),
            "max_speechiness": getattr(user, "max_speechiness", 1.0),
            "prefers_live": getattr(user, "prefers_live", False),
        }

    def _song_to_dict(self, song: Song) -> Dict:
        return {
            "id": song.id,
            "title": song.title,
            "artist": song.artist,
            "genre": song.genre,
            "mood": song.mood,
            "energy": song.energy,
            "tempo_bpm": song.tempo_bpm,
            "valence": song.valence,
            "danceability": song.danceability,
            "acousticness": song.acousticness,
            "popularity": getattr(song, "popularity", 50),
            "release_decade": getattr(song, "release_decade", 2020),
            "instrumentalness": getattr(song, "instrumentalness", 0.0),
            "speechiness": getattr(song, "speechiness", 0.0),
            "liveness": getattr(song, "liveness", 0.0),
        }

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        prefs = self._profile_to_prefs(user)
        song_dicts = [self._song_to_dict(song) for song in self.songs]
        results = recommend_songs(prefs, song_dicts, k=k)
        
        # Map the dictionary back to the original Song objects
        id_to_song = {s.id: s for s in self.songs}
        return [id_to_song[res[0]["id"]] for res in results]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        prefs = self._profile_to_prefs(user)
        song_dict = self._song_to_dict(song)
        total_score, reasons = score_song(prefs, song_dict)
        return f"Score {total_score:.2f} — " + "; ".join(reasons)
