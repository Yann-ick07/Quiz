"""
quiz_engine.py – Spielsteuerung für die Konsolenversion

Steuert den Frage-Antwort-Ablauf für beide Spielmodi:
  - Solo:        Feste Anzahl Fragen (10), kein Zeitlimit pro Frage
  - Time Attack: Unbegrenzte Fragen, aber nur 60 Sekunden Gesamtzeit

Warum eine eigene Engine-Klasse?
    Die Spiellogik (Fragen stellen, Eingabe lesen, Punkte vergeben) ist
    klar von der Datenverwaltung (QuestionDB) und dem Spieler (Player)
    getrennt. Die Engine orchestriert nur, wann und wie sie zusammenarbeiten.
    Das macht das Testen der einzelnen Teile einfacher.

Hinweis:
    Die Web-Version (app.py) implementiert dieselbe Logik direkt in den
    Flask-Routen, weil dort kein blockierendes input() verwendet werden kann.
"""

import time
import sys
from player import Player
from question_db import QuestionDB

# Antwortbuchstaben für die Anzeige (Index 0 = "A", 1 = "B", ...)
OPTION_LABELS = ["A", "B", "C", "D"]

# Anzahl Fragen im Solo-Modus
SOLO_QUESTION_COUNT = 10

# Zeitlimit in Sekunden für den Time-Attack-Modus
TIME_ATTACK_DURATION = 60


class QuizEngine:
    """
    Führt eine Quizrunde für einen Spieler in einem bestimmten Modus aus.

    Die Engine ist zustandslos zwischen Runden – für jede neue Runde
    wird eine neue Instanz erstellt (siehe main.py → play_game()).
    """

    def __init__(self, db: QuestionDB, player: Player, mode: str, category: str):
        """
        Args:
            db:       Fragedatenbank, aus der Fragen geladen werden
            player:   Spieler-Objekt, das Punkte und Statistiken verwaltet
            mode:     "solo" oder "time_attack"
            category: Kategoriename oder "random"
        """
        self.db = db
        self.player = player
        self.mode = mode
        self.category = category

    def run(self):
        """
        Startet die Spielrunde basierend auf dem gewählten Modus
        und zeigt danach die Zusammenfassung an.
        """
        if self.mode == "solo":
            self._run_solo()
        elif self.mode == "time_attack":
            self._run_time_attack()

        self._show_game_summary()

    # ── Solo-Modus ────────────────────────────────────────────────────────────

    def _run_solo(self):
        """
        Stellt genau SOLO_QUESTION_COUNT Fragen ohne Zeitlimit.
        Der Spieler hat so viel Zeit wie er braucht pro Frage,
        aber die Antwortzeit beeinflusst den Speed-Bonus.
        """
        questions = self.db.get_questions(self.category, count=SOLO_QUESTION_COUNT)

        if not questions:
            print("No questions found for this category. Returning to menu.")
            return

        for idx, question in enumerate(questions, 1):
            print(f"\n── Question {idx}/{len(questions)} ──")
            answered = self._ask_question(question)
            if not answered:
                break  # Ctrl+C wurde gedrückt – Schleife sauber beenden

    # ── Time-Attack-Modus ─────────────────────────────────────────────────────

    def _run_time_attack(self):
        """
        Stellt Fragen, bis die Gesamtzeit von TIME_ATTACK_DURATION Sekunden
        abgelaufen ist. Die Frageliste wird 10-fach wiederholt, damit
        bei sehr schnellen Spielern nie der Vorrat ausgeht.
        """
        questions = self.db.get_questions(self.category)
        question_pool = questions * 10  # Genug Fragen für jeden Spieler
        deadline = time.time() + TIME_ATTACK_DURATION

        print(f"\nYou have {TIME_ATTACK_DURATION} seconds. Go!\n")

        for idx, question in enumerate(question_pool, 1):
            remaining = deadline - time.time()
            if remaining <= 0:
                break  # Zeit abgelaufen, bevor eine neue Frage gestartet wird

            print(f"\n── Question {idx} | ⏱  {remaining:.0f}s remaining ──")
            answered = self._ask_question(question, time_limit=remaining)
            if not answered:
                break  # Zeit lief während der Eingabe ab oder Ctrl+C

        print("\n⏰  Time's up!")

    # ── Kernlogik: Frage stellen und auswerten ────────────────────────────────

    def _ask_question(self, question: dict, time_limit: float = None) -> bool:
        """
        Zeigt eine Frage an, liest die Eingabe und wertet die Antwort aus.

        HTML-Entities (z.B. &amp; oder &#039;) kommen von der Open Trivia DB
        und werden mit html.unescape() in lesbare Zeichen umgewandelt.

        Args:
            question:   Frage-Dict aus der QuestionDB
            time_limit: Maximale Restzeit in Sekunden (nur für Anzeige genutzt)

        Returns:
            True wenn die Frage beantwortet wurde, False wenn abgebrochen
        """
        import html

        # HTML-Entities dekodieren (für Fragen aus der Open Trivia DB)
        q_text = html.unescape(question["question"])
        options = [html.unescape(opt) for opt in question["options"]]
        correct_index = question["answer"]

        print(f"\n{q_text}\n")
        for i, opt in enumerate(options):
            print(f"  {OPTION_LABELS[i]}. {opt}")

        # Antwortzeit messen – wird für den Speed-Bonus verwendet
        start_time = time.time()
        answer = self._get_answer(time_limit)
        elapsed = time.time() - start_time

        if answer is None:
            return False  # Ctrl+C oder Timeout

        if answer == "q":
            print("\nQuitting current game...")
            sys.exit(0)

        if answer == "h":
            # Hilfe anzeigen ohne Zeitstrafe – danach dieselbe Frage wiederholen
            from main import show_help

            show_help()
            return self._ask_question(question, time_limit)

        chosen_index = OPTION_LABELS.index(answer.upper())

        if chosen_index == correct_index:
            # Punkte vergeben und Speed-Bonus-Info anzeigen
            points = self.player.award_points(elapsed)
            speed_info = " ⚡ Speed bonus!" if elapsed < 5 else ""
            print(f"  ✔  Correct! +{points} points{speed_info}")
        else:
            # Falsche Antwort: nur Gesamtzähler erhöhen, keine Punkte
            self.player.record_wrong_answer()
            correct_label = OPTION_LABELS[correct_index]
            print(f"  ✘  Wrong! Correct answer: {correct_label}. {options[correct_index]}")

        print(f"  Score: {self.player.current_score}")
        return True

    def _get_answer(self, time_limit: float = None) -> str:
        """
        Liest eine Eingabe von der Konsole und gibt sie normalisiert zurück.

        Akzeptiert: A/B/C/D (Buchstaben) und 1/2/3/4 (Zahlen, werden umgewandelt).
        Gibt None zurück bei Ctrl+C oder ungültigem Timeout.

        Args:
            time_limit: Nicht direkt genutzt (Eingabe blockiert), aber für
                        zukünftige non-blocking Eingabe vorbereitet

        Returns:
            Kleinbuchstabe "a"-"d", "h" oder "q", oder None bei Abbruch
        """
        valid_choices = {"a", "b", "c", "d", "1", "2", "3", "4", "h", "q"}
        number_map = {"1": "a", "2": "b", "3": "c", "4": "d"}
        prompt = "\nYour answer (A/B/C/D, h=help, q=quit): "

        while True:
            try:
                answer = input(prompt).strip().lower()
            except KeyboardInterrupt:
                print("\n\nSpiel abgebrochen.")
                return None

            if not answer:
                continue  # Leere Eingabe ignorieren

            if answer in valid_choices:
                return number_map.get(answer, answer)  # Zahl → Buchstabe umwandeln

            print("  Invalid input. Please enter A, B, C, D (or 1-4).")

    # ── Zusammenfassung ───────────────────────────────────────────────────────

    def _show_game_summary(self):
        """
        Gibt am Spielende eine formatierte Zusammenfassung auf der Konsole aus.
        Die detaillierte Antwort-für-Antwort-Auswertung gibt es in der Web-UI.
        """
        p = self.player
        print("\n" + "═" * 50)
        print("  GAME OVER")
        print("═" * 50)
        print(f"  Player   : {p.name}")
        print(f"  Score    : {p.current_score}")
        print(f"  Correct  : {p.correct_answers} / {p.total_answers}")
        print(f"  Accuracy : {p.accuracy():.0f}%")
        print("═" * 50)
