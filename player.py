"""
player.py - Player state, scoring, and in-game stats tracking.
"""


class Player:
    """Represents a quiz player with name, score and in-game statistics."""

    BASE_POINTS = 10
    MAX_SPEED_BONUS = 5
    FAST_ANSWER_THRESHOLD = 5  # seconds

    def __init__(self, name: str):
        self.name = name
        self.current_score = 0
        self.correct_answers = 0
        self.total_answers = 0
        self.fast_answers = 0  # answers given in under 3 seconds

    def reset_score(self):
        """Reset all stats for a new game session."""
        self.current_score = 0
        self.correct_answers = 0
        self.total_answers = 0
        self.fast_answers = 0

    def award_points(self, answer_time: float) -> int:
        """
        Award points for a correct answer with an optional speed bonus.
        Tracks fast answers (under 3s) for achievement checking.
        Returns the total points awarded.
        """
        speed_bonus = 0
        if answer_time < self.FAST_ANSWER_THRESHOLD:
            speed_bonus = int(
                self.MAX_SPEED_BONUS * (1 - answer_time / self.FAST_ANSWER_THRESHOLD)
            )
        if answer_time < 3:
            self.fast_answers += 1

        points = self.BASE_POINTS + speed_bonus
        self.current_score += points
        self.correct_answers += 1
        self.total_answers += 1
        return points

    def record_wrong_answer(self):
        """Record an incorrect answer (no points awarded)."""
        self.total_answers += 1

    def accuracy(self) -> float:
        """Return the percentage of correct answers (0-100)."""
        if self.total_answers == 0:
            return 0.0
        return (self.correct_answers / self.total_answers) * 100

    def __str__(self) -> str:
        return (
            f"Player: {self.name} | Score: {self.current_score} | "
            f"Correct: {self.correct_answers}/{self.total_answers} "
            f"({self.accuracy():.0f}%)"
        )
