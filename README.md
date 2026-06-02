# BrainBuster 🧠

A console-based quiz game built for the IT-Solutions BrainBuster project (Lernfeld 08).

## Quick Start

```bash
# Play the game
python main.py

# Show controls/help
python main.py h

# Run all automated tests
python tests.py
```

## Project Structure

```
brainbuster/
├── main.py          # Entry point, menus, game flow
├── player.py        # Player state and scoring logic
├── quiz_engine.py   # Game loop (Solo & Time Attack modes)
├── question_db.py   # Question storage and retrieval
├── leaderboard.py   # High-score persistence and display
├── tests.py         # Automated unit tests (20 tests)
└── data/
    ├── questions.json   # Question database (auto-created)
    └── scores.json      # Leaderboard scores (auto-created)
```

## Class Diagram

```
┌──────────────┐        ┌─────────────────┐
│    Player    │        │   QuestionDB    │
├──────────────┤        ├─────────────────┤
│ name: str    │        │ questions: list │
│ current_score│        ├─────────────────┤
│ correct_ans  │        │ get_categories()│
│ total_ans    │        │ get_questions() │
├──────────────┤        │ add_question()  │
│ award_points()│       │ _load()         │
│ record_wrong()│       │ _save()         │
│ accuracy()   │        └────────┬────────┘
│ reset_score()│                 │ uses
└──────┬───────┘                 │
       │ used by                 │
       ▼                         ▼
┌──────────────────────────────────────┐
│             QuizEngine               │
├──────────────────────────────────────┤
│ db: QuestionDB                       │
│ player: Player                       │
│ mode: str  (solo | time_attack)      │
│ category: str                        │
├──────────────────────────────────────┤
│ run()                                │
│ _run_solo()                          │
│ _run_time_attack()                   │
│ _ask_question()                      │
│ _get_answer()                        │
│ _show_game_summary()                 │
└──────────────────────────────────────┘

┌──────────────────┐
│   Leaderboard    │
├──────────────────┤
│ entries: list    │
├──────────────────┤
│ add_entry()      │
│ display()        │
│ _load()          │
│ _save()          │
└──────────────────┘
```

## MoSCoW Requirements Coverage

### Must Have ✅
- [x] Own small functions defined (every module)
- [x] Readable and well-commented code
- [x] Game tested for implemented features
- [x] **20 automated tests** implemented (`tests.py`)
- [x] Class diagram (see above)
- [x] Fully playable via console
- [x] Help via `python main.py h`
- [x] Leaderboard shown at end of each game

### Should Have ✅
- [x] Questions stored in a JSON database
- [x] Leaderboard viewable at any time from the menu
- [x] Good code structure (modules, small functions, clear names)
- [x] **20 automated tests** (exceeds the "3 tests" requirement)

### Could Have (Partial)
- [x] Open Trivia DB integration (`fetch_questions_from_opentdb` in `question_db.py`)
- [ ] Multiplayer mode (planned for next sprint)
- [ ] Separate backend admin panel

## Scoring

| Event | Points |
|-------|--------|
| Correct answer | +10 |
| Speed bonus (< 5s) | +0 to +5 |
| Wrong answer | 0 |

## Running Tests

```bash
python tests.py
```

Tests cover:
- **Player**: score, speed bonus, accuracy, reset
- **QuestionDB**: categories, question structure, shuffling, add
- **Leaderboard**: add entries, sorting, max-size cap, persistence
