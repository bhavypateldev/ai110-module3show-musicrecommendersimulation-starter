# Model Card: Music Recommender Simulation

## 1. Model Name  

**VibeMatch 1.0** -- A content-based music recommender that scores songs by how closely their attributes match a user's stated taste profile.

---

## 2. Intended Use  

VibeMatch generates a ranked list of song recommendations from a small catalog based on a user's preferred genre, mood, energy level, and acoustic preference. It assumes the user can express their taste as a simple set of target values. This is a **classroom simulation** built for learning how recommendation algorithms work -- it is not designed for production use with real listeners.

**Non-Intended Use:** This system should NOT be used to make real music licensing decisions, judge musical quality, or serve as a production recommendation engine. It has no concept of copyright, listener demographics, or cultural context. The 18-song catalog is far too small to represent the diversity of real music, and the fixed weights reflect one designer's assumptions about taste -- not validated user research. Using this system to filter or gatekeep music access could amplify the genre biases documented in Section 6.

---

## 3. How the Model Works  

Imagine you walk into a record store and tell the clerk: "I want something pop, happy, and high-energy." The clerk mentally goes through every album on the shelf and gives each one a score based on how well it matches your request.

That is exactly what VibeMatch does. For each song in the catalog, it checks:

1. **Genre** -- Does the song's genre match what you asked for? If yes, it gets 3 points. This is the biggest factor because most people filter by genre first.
2. **Mood** -- Does the song's mood match? A match earns 2 points. Mood matters a lot, but a "chill rock" song can still appeal to someone who said "intense" if the energy is right.
3. **Energy** -- How close is the song's energy level to your target? Instead of just checking "high or low," it measures the gap. A song at 0.82 when you want 0.80 scores almost perfectly (0.98 out of 1.0), earning up to 1.5 points.
4. **Valence (positivity)** -- Same proximity logic as energy. Measures how upbeat vs. melancholy the song is. Worth up to 1.0 point.
5. **Acousticness** -- If you prefer acoustic music, songs with more acoustic qualities score higher; if not, electronic-sounding tracks win. Worth up to 0.5 points.

The maximum possible score is 10.5 (a perfect match on every dimension). After scoring all songs, VibeMatch sorts them highest-to-lowest and shows you the top 5.

Compared to the starter code (which just returned the first k songs with no logic), this version implements real weighted scoring with per-feature explanations.

---

## 4. Data  

The catalog contains **18 songs** with 15 attributes each (id, title, artist, genre, mood, energy, tempo_bpm, valence, danceability, acousticness, popularity, release_decade, instrumentalness, speechiness, liveness).

**Genres represented (10):** pop, lofi, rock, ambient, jazz, synthwave, indie pop, hip-hop, electronic, classical, r&b, folk, metal, latin, country

**Moods represented (12):** happy, chill, intense, relaxed, moody, focused, energetic, melancholy, nostalgic, romantic, aggressive, upbeat

The original starter dataset had 10 songs. I added 8 new songs to cover genres and moods that were missing (hip-hop, electronic, classical, r&b, folk, metal, latin, country).

**Missing aspects of musical taste:** The dataset does not capture lyrics/language, song length, or cultural context. It also has no concept of "similar" genres -- the system treats rock and metal as completely unrelated, even though they share sonic DNA.

---

## 5. Strengths  

- **Works well for mainstream profiles:** Users with clear, well-represented preferences (like "pop/happy" or "lofi/chill") get highly relevant results. For the "Chill Lofi Listener" profile, the top 2 results were both lofi/chill songs with near-perfect scores (7.93 and 7.71 out of 8.0).
- **Energy proximity scoring is effective:** The system correctly identifies that a song with energy 0.82 is a better match for a 0.80 target than a song with energy 0.93, even though both are "high energy." This is more nuanced than simple thresholding.
- **Explanations build trust:** Every recommendation comes with a breakdown of exactly which features contributed points, making the system transparent and debuggable.
- **Results match intuition:** For the "Deep Intense Rock" profile, "Storm Runner" by Voltline (rock/intense/0.91 energy) ranked #1 at 7.85/8.00. That feels exactly right.

---

## 6. Limitations and Bias 

**Genre over-prioritization (filter bubble):** With a weight of 3.0 out of 8.0 total, genre alone accounts for 37.5% of the maximum score. This means a song that perfectly matches your mood, energy, and valence but has a different genre will almost always lose to a mediocre song in your preferred genre. For example, in the "High-Energy Pop Fan" profile, "Gym Hero" (pop/intense) scored 5.71 while "Rooftop Lights" (indie pop/happy) scored only 4.66 -- even though "Rooftop Lights" matched the user's mood better. The genre weight creates a filter bubble where the system never suggests cross-genre discoveries.

**Binary categorical matching:** Genre and mood use exact matching (1 or 0). There is no concept of genre similarity. A user who likes "rock" gets zero genre points for "metal" or "punk," even though those genres are musically adjacent. This penalizes niche or cross-genre users disproportionately.

**Small catalog bias:** With only 18 songs and many genres having just 1 representative, single-genre users (like "classical") will always get the same #1 result regardless of their other preferences. The system cannot provide variety within a genre.

**Adversarial fragility:** The "High-Energy Melancholy Classical" edge case exposed a weakness: the system recommended "Autumn Sonata" (energy 0.22) as #1 even though the user wanted energy 0.95. The genre+mood match (5 points) overwhelmed the terrible energy fit (0.4 points). The system cannot handle contradictory preferences gracefully.

**No popularity or novelty signals:** Unlike real systems, VibeMatch has no concept of trending songs, new releases, or play counts, so it cannot balance relevance with discovery.

---

## 7. Evaluation  

### Profiles Tested

I tested 5 user profiles -- 3 standard and 2 adversarial edge cases:

1. **High-Energy Pop Fan** (genre=pop, mood=happy, energy=0.8)
2. **Chill Lofi Listener** (genre=lofi, mood=chill, energy=0.35)
3. **Deep Intense Rock** (genre=rock, mood=intense, energy=0.9)
4. **EDGE: High-Energy Melancholy** (genre=classical, mood=melancholy, energy=0.95) -- contradictory
5. **EDGE: Perfectly Average** (genre=jazz, mood=relaxed, energy=0.5)

### Key Findings

**Pop Fan vs. Lofi Listener:** These two profiles produce completely non-overlapping top-5 lists, which is exactly what we want. The Pop Fan gets upbeat, high-energy tracks (Sunrise City, Gym Hero), while the Lofi Listener gets mellow, acoustic tracks (Library Rain, Midnight Coding). This confirms that the combination of genre, mood, and energy preferences successfully separates distinct listener types.

**Pop Fan vs. Rock Fan:** Both profiles want high energy, but genre separates them cleanly. The Pop Fan's #1 is "Sunrise City" (pop/happy) while the Rock Fan's #1 is "Storm Runner" (rock/intense). Interestingly, "Gym Hero" (pop/intense) appears in both top-5 lists -- at #2 for Pop and #3 for Rock. This makes sense: "Gym Hero" has the right energy for both users, but it matches Pop Fan's genre and Rock Fan's mood. This shows how the weighted system resolves partial matches.

**Why "Gym Hero" keeps appearing:** "Gym Hero" (pop/intense, energy 0.93) showed up in the top-5 for the Pop Fan, Rock Fan, and even the High-Energy Melancholy edge case. This is because it has the highest energy in the catalog (0.93), high danceability (0.88), and very low acousticness (0.05). For any user who wants high energy and does not prefer acoustic music, "Gym Hero" will score well on the numerical features alone, even without a genre or mood match. Think of it like that one catchy gym playlist song that everyone tolerates -- it is inoffensive enough to rank moderately for many different taste profiles.

**Edge Case -- Melancholy Classical at High Energy:** This was the most revealing test. The user wanted classical music with a melancholy mood but energy at 0.95 -- a contradictory request since classical/melancholy tracks in our catalog have very low energy (0.22). The system still recommended "Autumn Sonata" as #1 (score 6.81), but with a terrible energy proximity of only 0.27. The 5 points from genre+mood matching outweighed the energy mismatch. This reveals that the system cannot flag or warn about contradictory preferences.

**Edge Case -- Perfectly Average:** The jazz/relaxed user got "Coffee Shop Stories" as #1 at 7.54/8.00 -- an excellent match. Below that, the scores dropped sharply to 2.77, showing that jazz is underrepresented in the catalog (only 1 song). After the genre+mood match is used up, the system falls back to numerical proximity alone.

### Weight Experiment

I ran an experiment where I halved the genre weight (3.0 to 1.5) and doubled the energy weight (1.5 to 3.0). Key changes observed:

- **Pop Fan:** "Rooftop Lights" (indie pop/happy) jumped from #3 to #2, overtaking "Gym Hero" (pop/intense). With less genre dominance, mood match became the tiebreaker, which is arguably more musically accurate.
- **Melancholy Classical edge case:** "Autumn Sonata" dropped from 6.81 to 5.72, and "Iron Wake" (metal, energy 0.97) rose from 2.48 to 3.96. The system became more energy-responsive but started recommending metal to a classical listener -- trading one kind of inaccuracy for another.
- **Overall takeaway:** The experiment made recommendations more diverse but less genre-specific. Neither weighting is objectively "correct" -- it depends on whether you believe genre or energy is the stronger signal of taste.

---

## 8. Future Work  

- **Genre similarity scores:** Instead of binary matching, use a similarity matrix (e.g., rock-metal = 0.7, rock-jazz = 0.1) to allow partial genre credit and reduce filter bubbles.
- **Conflict detection:** Warn the user when their preferences are internally contradictory (e.g., "No classical songs in our catalog have energy above 0.5").
- **Diversity penalty:** After selecting the top-k, penalize songs with the same genre to ensure variety (e.g., not all 5 picks should be lofi).
- **User feedback loop:** Let users mark songs as "liked" or "skipped" to refine their profile over time, moving toward a hybrid collaborative/content-based approach.
- **Richer profile:** Add `target_danceability`, `target_tempo`, and `target_valence` to the UserProfile to capture more nuanced taste.

---

## 9. Personal Reflection  

**Biggest learning moment:** The weight experiment was the turning point. When I halved the genre weight and doubled energy, "Rooftop Lights" (indie pop/happy) jumped ahead of "Gym Hero" (pop/intense) for the Pop Fan profile. That single change taught me more about how recommendation systems work than any amount of reading -- it made tangible that every recommendation is a *design decision*, not an objective truth. The algorithm does not "know" what good music is; it just follows the math we give it.

**How AI tools helped -- and where I double-checked:** My AI coding assistant was invaluable for scaffolding the project structure, generating the initial scoring formula, and producing diverse test songs for the CSV. However, I needed to double-check the weight values it suggested -- the initial proposal treated all features equally, which would not have differentiated genre from acousticness. I also verified the proximity formula by hand (`1 - |0.8 - 0.82| = 0.98`) to make sure the math rewarded closeness rather than raw magnitude. The AI was excellent at producing boilerplate and explaining concepts (like `sorted()` vs `.sort()`), but the design decisions -- how much genre should matter, what makes a good edge case -- required human judgment.

**What surprised me about simple algorithms:** I was genuinely surprised that a formula with just 5 weighted terms could produce recommendations that "feel" reasonable. When the Chill Lofi profile returned "Library Rain" and "Midnight Coding" as #1 and #2, those felt like exactly what a lofi playlist should contain. The system has no understanding of music -- it is just comparing numbers -- but the results feel intentional. That gap between mechanical simplicity and perceived intelligence is what makes recommendation systems both powerful and dangerous: users trust results that "feel right" without realizing how fragile the underlying logic is.

**What I would try next:** If I extended this project, I would implement a genre similarity matrix so that rock and metal get partial credit instead of 0 points. I would also add a diversity constraint to prevent the top-5 from being all the same genre, and build a simple web interface where users can adjust the weights with sliders and see how their recommendations change in real time. That would make the "weights = design decisions" lesson interactive and visceral.
