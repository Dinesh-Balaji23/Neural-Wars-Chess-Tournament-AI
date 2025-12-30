<details>
<summary><strong>SOLO Neural Wars Chess Board AI</strong></summary>

**Team:** SOLO  
**Event:** Prometeo '26 – Neural Wars Chess Board Challenge  
**Goal:** Build the strongest non-learning autonomous agent for the 4x8 minichess arena.

</details>

---

## 1. Overview

This repository contains our end-to-end entry for the Neural Wars Chess Board AI event. The engine simulates a 4×8 chess variant and hosts our custom `SOLO` agent, which plays strictly within the constraints set by the organizers:

- Single Python submission file (`SOLO.py`) with class `SOLO`
- No reinforcement learning, supervised learning, or neural policies
- No auxiliary files, assets, or imports beyond the official template
- Logic must rely only on the data passed through the provided interface

Whenever we iterate on the agent, **README.md stays in sync** so evaluators and teammates have a single source of truth for the current strategy, rules, and usage notes.

---

## 2. Repository Layout

| File | Purpose |
| --- | --- |
| `SOLO.py` | Our competition submission implementing `SOLO.get_best_move` and `SOLO.evaluate_board`. |
| `ai_player.py` | Official base class. Must remain unchanged per event rules. |
| `board.py` | Game engine: board state, move generation, legality checks. |
| `config.py` | Piece values, PSTs, dimensions, Unicode symbols. |
| `game_runner.py` | Local harness to pit agents against each other for testing. |
| `docs/GameEngine.md` | Detailed engine reference from organizers. |

> **Upgrade Rule:** Any time logic or parameters change, update `SOLO.py` and this README together so the documentation reflects the exact submission.

---

## 3. Running Local Matches

```bash
python game_runner.py
```

By default both White and Black load the `SOLO` agent. Adjust `white_player_type` / `black_player_type` inside `game_runner.py` if you need mirrors or baselines.

### CLI Tips
1. Keep runs short to respect the 60 s bullet timer.
2. Use printouts from `game_runner` to watch material swings and detect stalemates early.
3. If you edit `config.depth` or heuristics, rerun immediately and log the outcome here.

---

## 4. SOLO Agent Design

| Component | Notes |
| --- | --- |
| Search | Iterative deepening minimax with alpha-beta pruning (depth window 2–5) + quiescence extension. |
| Move Ordering | Capture priority + history heuristic and root move promotion to accelerate pruning. |
| Time Control | Adaptive per-move budget based on branching factor and past think times. |
| Evaluation | Material + PST + king safety, pawn structure, bishop activity, mobility, tempo, repetition penalties, mate scoring. |
| Caching | Lightweight transposition table keyed on board+depth to reuse scores. |
| Compliance | First-line disclaimer confirms zero RL usage; only template imports allowed. |

We deliberately avoid:
- Learning-based heuristics, policy networks, or adaptive tuning.
- Hidden state or backend exploitation.

---

## 5. Submission Checklist

- [x] File name: `SOLO.py`
- [x] Class name: `SOLO`
- [x] Mandatory disclaimer at top of file
- [x] Only implements `get_best_move` and `evaluate_board` plus internal helpers
- [x] No template modifications (e.g., `ai_player.py`, `board.py`)
- [x] No external imports, files, or datasets
- [x] README updated after each upgrade

---

## 6. Official Rules (Condensed)

1. Use the provided template; do not change function signatures.
2. One `.py` file submission only.
3. Pure algorithmic methods—no reinforcement learning or training-based heuristics.
4. No cheating, hacking, or backend manipulation.
5. Agent must base every decision solely on provided game state.
6. Include the mandatory “no RL used” disclaimer comment at the top of the file.

Full wording is kept in the event portal; this summary mirrors what matters for implementation.

---

## 7. Upgrade Log

| Date | Change | Notes |
| --- | --- | --- |
| 2025-12-30 | Initial SOLO agent with depth-4 alpha-beta, PST evaluation, README overhaul. | Baseline submission-ready. |
| 2025-12-30 | Added iterative deepening, history-based move ordering, adaptive time control. | SOLO.py + README synced. |
| 2025-12-30 | Added quiescence search, transposition table, repetition avoidance heuristic. | SOLO.py + README synced. |
| 2025-12-30 | Added king safety, pawn structure, bishop activity, and mobility heuristics. | SOLO.py + README synced. |

Add entries here every time we tweak heuristics, depth, or supporting docs so the lineage remains auditable.

---

## 8. Next Steps

1. Stress-test at multiple depths (3–5) to balance strength vs. clock usage.
2. Explore enhanced move ordering (killer heuristic, history table) while staying within rules.
3. Iterate on evaluation weights; log every adjustment in section 7.

If you push changes, **update this README immediately**—that’s part of our “always upgrade the docs” rule.