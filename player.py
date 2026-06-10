"""
player.py – Spieler-Zustand und Punktevergabe

Diese Klasse speichert alle Informationen über einen aktiven Spieler
während einer Spielrunde: Name, Punktestand und Statistiken.

Warum eine eigene Klasse?
  Die Spielerlogik (Punkte berechnen, Genauigkeit messen, Rücksetzen)
  ist klar abgrenzbar von der Spielsteuerung (QuizEngine) und der
  Persistenz (Leaderboard). Eine eigene Klasse hält die Verantwortlichkeiten
  getrennt (Single Responsibility Principle).
"""


class Player:
    """
    Repräsentiert einen aktiven Quizspieler mit Punktestand und Statistiken.

    Klassenattribute (Konstanten):
        BASE_POINTS            – Basispunkte pro richtiger Antwort
        MAX_SPEED_BONUS        – Maximaler Bonuspunkt für schnelle Antworten
        FAST_ANSWER_THRESHOLD  – Zeitlimit in Sekunden für den Speed-Bonus
    """

    BASE_POINTS = 10  # Jede richtige Antwort bringt mindestens 10 Punkte
    MAX_SPEED_BONUS = 5  # Bis zu 5 Bonuspunkte für sehr schnelle Antworten
    FAST_ANSWER_THRESHOLD = 5  # Antworten unter 5 Sekunden erhalten einen Bonus

    def __init__(self, name: str):
        """
        Erstellt einen neuen Spieler.

        Args:
            name: Anzeigename des Spielers (max. 20 Zeichen, geprüft in main.py)
        """
        self.name = name
        self.current_score = 0  # Punkte in der aktuellen Runde
        self.correct_answers = 0  # Anzahl richtig beantworteter Fragen
        self.total_answers = 0  # Gesamtanzahl beantworteter Fragen (richtig + falsch)
        self.fast_answers = 0  # Anzahl Antworten unter 3 Sekunden (für Achievements)

    def reset_score(self):
        """
        Setzt alle Statistiken für eine neue Spielrunde zurück.
        Wird in main.py vor jedem neuen Spiel aufgerufen.
        """
        self.current_score = 0
        self.correct_answers = 0
        self.total_answers = 0
        self.fast_answers = 0

    def award_points(self, answer_time: float) -> int:
        """
        Vergibt Punkte für eine richtige Antwort und berechnet den Speed-Bonus.

        Der Speed-Bonus ist linear: Bei 0 Sekunden gibt es den vollen Bonus (+5),
        bei 5 Sekunden keinen Bonus mehr. Formel: bonus = 5 * (1 - t/5)

        Außerdem wird gezählt, ob die Antwort unter 3 Sekunden lag –
        das wird für das Achievement "Speed Demon" benötigt.

        Args:
            answer_time: Antwortzeit in Sekunden (gemessen in QuizEngine / app.py)

        Returns:
            Tatsächlich vergebene Punkte (Basis + Bonus)
        """
        speed_bonus = 0
        if answer_time < self.FAST_ANSWER_THRESHOLD:
            # Linearer Bonus: schnellere Antwort = mehr Punkte
            speed_bonus = int(self.MAX_SPEED_BONUS * (1 - answer_time / self.FAST_ANSWER_THRESHOLD))

        # Separat tracken für das "Speed Demon"-Achievement (3x unter 3s)
        if answer_time < 3:
            self.fast_answers += 1

        points = self.BASE_POINTS + speed_bonus
        self.current_score += points
        self.correct_answers += 1
        self.total_answers += 1
        return points

    def record_wrong_answer(self):
        """
        Erfasst eine falsche Antwort ohne Punktvergabe.
        Wird dennoch für die Genauigkeitsberechnung benötigt.
        """
        self.total_answers += 1

    def accuracy(self) -> float:
        """
        Berechnet die Trefferquote als Prozentwert (0–100).

        Returns:
            0.0 wenn noch keine Fragen beantwortet wurden, sonst Prozentwert.
        """
        if self.total_answers == 0:
            return 0.0
        return (self.correct_answers / self.total_answers) * 100

    def __str__(self) -> str:
        """Lesbare Darstellung für Debugging und Konsolenausgabe."""
        return (
            f"Player: {self.name} | Score: {self.current_score} | "
            f"Correct: {self.correct_answers}/{self.total_answers} "
            f"({self.accuracy():.0f}%)"
        )
