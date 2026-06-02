"""
tests.py - Automated unit tests for BrainBuster.
Run with: python tests.py
"""

import unittest
import json
import os
import tempfile
import shutil
from unittest.mock import patch, MagicMock

# Modules under test
from player import Player
from leaderboard import Leaderboard
from question_db import QuestionDB


# ── Player tests ──────────────────────────────────────────────────────────────

class TestPlayer(unittest.TestCase):
    """Tests for the Player class."""

    def setUp(self):
        self.player = Player("Tester")

    def test_initial_score_is_zero(self):
        """A new player starts with a score of zero."""
        self.assertEqual(self.player.current_score, 0)

    def test_award_points_fast_answer(self):
        """A very fast answer should earn base points plus a speed bonus."""
        points = self.player.award_points(answer_time=1.0)
        self.assertGreater(points, Player.BASE_POINTS)
        self.assertEqual(self.player.current_score, points)

    def test_award_points_slow_answer(self):
        """A slow answer (above threshold) should earn only base points."""
        points = self.player.award_points(answer_time=10.0)
        self.assertEqual(points, Player.BASE_POINTS)

    def test_correct_answers_increments(self):
        """Awarding points should increment the correct-answer counter."""
        self.player.award_points(answer_time=3.0)
        self.player.award_points(answer_time=3.0)
        self.assertEqual(self.player.correct_answers, 2)

    def test_wrong_answer_increments_total_only(self):
        """Recording a wrong answer increases total but not correct counter."""
        self.player.record_wrong_answer()
        self.assertEqual(self.player.total_answers, 1)
        self.assertEqual(self.player.correct_answers, 0)

    def test_accuracy_calculation(self):
        """Accuracy should reflect correct vs total answers."""
        self.player.award_points(1.0)   # correct
        self.player.record_wrong_answer()  # wrong
        self.assertAlmostEqual(self.player.accuracy(), 50.0)

    def test_accuracy_no_answers(self):
        """Accuracy should be 0 when no questions have been answered."""
        self.assertEqual(self.player.accuracy(), 0.0)

    def test_reset_score(self):
        """reset_score should clear all stats."""
        self.player.award_points(1.0)
        self.player.reset_score()
        self.assertEqual(self.player.current_score, 0)
        self.assertEqual(self.player.correct_answers, 0)
        self.assertEqual(self.player.total_answers, 0)


# ── QuestionDB tests ──────────────────────────────────────────────────────────

class TestQuestionDB(unittest.TestCase):
    """Tests for the QuestionDB class."""

    def setUp(self):
        # Use the built-in fallback questions (no file needed)
        self.db = QuestionDB()

    def test_categories_not_empty(self):
        """At least one category should be available."""
        self.assertGreater(len(self.db.get_categories()), 0)

    def test_categories_are_sorted(self):
        """Categories should be returned in alphabetical order."""
        cats = self.db.get_categories()
        self.assertEqual(cats, sorted(cats))

    def test_get_questions_returns_correct_count(self):
        """get_questions with a count limit should respect that limit."""
        questions = self.db.get_questions("random", count=3)
        self.assertLessEqual(len(questions), 3)

    def test_get_questions_shuffled(self):
        """Two calls should not always return the same order (probabilistic)."""
        results = set()
        for _ in range(10):
            qs = self.db.get_questions("random", count=5)
            results.add(tuple(q["question"] for q in qs))
        # At least two different orderings should appear in 10 draws
        self.assertGreater(len(results), 1)

    def test_question_structure(self):
        """Each question must have the required fields."""
        for q in self.db.questions:
            self.assertIn("category", q)
            self.assertIn("question", q)
            self.assertIn("options", q)
            self.assertIn("answer", q)
            self.assertEqual(len(q["options"]), 4)
            self.assertIn(q["answer"], range(4))

    def test_add_question(self):
        """Adding a question should increase the total count."""
        before = len(self.db.questions)
        # Patch _save_questions so we don't write to disk
        with patch.object(self.db, "_save_questions"):
            self.db.add_question(
                category="Test",
                question="Is this a test?",
                options=["Yes", "No", "Maybe", "Always"],
                answer=0,
            )
        self.assertEqual(len(self.db.questions), before + 1)


# ── Leaderboard tests ─────────────────────────────────────────────────────────

class TestLeaderboard(unittest.TestCase):
    """Tests for the Leaderboard class."""

    def setUp(self):
        # Use a temporary directory so tests don't touch real data
        self.tmp_dir = tempfile.mkdtemp()
        self.scores_file = os.path.join(self.tmp_dir, "scores.json")

        import leaderboard as lb_module
        self._original_file = lb_module.SCORES_FILE
        lb_module.SCORES_FILE = self.scores_file

        self.lb = Leaderboard()

    def tearDown(self):
        import leaderboard as lb_module
        lb_module.SCORES_FILE = self._original_file
        shutil.rmtree(self.tmp_dir)

    def test_empty_leaderboard(self):
        """A fresh leaderboard should have no entries."""
        self.assertEqual(len(self.lb.entries), 0)

    def test_add_entry(self):
        """Adding an entry should be reflected in the leaderboard."""
        self.lb.add_entry("Alice", 100, "Science", "solo")
        self.assertEqual(len(self.lb.entries), 1)
        self.assertEqual(self.lb.entries[0]["name"], "Alice")

    def test_entries_sorted_by_score(self):
        """Entries should be sorted highest score first."""
        self.lb.add_entry("Alice", 50, "Science", "solo")
        self.lb.add_entry("Bob", 120, "History", "solo")
        self.lb.add_entry("Carol", 80, "Geography", "time_attack")
        self.assertEqual(self.lb.entries[0]["name"], "Bob")
        self.assertEqual(self.lb.entries[1]["name"], "Carol")

    def test_max_entries_respected(self):
        """Leaderboard should not exceed MAX_ENTRIES."""
        from leaderboard import MAX_ENTRIES
        for i in range(MAX_ENTRIES + 5):
            self.lb.add_entry(f"Player{i}", i * 10, "Science", "solo")
        self.assertLessEqual(len(self.lb.entries), MAX_ENTRIES)

    def test_persistence(self):
        """Scores should be saved to disk and reloadable."""
        self.lb.add_entry("Persistent", 999, "Technology", "solo")

        # Load a fresh leaderboard from the same file
        lb2 = Leaderboard()
        self.assertEqual(lb2.entries[0]["name"], "Persistent")
        self.assertEqual(lb2.entries[0]["score"], 999)


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Running BrainBuster automated tests...\n")
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(TestPlayer))
    suite.addTests(loader.loadTestsFromTestCase(TestQuestionDB))
    suite.addTests(loader.loadTestsFromTestCase(TestLeaderboard))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    total = result.testsRun
    passed = total - len(result.failures) - len(result.errors)
    print(f"\n{'='*50}")
    print(f"Tests passed: {passed}/{total}")
    if result.wasSuccessful():
        print("✔  All tests passed!")
    else:
        print("✘  Some tests failed.")
    print(f"{'='*50}")
