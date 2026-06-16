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

## Klassendiagramm

```mermaid
classDiagram

    class Player {
        +str name
        +int current_score
        +int correct_answers
        +int total_answers
        +int fast_answers
        +int BASE_POINTS = 10
        +int MAX_SPEED_BONUS = 5
        +int FAST_ANSWER_THRESHOLD = 5
        +award_points(answer_time) int
        +record_wrong_answer()
        +accuracy() float
        +reset_score()
        +__str__() str
    }

    class QuestionDB {
        +list questions
        +str DATA_FILE
        +get_categories() list
        +get_questions(category, count) list
        +get_question_count(category) int
        +add_question(category, question, options, answer)
        -_load_questions() list
        -_save_questions()
    }

    class AccountManager {
        +dict accounts
        +str ACCOUNTS_FILE
        +register(username, password) tuple
        +login(username, password) tuple
        +get_profile(username) dict
        +update_stats(username, score)
        +add_achievement(username, achievement_id)
        +user_exists(username) bool
        -_load() dict
        -_save()
    }

    class Leaderboard {
        +list entries
        +str SCORES_FILE
        +int MAX_ENTRIES = 10
        +add_entry(name, score, category, mode)
        +display(filter_mode)
        -_load() list
        -_save()
    }

    class achievements {
        <<module>>
        +dict ACHIEVEMENTS
        +check_achievements(games_played, total_score, ...) list
        +get_all_achievements() dict
    }

    class quiz_engine {
        <<module>>
        +run_quiz(player, db, category, mode)
        +calculate_points(time) int
        +display_question(q, number, total)
    }

    class app_Flask {
        <<module>>
        +Flask app
        +GET / index()
        +GET POST /login login()
        +GET POST /register register()
        +GET /logout logout()
        +GET POST /play play()
        +GET /leaderboard leaderboard()
        +GET POST /admin admin()
        +GET /profile profile()
    }

    %% Beziehungen
    quiz_engine ..> Player           : uses
    quiz_engine ..> QuestionDB       : uses

    app_Flask   ..> Player           : uses
    app_Flask   ..> QuestionDB       : uses
    app_Flask   ..> AccountManager   : uses
    app_Flask   ..> Leaderboard      : uses
    app_Flask   ..> quiz_engine      : uses
    app_Flask   ..> achievements     : uses

    AccountManager ..> achievements  : uses
```

## Achievements

| Icon | Name | Bedingung |
|------|------|-----------|
| 🎮 | First Steps | Erstes Spiel abschließen |
| 🏆 | Perfect Mind | Alle Fragen richtig |
| ⚡ | Speed Demon | 3 Fragen unter 3 Sekunden |
| 💯 | Century | 100 Gesamtpunkte |
| 🎓 | Scholar | 500 Gesamtpunkte |
| 🎖 | Veteran | 10 Spiele gespielt |
| 🧠 | Quiz Master | 80% Genauigkeit (mind. 5 Fragen) |

## Punkte-System

| Ereignis | Punkte |
|----------|--------|
| Richtige Antwort | +10 |
| Speed Bonus (< 5s) | +0 bis +5 |
| Falsche Antwort | 0 |

## Team-Organisation im Scrum

```text
==========================
Leon = Developer
----------------
Aufgaben:
- Entwicklung der Software
- Implementierung neuer Features
- Erstellung und Durchführung von Tests
- Unterstützung bei der technischen Dokumentation
- Fehlerbehebung und Wartung des Codes

Robin = Scrum Master
--------------------
Aufgaben:
- Überwachung des Scrum-Prozesses
- Moderation der Sprintplanung
- Organisation von Retrospektiven
- Unterstützung des Teams bei Problemen und Hindernissen
- Pflege und Verwaltung des Scrum-Boards

Yannick = Product Owner
-----------------------
Aufgaben:
- Sammlung und Analyse der Anforderungen
- Priorisierung der Anforderungen im Product Backlog
- Abstimmung mit dem Lehrerteam und dem Auftraggeber
- Definition der Sprintziele
- Abnahme der entwickelten Funktionen

Hinweis:
Da es sich um ein kleines Projektteam handelt, übernehmen alle Teammitglieder zusätzlich Entwicklungsaufgaben und unterstützen sich gegenseitig bei Tests, Dokumentation und Qualitätssicherung.
```

## User Stories

1. Als Spieler möchte ich verschiedene Kategorien auswählen können, damit ich genau das Thema spielen kann, das mich interessiert.  
2. Als User möchte ich mich mit meinem Benutzernamen und Passwort registrieren können, damit ich beim nächsten Besuch wieder auf meinen Punktestand und meine Spielhistorie zugreifen kann.  
3. Als User möchte ich mich mit meinem Benutzernamen und Passwort einloggen können, damit ich meine Spielhistorie einsehen kann.  
4. Als Spieler möchte ich am Ende eines Spiels eine Rangliste sehen, damit ich einen Anreiz habe, mich zu verbessern und mich mit Freunden vergleichen kann.  
5. Als Spieler möchte ich das Spiel über den Browser spielen können, damit ich es auch ohne Terminal unterwegs nutzen kann.  
6. Als Spieler möchte ich einen Schwierigkeitsgrad auswählen können, damit ich das Quiz individuell an mein Wissen anpassen kann.  
7. Als Admin möchte ich über ein einfaches Web-Backend neue Quizfragen oder Kategorien hinzufügen können, damit die Datenbank ohne Code erweitert werden kann.  
8. Als Spieler möchte ich einen Online-Mehrspieler-Modus nutzen können, damit ich gegen Freunde um den Sieg spielen kann.  
