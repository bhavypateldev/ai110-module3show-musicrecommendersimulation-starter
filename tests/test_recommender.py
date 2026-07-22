from src.recommender import (
    Song, UserProfile, Recommender,
    BalancedScorer, GenreFirstScorer, EnergyFocusedScorer,
    score_song, recommend_songs, load_songs,
)
import os
import tempfile


# ---------------------------------------------------------------------------
# Fixtures — reusable test data
# ---------------------------------------------------------------------------

def _make_songs():
    """Build a small catalog with enough variety to test scoring and diversity."""
    return [
        Song(id=1, title="Test Pop Track", artist="Artist A",
             genre="pop", mood="happy", energy=0.8, tempo_bpm=120,
             valence=0.9, danceability=0.8, acousticness=0.2,
             instrumentalness=0.02, speechiness=0.05, liveness=0.10),
        Song(id=2, title="Chill Lofi Loop", artist="Artist A",
             genre="lofi", mood="chill", energy=0.4, tempo_bpm=80,
             valence=0.6, danceability=0.5, acousticness=0.9,
             instrumentalness=0.85, speechiness=0.03, liveness=0.06),
        Song(id=3, title="Hard Rock Anthem", artist="Artist B",
             genre="rock", mood="intense", energy=0.92, tempo_bpm=150,
             valence=0.45, danceability=0.65, acousticness=0.08,
             instrumentalness=0.10, speechiness=0.06, liveness=0.30),
        Song(id=4, title="Another Pop Hit", artist="Artist C",
             genre="pop", mood="happy", energy=0.75, tempo_bpm=115,
             valence=0.85, danceability=0.78, acousticness=0.25,
             instrumentalness=0.03, speechiness=0.04, liveness=0.15),
        Song(id=5, title="Pop Banger", artist="Artist A",
             genre="pop", mood="intense", energy=0.95, tempo_bpm=135,
             valence=0.70, danceability=0.90, acousticness=0.05,
             instrumentalness=0.01, speechiness=0.08, liveness=0.20),
    ]


def make_small_recommender() -> Recommender:
    return Recommender(_make_songs())


def _pop_user():
    return UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )


# ---------------------------------------------------------------------------
# Original starter tests (kept as-is)
# ---------------------------------------------------------------------------

def test_recommend_returns_songs_sorted_by_score():
    user = _pop_user()
    rec = make_small_recommender()
    results = rec.recommend(user, k=2)

    assert len(results) == 2
    # The pop, happy, high energy song should score highest
    assert results[0].genre == "pop"
    assert results[0].mood == "happy"


def test_explain_recommendation_returns_non_empty_string():
    user = _pop_user()
    rec = make_small_recommender()
    song = rec.songs[0]

    explanation = rec.explain_recommendation(user, song)
    assert isinstance(explanation, str)
    assert explanation.strip() != ""


# ---------------------------------------------------------------------------
# Scoring strategy tests
# ---------------------------------------------------------------------------

def test_genre_first_scorer_ranks_genre_match_higher():
    """GenreFirstScorer should give even more weight to genre than BalancedScorer."""
    user_prefs = {"genre": "pop", "mood": "intense", "energy": 0.9,
                  "valence": 0.5, "likes_acoustic": False}
    # Rock song that matches mood and energy perfectly
    rock_song = {"id": 1, "title": "Rock", "artist": "X", "genre": "rock",
                 "mood": "intense", "energy": 0.91, "valence": 0.48,
                 "acousticness": 0.1, "popularity": 50, "release_decade": 2020,
                 "instrumentalness": 0.1, "speechiness": 0.05, "liveness": 0.2}
    # Pop song that matches genre but not mood/energy as well
    pop_song = {"id": 2, "title": "Pop", "artist": "Y", "genre": "pop",
                "mood": "happy", "energy": 0.6, "valence": 0.8,
                "acousticness": 0.3, "popularity": 50, "release_decade": 2020,
                "instrumentalness": 0.02, "speechiness": 0.04, "liveness": 0.1}

    gf = GenreFirstScorer()
    rock_score, _ = gf.score_song(user_prefs, rock_song)
    pop_score, _ = gf.score_song(user_prefs, pop_song)

    # With genre weight 6.0, pop song should beat rock despite weaker features
    assert pop_score > rock_score, "GenreFirstScorer should favour genre matches"


def test_energy_focused_scorer_ranks_energy_match_higher():
    """EnergyFocusedScorer should favour songs closest in energy."""
    user_prefs = {"genre": "jazz", "mood": "relaxed", "energy": 0.9,
                  "valence": 0.5, "likes_acoustic": False}
    # Low-energy jazz that matches genre + mood but terrible energy fit
    jazz_song = {"id": 1, "title": "Jazz", "artist": "X", "genre": "jazz",
                 "mood": "relaxed", "energy": 0.2, "valence": 0.5,
                 "acousticness": 0.9, "popularity": 50, "release_decade": 2020,
                 "instrumentalness": 0.3, "speechiness": 0.04, "liveness": 0.5}
    # High-energy rock that nails the energy target
    rock_song = {"id": 2, "title": "Rock", "artist": "Y", "genre": "rock",
                 "mood": "intense", "energy": 0.91, "valence": 0.5,
                 "acousticness": 0.1, "popularity": 50, "release_decade": 2020,
                 "instrumentalness": 0.1, "speechiness": 0.05, "liveness": 0.3}

    ef = EnergyFocusedScorer()
    jazz_score, _ = ef.score_song(user_prefs, jazz_song)
    rock_score, _ = ef.score_song(user_prefs, rock_song)

    # With energy weight 5.0, rock's energy proximity (0.99) should overcome
    # jazz's genre+mood bonus because jazz's energy proximity is only 0.30
    assert rock_score > jazz_score, "EnergyFocusedScorer should favour energy matches"


def test_different_strategies_produce_different_rankings():
    """Same input, different strategy -> different top-1 pick."""
    songs = [
        {"id": 1, "title": "Genre Match", "artist": "A", "genre": "pop",
         "mood": "chill", "energy": 0.2, "valence": 0.5, "acousticness": 0.5,
         "popularity": 50, "release_decade": 2020,
         "instrumentalness": 0.0, "speechiness": 0.0, "liveness": 0.0},
        {"id": 2, "title": "Energy Match", "artist": "B", "genre": "rock",
         "mood": "intense", "energy": 0.89, "valence": 0.5, "acousticness": 0.1,
         "popularity": 50, "release_decade": 2020,
         "instrumentalness": 0.0, "speechiness": 0.0, "liveness": 0.0},
    ]
    prefs = {"genre": "pop", "mood": "chill", "energy": 0.9,
             "valence": 0.5, "likes_acoustic": False}

    balanced = recommend_songs(prefs, songs, k=2, strategy=BalancedScorer())
    energy = recommend_songs(prefs, songs, k=2, strategy=EnergyFocusedScorer())

    # BalancedScorer: genre+mood bonus (3+2=5) should dominate for "Genre Match"
    assert balanced[0][0]["title"] == "Genre Match"
    # EnergyFocusedScorer: energy weight 5.0 makes energy proximity decisive
    assert energy[0][0]["title"] == "Energy Match"


# ---------------------------------------------------------------------------
# Diversity penalty tests
# ---------------------------------------------------------------------------

def test_diversity_penalty_demotes_repeated_artist():
    """If two songs share an artist, the second one should be penalized."""
    songs = [
        {"id": 1, "title": "Hit A1", "artist": "SameArtist", "genre": "pop",
         "mood": "happy", "energy": 0.8, "valence": 0.8, "acousticness": 0.2,
         "popularity": 80, "release_decade": 2020,
         "instrumentalness": 0.0, "speechiness": 0.0, "liveness": 0.0},
        {"id": 2, "title": "Hit A2", "artist": "SameArtist", "genre": "pop",
         "mood": "happy", "energy": 0.79, "valence": 0.79, "acousticness": 0.21,
         "popularity": 79, "release_decade": 2020,
         "instrumentalness": 0.0, "speechiness": 0.0, "liveness": 0.0},
        {"id": 3, "title": "Other Song", "artist": "DiffArtist", "genre": "rock",
         "mood": "intense", "energy": 0.5, "valence": 0.5, "acousticness": 0.5,
         "popularity": 50, "release_decade": 2020,
         "instrumentalness": 0.0, "speechiness": 0.0, "liveness": 0.0},
    ]
    prefs = {"genre": "pop", "mood": "happy", "energy": 0.8,
             "valence": 0.8, "likes_acoustic": False}

    results = recommend_songs(prefs, songs, k=3)
    # First result should be Hit A1 (highest raw score)
    assert results[0][0]["title"] == "Hit A1"
    # Second result should NOT be Hit A2 because diversity penalty
    # demotes it for sharing artist + genre with Hit A1
    assert results[1][0]["title"] != "Hit A1"


def test_diversity_penalty_appears_in_explanation():
    """The explanation string should mention the diversity penalty when applied."""
    songs = [
        {"id": 1, "title": "Song1", "artist": "Same", "genre": "pop",
         "mood": "happy", "energy": 0.8, "valence": 0.8, "acousticness": 0.2,
         "popularity": 80, "release_decade": 2020,
         "instrumentalness": 0.0, "speechiness": 0.0, "liveness": 0.0},
        {"id": 2, "title": "Song2", "artist": "Same", "genre": "pop",
         "mood": "happy", "energy": 0.78, "valence": 0.78, "acousticness": 0.22,
         "popularity": 78, "release_decade": 2020,
         "instrumentalness": 0.0, "speechiness": 0.0, "liveness": 0.0},
    ]
    prefs = {"genre": "pop", "mood": "happy", "energy": 0.8,
             "valence": 0.8, "likes_acoustic": False}

    results = recommend_songs(prefs, songs, k=2)
    second_explanation = results[1][2]
    assert "diversity penalty" in second_explanation


# ---------------------------------------------------------------------------
# Edge case and defensive coding tests
# ---------------------------------------------------------------------------

def test_recommend_songs_with_empty_list():
    """Should return [] when given no songs."""
    results = recommend_songs({"genre": "pop"}, [], k=5)
    assert results == []


def test_recommend_songs_k_larger_than_catalog():
    """When k exceeds catalog size, return all songs without crashing."""
    songs = [
        {"id": 1, "title": "Only Song", "artist": "A", "genre": "pop",
         "mood": "happy", "energy": 0.5, "valence": 0.5, "acousticness": 0.5,
         "popularity": 50, "release_decade": 2020,
         "instrumentalness": 0.0, "speechiness": 0.0, "liveness": 0.0},
    ]
    results = recommend_songs({"genre": "pop"}, songs, k=100)
    assert len(results) == 1


def test_recommend_songs_k_zero_returns_empty():
    """k=0 should return no recommendations."""
    songs = [
        {"id": 1, "title": "S", "artist": "A", "genre": "pop",
         "mood": "happy", "energy": 0.5, "valence": 0.5, "acousticness": 0.5,
         "popularity": 50, "release_decade": 2020,
         "instrumentalness": 0.0, "speechiness": 0.0, "liveness": 0.0},
    ]
    results = recommend_songs({"genre": "pop"}, songs, k=0)
    assert results == []


def test_load_songs_missing_file_returns_empty():
    """load_songs should return [] for a nonexistent path, not crash."""
    result = load_songs("nonexistent/path/songs.csv")
    assert result == []


def test_load_songs_skips_malformed_rows(tmp_path):
    """Rows with bad data should be skipped, not crash the load."""
    csv_content = (
        "id,title,artist,genre,mood,energy,tempo_bpm,valence,danceability,acousticness,popularity,release_decade,instrumentalness,speechiness,liveness\n"
        "1,Good Song,Artist,pop,happy,0.8,120,0.9,0.8,0.2,80,2020,0.02,0.05,0.10\n"
        "BAD,Bad Row,Artist,pop,happy,NOT_A_NUMBER,120,0.9,0.8,0.2,80,2020,0.02,0.05,0.10\n"
        "3,Another Good,Artist,rock,intense,0.9,140,0.5,0.7,0.1,70,2000,0.10,0.06,0.30\n"
    )
    csv_file = tmp_path / "test_songs.csv"
    csv_file.write_text(csv_content, encoding="utf-8")

    songs = load_songs(str(csv_file))
    # Should load 2 good rows, skip the bad one
    assert len(songs) == 2
    assert songs[0]["title"] == "Good Song"
    assert songs[1]["title"] == "Another Good"


# ---------------------------------------------------------------------------
# New attribute tests
# ---------------------------------------------------------------------------

def test_instrumentalness_affects_scoring():
    """Users who prefer instrumental tracks should score instrumental songs higher."""
    song = {"id": 1, "title": "S", "artist": "A", "genre": "lofi", "mood": "chill",
            "energy": 0.4, "valence": 0.5, "acousticness": 0.8,
            "popularity": 50, "release_decade": 2020,
            "instrumentalness": 0.9, "speechiness": 0.02, "liveness": 0.05}

    prefs_instrumental = {"genre": "lofi", "mood": "chill", "energy": 0.4,
                          "valence": 0.5, "likes_acoustic": True,
                          "prefers_instrumental": True}
    prefs_vocal = {"genre": "lofi", "mood": "chill", "energy": 0.4,
                   "valence": 0.5, "likes_acoustic": True,
                   "prefers_instrumental": False}

    scorer = BalancedScorer()
    score_inst, _ = scorer.score_song(prefs_instrumental, song)
    score_vocal, _ = scorer.score_song(prefs_vocal, song)

    assert score_inst > score_vocal, "Instrumental preference should boost score for instrumental tracks"


def test_speechiness_penalty_works():
    """A song exceeding the user's speechiness tolerance should score lower."""
    base_song = {"id": 1, "title": "S", "artist": "A", "genre": "pop", "mood": "happy",
                 "energy": 0.8, "valence": 0.8, "acousticness": 0.2,
                 "popularity": 80, "release_decade": 2020,
                 "instrumentalness": 0.02, "liveness": 0.1}

    low_speech = {**base_song, "speechiness": 0.05}
    high_speech = {**base_song, "speechiness": 0.60}

    prefs = {"genre": "pop", "mood": "happy", "energy": 0.8,
             "valence": 0.8, "likes_acoustic": False,
             "max_speechiness": 0.10}

    scorer = BalancedScorer()
    score_low, _ = scorer.score_song(prefs, low_speech)
    score_high, _ = scorer.score_song(prefs, high_speech)

    assert score_low > score_high, "High speechiness should be penalized when user has low tolerance"


def test_liveness_preference_affects_scoring():
    """Users who prefer live recordings should score live tracks higher."""
    song = {"id": 1, "title": "S", "artist": "A", "genre": "jazz", "mood": "relaxed",
            "energy": 0.4, "valence": 0.7, "acousticness": 0.9,
            "popularity": 50, "release_decade": 1960,
            "instrumentalness": 0.3, "speechiness": 0.04, "liveness": 0.65}

    prefs_live = {"genre": "jazz", "mood": "relaxed", "energy": 0.4,
                  "valence": 0.7, "likes_acoustic": True, "prefers_live": True}
    prefs_studio = {"genre": "jazz", "mood": "relaxed", "energy": 0.4,
                    "valence": 0.7, "likes_acoustic": True, "prefers_live": False}

    scorer = BalancedScorer()
    score_live, _ = scorer.score_song(prefs_live, song)
    score_studio, _ = scorer.score_song(prefs_studio, song)

    assert score_live > score_studio, "Live preference should boost score for live-recorded tracks"
