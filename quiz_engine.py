"""
Quiz engine - drives the question/answer game loop for both
'solo' (fixed 10 questions) and 'time_attack' (60-second sprint) modes.
"""

import time
import sys
from player import Player
from question_db import QuestionDB

OPTION_LABELS = ["A", "B", "C", "D"]
SOLO_QUESTION_COUNT = 10
TIME_ATTACK_DURATION = 60  # seconds


class QuizEngine:
    """Runs a quiz session for a given player, mode, and category."""

    def __init__(self, db: QuestionDB, player: Player, mode: str, category: str):
        self.db = db
        self.player = player
        self.mode = mode
        self.category = category

    def run(self):
        """Start and manage the game loop based on the selected mode."""
        if self.mode == "solo":
            self._run_solo()
        elif self.mode == "time_attack":
            self._run_time_attack()

        self._show_game_summary()

    # ── Solo mode ────────────────────────────────────────────────────────────

    def _run_solo(self):
        """Play through a fixed set of questions."""
        questions = self.db.get_questions(self.category, count=SOLO_QUESTION_COUNT)

        if not questions:
            print("No questions found for this category. Returning to menu.")
            return

        for idx, question in enumerate(questions, 1):
            print(f"\n── Question {idx}/{len(questions)} ──")
            self._ask_question(question)

    # ── Time attack mode ─────────────────────────────────────────────────────

    def _run_time_attack(self):
        """Keep asking questions until time runs out."""
        questions = self.db.get_questions(self.category)
        # Loop questions if needed
        question_pool = questions * 10
        deadline = time.time() + TIME_ATTACK_DURATION

        print(f"\nYou have {TIME_ATTACK_DURATION} seconds. Go!\n")

        for idx, question in enumerate(question_pool, 1):
            remaining = deadline - time.time()
            if remaining <= 0:
                break
            print(f"\n── Question {idx} | ⏱  {remaining:.0f}s remaining ──")
            answered = self._ask_question(question, time_limit=remaining)
            if not answered:
                break  # Time ran out during the question

        print("\n⏰  Time's up!")

    # ── Core question logic ───────────────────────────────────────────────────

    def _ask_question(self, question: dict, time_limit: float = None) -> bool:
        """
        Display a question and handle the player's answer.
        Returns True if the question was answered, False if time ran out.
        """
        import html

        # Decode HTML entities (questions from Open Trivia DB contain them)
        q_text = html.unescape(question["question"])
        options = [html.unescape(opt) for opt in question["options"]]
        correct_index = question["answer"]

        print(f"\n{q_text}\n")
        for i, opt in enumerate(options):
            print(f"  {OPTION_LABELS[i]}. {opt}")

        start_time = time.time()
        answer = self._get_answer(time_limit)
        elapsed = time.time() - start_time

        if answer is None:
            # Timed out or user quit
            return False

        if answer == "q":
            print("\nQuitting current game...")
            sys.exit(0)

        if answer == "h":
            from main import show_help
            show_help()
            # Re-ask the same question (no time penalty for help)
            return self._ask_question(question, time_limit)

        chosen_index = OPTION_LABELS.index(answer.upper())

        if chosen_index == correct_index:
            points = self.player.award_points(elapsed)
            speed_info = " ⚡ Speed bonus!" if elapsed < 5 else ""
            print(f"  ✔  Correct! +{points} points{speed_info}")
        else:
            self.player.record_wrong_answer()
            correct_label = OPTION_LABELS[correct_index]
            print(f"  ✘  Wrong! Correct answer: {correct_label}. {options[correct_index]}")

        print(f"  Score: {self.player.current_score}")
        return True

    def _get_answer(self, time_limit: float = None) -> str:
        """
        Prompt for input. Returns 'A'-'D', 'h', or 'q'.
        Returns None if time runs out.
        """
        valid_choices = set(["a", "b", "c", "d", "1", "2", "3", "4", "h", "q"])
        number_map = {"1": "a", "2": "b", "3": "c", "4": "d"}

        prompt = "\nYour answer (A/B/C/D, h=help, q=quit): "

        while True:
            # Check remaining time
            answer = input(prompt).strip().lower()

            if not answer:
                continue

            if answer in valid_choices:
                return number_map.get(answer, answer)

            print("  Invalid input. Please enter A, B, C, D (or 1-4).")

    # ── Summary ───────────────────────────────────────────────────────────────

    def _show_game_summary(self):
        """Display a summary of the player's performance."""
        p = self.player
        print("\n" + "═" * 50)
        print("  GAME OVER")
        print("═" * 50)
        print(f"  Player   : {p.name}")
        print(f"  Score    : {p.current_score}")
        print(f"  Correct  : {p.correct_answers} / {p.total_answers}")
        print(f"  Accuracy : {p.accuracy():.0f}%")
        print("═" * 50)
