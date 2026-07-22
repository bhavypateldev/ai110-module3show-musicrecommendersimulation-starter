# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

This project implements a content-based music recommender simulation. Given an expanded catalog of **18 songs** spanning 10 genres (pop, lofi, rock, ambient, jazz, synthwave, indie pop, hip-hop, electronic, classical, r&b, folk, metal, latin, country) and a user taste profile, it scores each song using a weighted proximity formula and returns the top-k closest matches with human-readable explanations. The system demonstrates how real-world platforms like Spotify turn raw audio features and user preferences into personalized "For You" playlists.

---

## How The System Works

Real-world music recommenders like Spotify and YouTube combine **collaborative filtering** (learning from millions of users with similar tastes) and **content-based filtering** (matching measurable song attributes to a user's preferences). They ingest both explicit signals (likes, saves) and implicit signals (skips, listen duration) to continuously refine a model of each user's taste. Our simulation focuses on the **content-based approach**: we define a user's ideal "vibe" as a set of preferred attributes, then mathematically score every song in the catalog by how closely it matches that vibe.

### Song Features

Each `Song` object stores the following attributes from `data/songs.csv`:

- **`genre`** — categorical (pop, lofi, rock, ambient, jazz, synthwave, indie pop, hip-hop, electronic, classical, r&b, folk, metal, latin, country)
- **`mood`** — categorical (happy, chill, intense, relaxed, moody, focused, energetic, melancholy, nostalgic, romantic, aggressive, upbeat)
- **`energy`** — float 0–1, how intense the track feels
- **`tempo_bpm`** — int, beats per minute
- **`valence`** — float 0–1, musical positiveness (high = happy)
- **`danceability`** — float 0–1, how suitable for dancing
- **`acousticness`** — float 0–1, confidence the track is acoustic
- **`popularity`** — int 0–100, simulated streaming popularity score
- **`release_decade`** — int, decade the track was released (e.g., 1990, 2020)
- **`instrumentalness`** — float 0–1, likelihood the track has no vocals
- **`speechiness`** — float 0–1, presence of spoken words (high = podcast-like)
- **`liveness`** — float 0–1, probability the track was recorded live

### UserProfile Data

Each `UserProfile` stores the user's taste preferences:

- **`favorite_genre`** — preferred genre (e.g., "pop")
- **`favorite_mood`** — preferred mood (e.g., "happy")
- **`target_energy`** — ideal energy level as a float (e.g., 0.8)
- **`likes_acoustic`** — boolean preference for acoustic tracks

**Profile Design Critique:** These four preferences are enough to differentiate broad taste clusters — for example, a user with `genre=rock, mood=intense, energy=0.9, acoustic=False` will get very different results than `genre=lofi, mood=chill, energy=0.3, acoustic=True`. However, the profile is too narrow to distinguish between sub-vibes within a cluster (e.g., "nostalgic folk" vs. "nostalgic country"). A future improvement would add `target_valence` and `target_danceability` to the profile.

### Algorithm Recipe (Finalized Scoring Logic)

**Scoring Rule** — evaluates one song at a time:

| Feature | Type | Formula | Weight | Rationale |
|---|---|---|---|---|
| `genre` | Categorical | `1.0` if exact match, else `0.0` | **3.0** | Primary filter — wrong genre rarely feels right |
| `mood` | Categorical | `1.0` if exact match, else `0.0` | **2.0** | Strong emotional signal, but more flexible than genre |
| `energy` | Numerical | `1.0 - abs(user_target - song_value)` | **1.5** | Key situational feature (gym vs. study) |
| `valence` | Numerical | `1.0 - abs(0.7 - song_value)` (default target) | **1.0** | Emotional nuance refinement |
| `acousticness` | Numerical | `song_value` if `likes_acoustic`, else `1.0 - song_value` | **0.5** | Separates "unplugged" from "produced" listeners |
| `popularity` | Numerical | `1.0 - abs(target/100 - song/100)` | **0.5** | Preference for mainstream vs. underground tracks |
| `release_decade` | Categorical | `1.0` if exact match, else `0.0` | **1.0** | Fans of a specific era get period-matched results |
| `instrumentalness` | Numerical | `song_value` if prefers, else `1.0 - song_value` | **0.5** | Separates vocal tracks from pure instrumental/lofi |
| `speechiness` | Numerical | `1.0 - max(0, speech - tolerance)` | **0.3** | Penalizes podcast-like tracks for music listeners |
| `liveness` | Numerical | `song_value` if prefers, else `1.0 - song_value` | **0.2** | Live recording preference for jazz/folk fans |

**Maximum possible score:** 3.0 + 2.0 + 1.5 + 1.0 + 0.5 + 0.5 + 1.0 + 0.5 + 0.3 + 0.2 = **10.5**

**Ranking Rule** — produces the final list:
1. Compute `score_song(user, song)` for every song in the catalog
2. Sort all songs by score in descending order
3. Return the top `k` songs (default k = 5) with explanations

### Data Flow

```
Input (User Prefs)          Process (The Loop)              Output (The Ranking)
┌─────────────────┐    ┌──────────────────────────┐    ┌─────────────────────┐
│ favorite_genre   │    │ FOR each song in CSV:    │    │ Sort scored songs   │
│ favorite_mood    │───▶│   score = weighted sum   │───▶│ by score descending │
│ target_energy    │    │   of feature matches     │    │ Return top k songs  │
│ likes_acoustic   │    │   + proximity scores     │    │ with explanations   │
└─────────────────┘    └──────────────────────────┘    └─────────────────────┘
```

### Expected Biases and Limitations

- **Genre over-prioritization:** With a weight of 3.0, genre dominates the score. A song that matches mood, energy, and valence perfectly but has a different genre will likely score lower than a genre-matched song with poor numerical fit. This mirrors a real "filter bubble" effect.
- **Exact-match penalty:** Categorical features use binary matching (1 or 0). There's no concept of "similar" genres — rock and metal get 0 points for a rock-preferring user, even though they're sonically close.
- **Small catalog bias:** With only 18 songs, some genres have just 1 representative, making recommendations for those genres trivially deterministic.

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Sample Recommendation Output

Output from running `python -m src.main` with a pop/happy/high-energy user profile:

```
Loaded songs: 18

============================================================
  MUSIC RECOMMENDER -- Top 5 Picks
============================================================
  User profile: genre=pop, mood=happy, energy=0.8
------------------------------------------------------------

  #1  Sunrise City  by Neon Echo
       Genre: pop  |  Mood: happy  |  Energy: 0.82
       Score: 7.74 / 8.00
       Why:   genre match (+3.0); mood match (+2.0); energy proximity 0.98 (+1.5);
              valence proximity 0.86 (+0.9); acousticness fit 0.82 (+0.4)

  #2  Gym Hero  by Max Pulse
       Genre: pop  |  Mood: intense  |  Energy: 0.93
       Score: 5.71 / 8.00
       Why:   genre match (+3.0); energy proximity 0.87 (+1.3);
              valence proximity 0.93 (+0.9); acousticness fit 0.95 (+0.5)

  #3  Rooftop Lights  by Indigo Parade
       Genre: indie pop  |  Mood: happy  |  Energy: 0.76
       Score: 4.66 / 8.00
       Why:   mood match (+2.0); energy proximity 0.96 (+1.4);
              valence proximity 0.89 (+0.9); acousticness fit 0.65 (+0.3)

  #4  Golden Hour Freestyle  by Ray Vega
       Genre: hip-hop  |  Mood: energetic  |  Energy: 0.85
       Score: 2.85 / 8.00
       Why:   energy proximity 0.95 (+1.4); valence proximity 0.98 (+1.0);
              acousticness fit 0.88 (+0.4)

  #5  Neon Pulse  by Circuit Theory
       Genre: electronic  |  Mood: intense  |  Energy: 0.92
       Score: 2.65 / 8.00
       Why:   energy proximity 0.88 (+1.3); valence proximity 0.85 (+0.9);
              acousticness fit 0.96 (+0.5)

============================================================
```

---

## Experiments You Tried

### Weight Shift: Genre halved (3.0 -> 1.5), Energy doubled (1.5 -> 3.0)

- **Pop Fan profile:** "Rooftop Lights" (indie pop/happy) jumped from #3 to #2, overtaking "Gym Hero" (pop/intense). With less genre dominance, the mood match became the tiebreaker, which felt more musically accurate -- a happy indie pop song is closer to a "happy pop" vibe than an intense pop workout track.
- **Melancholy Classical edge case:** "Iron Wake" (metal, energy 0.97) rose from score 2.48 to 3.96, closing in on "Autumn Sonata" (classical, score dropped from 6.81 to 5.72). The system became more energy-responsive but started recommending metal to a classical listener.
- **Takeaway:** Lower genre weight = more diverse but less genre-specific results. Neither weighting is objectively "correct."

### Multi-Profile Stress Test

Tested 5 profiles (3 standard + 2 adversarial edge cases). Key observation: "Gym Hero" appeared in the top-5 for 3 out of 5 profiles because of its extreme energy (0.93) and low acousticness (0.05). It acts as a "universal high-energy filler" -- the system's equivalent of that one gym playlist song everyone tolerates.

---

## Limitations and Risks

- **Tiny catalog (18 songs):** Many genres have only 1 representative. A jazz fan will always get the same #1 regardless of other preferences.
- **No lyric or language understanding:** The system treats all songs as bags of numbers. A Spanish-language latin track and an English pop track are compared purely by audio features.
- **Genre filter bubble:** Genre weight (3.0/8.0 = 37.5% of total score) means the system rarely suggests cross-genre discoveries. A rock fan will never discover a metal song that matches their energy and mood perfectly.
- **Cannot handle contradictory preferences:** A user requesting "high-energy classical" gets a low-energy classical song because genre+mood points overwhelm the energy mismatch.
- **Binary categorical matching:** No concept of genre similarity -- rock and metal get 0 genre points for each other despite being sonically related.

See [model_card.md](model_card.md) for a deeper analysis.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Building this recommender revealed that recommendation is fundamentally a translation problem: converting a vague human concept ("I want something that vibes") into precise mathematical operations (weighted proximity scoring). The most surprising discovery was how much the weights matter -- changing just two numbers (genre from 3.0 to 1.5, energy from 1.5 to 3.0) completely reshuffled the recommendations. There is no single "right" configuration; every weighting reflects a design decision about which dimension of taste to prioritize.

Bias shows up in subtle, structural ways. The genre weight creates a filter bubble by design -- it is literally coded to favor same-genre songs. The binary genre matching treats "rock" and "metal" as completely unrelated, which disadvantages niche listeners whose taste spans adjacent genres. And because the catalog has more pop/lofi songs than classical or jazz, users of underrepresented genres get worse recommendations simply because the system has fewer options to choose from. These are the same dynamics that play out at scale on platforms like Spotify and TikTok, where algorithmic choices about weights and features shape what millions of people hear.

---

## Optional Extensions Completed

1. **Advanced Song Features (5 new attributes):** Added `popularity` (0-100), `release_decade`, `instrumentalness` (0-1), `speechiness` (0-1), and `liveness` (0-1) to the dataset and scoring logic. Each new attribute has a corresponding user preference and contributes to the final score.
2. **Strategy Pattern (Multiple Modes):** Refactored scoring into modular strategies (`BalancedScorer`, `GenreFirstScorer`, `EnergyFocusedScorer`) so users can experience how different algorithms rank the exact same profile.
3. **Diversity & Fairness Logic:** Added a greedy selection algorithm with a "Diversity Penalty" that actively subtracts points from a song if its artist or genre is already represented in the top results, preventing monotonous recommendations.
4. **Visual Summary Table:** Overhauled the CLI output to render a clean, readable ASCII table that wraps the complex "Why" explanations neatly into columns.
