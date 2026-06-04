# BrainBuster 🧠

Ein konsolen- und webbasiertes Quiz-Spiel für das IT-Solutions Projekt (Lernfeld 08).

## Quick Start

```bash
# Abhängigkeiten installieren
pip install flask

# Web-App starten
python app.py
# → http://localhost:5000 im Browser öffnen

# Konsolen-Version
python main.py
python main.py h   # Hilfe

# Alle Tests ausführen
python tests.py
```

## Projektstruktur

```
brainbuster/
├── app.py              # Flask Web-App (Hauptanwendung)
├── main.py             # Konsolen-Version
├── player.py           # Spieler-Klasse (Score, Bonus, Stats)
├── quiz_engine.py      # Spiellogik Konsole (Solo & Time Attack)
├── question_db.py      # Fragedatenbank (JSON + Open Trivia DB)
├── leaderboard.py      # Rangliste (persistent)
├── accounts.py         # Benutzerverwaltung (Register/Login)
├── achievements.py     # Achievement-System (7 Achievements)
├── tests.py            # 35 automatisierte Unit-Tests
├── templates/          # HTML-Templates (Flask/Jinja2)
│   ├── base.html
│   ├── index.html
│   ├── login.html / register.html
│   ├── play.html / question.html / result.html
│   ├── leaderboard.html / profile.html
│   ├── admin.html / edit_question.html
│   └── multiplayer_*.html
└── data/
    ├── questions.json   # Fragedatenbank (auto-erstellt)
    ├── scores.json      # Rangliste (auto-erstellt)
    └── accounts.json    # Benutzerkonten (auto-erstellt)
```

## Sequenzdiagramm

```text
Entwickler        GitHub         GitHub Actions      Runner (Ubuntu)
    |               |                  |                   |
    | git push      |                  |                   |
    |-------------->|                  |                   |
    |               | Workflow startet |                   |
    |               |----------------->|                   |
    |               |                  | Code holen        |
    |               |                  |------------------>|
    |               |                  | Python installieren|
    |               |                  |------------------>|
    |               |                  | Tests ausführen   |
    |               |                  |------------------>|
    |               |                  | Ergebnis zurück   |
    |<--------------|                  |                   |
    | Ergebnis sehen|                  |                   |
```

## MoSCoW Anforderungen (Teil 2: Quiz Game)

### Must Have ✅
- [x] Eigene kleine Funktionen definiert (alle Module)
- [x] Programmcode lesbar und verständlich gestaltet
- [x] Spiel für die umgesetzten Anforderungen getestet
- [x] **1+ automatisierter Test** implementiert (`tests.py`, 35 Tests)
- [x] Klassendiagramm erstellt (`klassendiagramm.txt`)
- [x] Spiel über die Konsole vollständig spielbar (`main.py`)
- [x] Steuerungshilfe mit Parameter `h` (`python main.py h`)
- [x] Am Ende jedes Spiels wird eine Rangliste angezeigt

### Should Have ✅
- [x] Spiel über Webseite spielbar (`app.py` → Flask)
- [x] Datenbank erstellt, aus der Quizfragen ausgelesen werden (`data/questions.json`)
- [x] Jeder Spieler hat seinen eigenen Account (`accounts.py`)
- [x] Rangliste kann jederzeit eingesehen werden (`/leaderboard`)
- [x] Programm ist leicht erweiterbar (Module, kleine Funktionen, Kommentare)
- [x] **3+ automatisierte Tests** (35 Tests vorhanden)

### Could Have ✅
- [x] Mehrspielermodus implementiert (`/multiplayer`, lokales 2-Spieler-Modus)
- [x] Separates Backend zur Verwaltung der Quizfragen (`/admin`: hinzufügen, bearbeiten, löschen)
- [x] Selbst erdachtes Achievement-System (`achievements.py`, 7 Achievements)
- [x] **5+ automatisierte Tests** (35 Tests vorhanden)
- [x] Grundlagen der OOP angewendet (`Player`, `QuizEngine`, `QuestionDB`, `Leaderboard`, `AccountManager`)
- [ ] Spiel unter Windows, Mac und Linux getestet *(steht noch aus)*

## Achievements

| Icon | Name | Bedingung |
|------|------|-----------|
| 🎮 | First Steps | Erstes Spiel abschließen |
| 🏆 | Perfect Mind | Alle Fragen richtig |
| ⚡ | Speed Demon | 3 Fragen unter 3 Sekunden |
| 💯 | Century | 100 Gesamtpunkte |
| 🎓 | Scholar | 500 Gesamtpunkte |
| 🎖️ | Veteran | 10 Spiele gespielt |
| 🧠 | Quiz Master | 80% Genauigkeit (mind. 5 Fragen) |

## Punkte-System

| Ereignis | Punkte |
|----------|--------|
| Richtige Antwort | +10 |
| Speed Bonus (< 5s) | +0 bis +5 |
| Falsche Antwort | 0 |

## Tests ausführen

```bash
python tests.py
```

35 Tests in 5 Klassen:

```
- **TestPlayer** (9): Score, Speed-Bonus, Genauigkeit, Reset
- **TestQuestionDB** (6): Kategorien, Struktur, Shuffling, Hinzufügen
- **TestLeaderboard** (5): Einträge, Sortierung, Max-Größe, Persistenz
- **TestAccountManager** (9): Registrierung, Login, Stats, Achievements
- **TestAchievements** (6): Freischaltbedingungen, Duplikatschutz
```

```text
## Team-Organisation im Scrum
==========================
Leon = **Developer**
----------------
Aufgaben:
- Entwicklung der Software
- Implementierung neuer Features
- Erstellung und Durchführung von Tests
- Unterstützung bei der technischen Dokumentation
- Fehlerbehebung und Wartung des Codes

Robin = **Scrum Master**
--------------------
Aufgaben:
- Überwachung des Scrum-Prozesses
- Moderation der Sprintplanung
- Organisation von Retrospektiven
- Unterstützung des Teams bei Problemen und Hindernissen
- Pflege und Verwaltung des Scrum-Boards

Yannick = **Product Owner**
-----------------------
Aufgaben:
- Sammlung und Analyse der Anforderungen
- Priorisierung der Anforderungen im Product Backlog
- Abstimmung mit dem Lehrerteam und dem Auftraggeber
- Definition der Sprintziele
- Abnahme der entwickelten Funktionen

Hinweis:
Da es sich um ein kleines Projektteam handelt, übernehmen alle Teammitglieder zusätzlich Entwicklungsaufgaben und unterstützen sich gegenseitig bei Tests, Dokumentation und Qualitätssicherung.

