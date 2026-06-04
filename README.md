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

## MoSCoW Requirements Coverage (Teil 2: Quiz Game)

### Must Have ✅
- [x] Eigene kleine Funktionen definiert (alle Module)
- [x] Programmcode lesbar und verständlich gestaltet
- [x] Spiel für die umgesetzten Anforderungen getestet
- [x] **1 automatisierter Test** implementiert (`tests.py`)
- [x] Klassendiagramm erstellt (siehe oben & `klassendiagramm.txt`)
- [x] Spiel über die Konsole vollständig spielbar
- [x] Steuerungshilfe mit Parameter `h` (`python main.py h`)
- [x] Am Ende jedes Spiels wird eine Rangliste angezeigt

### Should Have (Teilweise ✅)
- [ ] Spiel über grafische Oberfläche oder Webseite spielbar
- [x] Datenbank erstellt, aus der Quizfragen ausgelesen werden (`data/questions.json`)
- [ ] Jeder Spieler hat seinen eigenen Account
- [x] Rangliste kann jederzeit eingesehen werden (Hauptmenü → Option 2)
- [x] Programm ist leicht erweiterbar:
  - [x] Gute Programmstruktur (Module, kleine Funktionen)
  - [x] Selbsterklärender Programmcode
  - [x] Aussagekräftige Namen der Variablen und Funktionen
  - [x] Sinnvolle Kommentare
- [x] **3 automatisierte Tests** implementiert (19 Tests vorhanden – Anforderung übertroffen)

### Could Have (Teilweise ✅)
- [ ] Mehrspielermodus implementiert
- [ ] Separates Backend zur Verwaltung der Quizfragen (hinzufügen, bearbeiten, löschen)
- [ ] Selbst erdachtes Achievement-System implementiert
- [x] **5 automatisierte Tests** implementiert (19 Tests vorhanden – Anforderung übertroffen)
- [x] Grundlagen der objektorientierten Programmierung angewendet (`Player`, `QuizEngine`, `QuestionDB`, `Leaderboard`)
- [ ] Spiel unter Windows, Mac und Linux getestet

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
