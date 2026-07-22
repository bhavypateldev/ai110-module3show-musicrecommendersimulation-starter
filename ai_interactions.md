# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agentic Workflow (SF8)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

I asked the agent to implement Challenge 1 (adding advanced song features like `popularity` and `release_decade`) by updating the `songs.csv` dataset and modifying the Python parsing and scoring logic to account for these new dimensions.

**Prompts used:**

"Add popularity (0-100) and release_decade (e.g. 1990, 2020) to data/songs.csv and update the Song and UserProfile dataclasses in src/recommender.py to support them. Also ensure the scoring logic factors them in."

**What did the agent generate or change?**

The agent completely rewrote `data/songs.csv` to inject realistic popularity and decade values for all 18 songs. It then modified `src/recommender.py` to add those fields to the dataclasses and update `load_songs` to cast them correctly. It also added distance proximity matching for popularity and exact-matching for decade.

**What did you verify or fix manually?**

I had to ensure the agent provided default values in the `Song` and `UserProfile` dataclasses so that the existing test suite in `tests/test_recommender.py` would not break (since the test suite only instantiates objects with the baseline fields).

---

## Design Pattern (SF10)

> Document how AI helped you choose or implement a design pattern.

**Which design pattern did you use?**

The **Strategy Pattern**.

**How did AI help you brainstorm or implement it?**

I used the AI to help me restructure the hardcoded scoring dictionary into a class-based hierarchy. We defined a `ScoringStrategy` base class and created subclasses like `BalancedScorer`, `GenreFirstScorer`, and `EnergyFocusedScorer`. 

**How does the pattern appear in your final code?**

In `src/recommender.py`, there is an abstract class `ScoringStrategy`. The function `recommend_songs` now takes a `strategy` object as an argument. Depending on which strategy is passed from `src/main.py`, the recommendation logic dynamically changes its weights without altering the underlying recommendation loop.
