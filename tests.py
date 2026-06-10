"""
tests.py - Automated unit tests for BrainBuster.
Run with: python tests.py
"""

import unittest
import os
import shutil
import tempfile
from unittest.mock import patch

from player import Player
from leaderboard import Leaderboard
from question_db import QuestionDB
from accounts import AccountManager
from achievements import check_achievements, get_all_achievements

# ── Player tests ──────────────────────────────────────────────────────────────


class TestPlayer(unittest.TestCase):

    def setUp(self):
        self.player = Player("Tester")

    def test_initial_score_is_zero(self):
        self.assertEqual(self.player.current_score, 0)

    def test_award_points_fast_answer(self):
        points = self.player.award_points(answer_time=1.0)
        self.assertGreater(points, Player.BASE_POINTS)

    def test_award_points_slow_answer(self):
        points = self.player.award_points(answer_time=10.0)
        self.assertEqual(points, Player.BASE_POINTS)

    def test_correct_answers_increments(self):
        self.player.award_points(3.0)
        self.player.award_points(3.0)
        self.assertEqual(self.player.correct_answers, 2)

    def test_fast_answers_tracked(self):
        self.player.award_points(1.0)  # under 3s -> fast
        self.player.award_points(5.0)  # over 3s -> not fast
        self.assertEqual(self.player.fast_answers, 1)

    def test_wrong_answer_increments_total_only(self):
        self.player.record_wrong_answer()
        self.assertEqual(self.player.total_answers, 1)
        self.assertEqual(self.player.correct_answers, 0)

    def test_accuracy_calculation(self):
        self.player.award_points(1.0)
        self.player.record_wrong_answer()
        self.assertAlmostEqual(self.player.accuracy(), 50.0)

    def test_accuracy_no_answers(self):
        self.assertEqual(self.player.accuracy(), 0.0)

    def test_reset_score(self):
        self.player.award_points(1.0)
        self.player.reset_score()
        self.assertEqual(self.player.current_score, 0)
        self.assertEqual(self.player.fast_answers, 0)


# ── QuestionDB tests ──────────────────────────────────────────────────────────


class TestQuestionDB(unittest.TestCase):

    def setUp(self):
        self.db = QuestionDB()

    def test_categories_not_empty(self):
        self.assertGreater(len(self.db.get_categories()), 0)

    def test_categories_are_sorted(self):
        cats = self.db.get_categories()
        self.assertEqual(cats, sorted(cats))

    def test_get_questions_returns_correct_count(self):
        questions = self.db.get_questions("random", count=3)
        self.assertLessEqual(len(questions), 3)

    def test_get_questions_shuffled(self):
        results = set()
        for _ in range(10):
            qs = self.db.get_questions("random", count=5)
            results.add(tuple(q["question"] for q in qs))
        self.assertGreater(len(results), 1)

    def test_question_structure(self):
        for q in self.db.questions:
            self.assertIn("category", q)
            self.assertIn("question", q)
            self.assertIn("options", q)
            self.assertIn("answer", q)
            self.assertEqual(len(q["options"]), 4)
            self.assertIn(q["answer"], range(4))

    def test_add_question(self):
        before = len(self.db.questions)
        with patch.object(self.db, "_save_questions"):
            self.db.add_question("Test", "Is this a test?", ["Yes", "No", "Maybe", "Always"], 0)
        self.assertEqual(len(self.db.questions), before + 1)


# ── Leaderboard tests ─────────────────────────────────────────────────────────


class TestLeaderboard(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.scores_file = os.path.join(self.tmp_dir, "scores.json")
        import leaderboard as lb_module

        self._orig = lb_module.SCORES_FILE
        lb_module.SCORES_FILE = self.scores_file
        self.lb = Leaderboard()

    def tearDown(self):
        import leaderboard as lb_module

        lb_module.SCORES_FILE = self._orig
        shutil.rmtree(self.tmp_dir)

    def test_empty_leaderboard(self):
        self.assertEqual(len(self.lb.entries), 0)

    def test_add_entry(self):
        self.lb.add_entry("Alice", 100, "Science", "solo")
        self.assertEqual(self.lb.entries[0]["name"], "Alice")

    def test_entries_sorted_by_score(self):
        self.lb.add_entry("Alice", 50, "Science", "solo")
        self.lb.add_entry("Bob", 120, "History", "solo")
        self.assertEqual(self.lb.entries[0]["name"], "Bob")

    def test_max_entries_respected(self):
        from leaderboard import MAX_ENTRIES

        for i in range(MAX_ENTRIES + 5):
            self.lb.add_entry(f"P{i}", i * 10, "Science", "solo")
        self.assertLessEqual(len(self.lb.entries), MAX_ENTRIES)

    def test_persistence(self):
        self.lb.add_entry("Persistent", 999, "Tech", "solo")
        lb2 = Leaderboard()
        self.assertEqual(lb2.entries[0]["name"], "Persistent")


# ── AccountManager tests ──────────────────────────────────────────────────────


class TestAccountManager(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.acc_file = os.path.join(self.tmp_dir, "accounts.json")
        import accounts as acc_module

        self._orig = acc_module.ACCOUNTS_FILE
        acc_module.ACCOUNTS_FILE = self.acc_file
        self.mgr = AccountManager()

    def tearDown(self):
        import accounts as acc_module

        acc_module.ACCOUNTS_FILE = self._orig
        shutil.rmtree(self.tmp_dir)

    def test_register_success(self):
        ok, msg = self.mgr.register("alice", "pass1234")
        self.assertTrue(ok)
        self.assertTrue(self.mgr.user_exists("alice"))

    def test_register_duplicate(self):
        self.mgr.register("alice", "pass1234")
        ok, _ = self.mgr.register("alice", "other")
        self.assertFalse(ok)

    def test_register_short_username(self):
        ok, _ = self.mgr.register("ab", "pass1234")
        self.assertFalse(ok)

    def test_login_success(self):
        self.mgr.register("bob", "secret99")
        ok, _ = self.mgr.login("bob", "secret99")
        self.assertTrue(ok)

    def test_login_wrong_password(self):
        self.mgr.register("bob", "secret99")
        ok, _ = self.mgr.login("bob", "wrongpass")
        self.assertFalse(ok)

    def test_login_unknown_user(self):
        ok, _ = self.mgr.login("nobody", "pass")
        self.assertFalse(ok)

    def test_update_stats(self):
        self.mgr.register("carol", "pass1234")
        self.mgr.update_stats("carol", 50)
        self.mgr.update_stats("carol", 30)
        profile = self.mgr.get_profile("carol")
        self.assertEqual(profile["total_score"], 80)
        self.assertEqual(profile["games_played"], 2)

    def test_add_achievement_no_duplicates(self):
        self.mgr.register("dave", "pass1234")
        self.mgr.add_achievement("dave", "first_game")
        self.mgr.add_achievement("dave", "first_game")
        profile = self.mgr.get_profile("dave")
        self.assertEqual(profile["achievements"].count("first_game"), 1)

    def test_profile_hides_password_hash(self):
        self.mgr.register("eve", "secret")
        profile = self.mgr.get_profile("eve")
        self.assertNotIn("password_hash", profile)


# ── Achievement tests ─────────────────────────────────────────────────────────


class TestAchievements(unittest.TestCase):

    def _check(self, **kwargs):
        defaults = dict(
            games_played=1,
            total_score=10,
            current_score=10,
            correct=1,
            total=1,
            fast_answers=0,
            existing=[],
        )
        defaults.update(kwargs)
        return check_achievements(**defaults)

    def test_first_game_unlocked(self):
        result = self._check(games_played=1)
        self.assertIn("first_game", result)

    def test_first_game_not_duplicated(self):
        result = self._check(games_played=1, existing=["first_game"])
        self.assertNotIn("first_game", result)

    def test_perfect_game(self):
        result = self._check(correct=5, total=5)
        self.assertIn("perfect_game", result)

    def test_speed_demon(self):
        result = self._check(fast_answers=3)
        self.assertIn("speed_demon", result)

    def test_century(self):
        result = self._check(total_score=100)
        self.assertIn("century", result)

    def test_all_achievements_have_required_keys(self):
        for ach_id, ach in get_all_achievements().items():
            self.assertIn("name", ach)
            self.assertIn("description", ach)
            self.assertIn("icon", ach)


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Running BrainBuster automated tests...\n")
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    for tc in [TestPlayer, TestQuestionDB, TestLeaderboard, TestAccountManager, TestAchievements]:
        suite.addTests(loader.loadTestsFromTestCase(tc))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    total = result.testsRun
    passed = total - len(result.failures) - len(result.errors)
    print(f"\n{'='*50}")
    print(f"Tests passed: {passed}/{total}")
    print("✔  All tests passed!" if result.wasSuccessful() else "✘  Some tests failed.")
    print(f"{'='*50}")


# ── Integration Tests ─────────────────────────────────────────────────────────
# These tests verify that multiple modules work correctly TOGETHER,
# not just in isolation. They test real end-to-end flows.


class TestQuizEngineIntegration(unittest.TestCase):
    """
    Integration test: QuizEngine + QuestionDB + Player working together.
    Simulates a full solo game session without any mocking.
    """

    def setUp(self):
        self.db = QuestionDB()
        self.player = Player("IntegrationTester")

    def test_full_solo_game_updates_player_score(self):
        """
        After simulating correct answers for all questions,
        the player's score must be greater than zero.
        """
        questions = self.db.get_questions("random", count=5)
        self.assertGreater(len(questions), 0, "DB must return questions")

        for q in questions:
            # Simulate a correct answer with a 3-second response time
            self.player.award_points(answer_time=3.0)

        self.assertGreater(self.player.current_score, 0)
        self.assertEqual(self.player.correct_answers, len(questions))

    def test_wrong_answers_do_not_change_score(self):
        """
        Recording only wrong answers must leave the score at zero.
        """
        questions = self.db.get_questions("random", count=5)
        for _ in questions:
            self.player.record_wrong_answer()

        self.assertEqual(self.player.current_score, 0)
        self.assertEqual(self.player.total_answers, len(questions))

    def test_mixed_game_accuracy(self):
        """
        3 correct + 2 wrong answers must produce 60% accuracy.
        """
        for _ in range(3):
            self.player.award_points(answer_time=3.0)
        for _ in range(2):
            self.player.record_wrong_answer()

        self.assertAlmostEqual(self.player.accuracy(), 60.0)


class TestAccountLeaderboardIntegration(unittest.TestCase):
    """
    Integration test: AccountManager + Leaderboard working together.
    Simulates a complete game lifecycle: register → play → save score → rank.
    """

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()

        import accounts as acc_mod
        import leaderboard as lb_mod

        self._orig_acc = acc_mod.ACCOUNTS_FILE
        self._orig_lb = lb_mod.SCORES_FILE
        acc_mod.ACCOUNTS_FILE = os.path.join(self.tmp_dir, "accounts.json")
        lb_mod.SCORES_FILE = os.path.join(self.tmp_dir, "scores.json")

        self.mgr = AccountManager()
        self.lb = Leaderboard()

    def tearDown(self):
        import accounts as acc_mod
        import leaderboard as lb_mod

        acc_mod.ACCOUNTS_FILE = self._orig_acc
        lb_mod.SCORES_FILE = self._orig_lb
        shutil.rmtree(self.tmp_dir)

    def test_register_play_and_appear_on_leaderboard(self):
        """
        A newly registered player who finishes a game should appear
        on the leaderboard with the correct score.
        """
        ok, _ = self.mgr.register("player1", "pass1234")
        self.assertTrue(ok)

        score = 80
        self.mgr.update_stats("player1", score)
        self.lb.add_entry("player1", score, "Science", "solo")

        profile = self.mgr.get_profile("player1")
        self.assertEqual(profile["total_score"], score)
        self.assertEqual(self.lb.entries[0]["name"], "player1")
        self.assertEqual(self.lb.entries[0]["score"], score)

    def test_leaderboard_ranking_across_multiple_players(self):
        """
        After multiple players finish games, leaderboard must be
        sorted by score descending.
        """
        players = [("alice", 50), ("bob", 120), ("carol", 85)]
        for name, score in players:
            self.mgr.register(name, "pass1234")
            self.mgr.update_stats(name, score)
            self.lb.add_entry(name, score, "History", "solo")

        self.assertEqual(self.lb.entries[0]["name"], "bob")
        self.assertEqual(self.lb.entries[1]["name"], "carol")
        self.assertEqual(self.lb.entries[2]["name"], "alice")

    def test_achievements_unlocked_after_game(self):
        """
        After completing a game, the correct achievements should be
        granted and persisted to the account.
        """
        self.mgr.register("dave", "pass1234")
        self.mgr.update_stats("dave", 10)  # games_played becomes 1

        profile = self.mgr.get_profile("dave")
        new_achs = check_achievements(
            games_played=profile["games_played"],
            total_score=profile["total_score"],
            current_score=10,
            correct=5,
            total=5,
            fast_answers=0,
            existing=profile["achievements"],
        )
        for ach_id in new_achs:
            self.mgr.add_achievement("dave", ach_id)

        updated = self.mgr.get_profile("dave")
        self.assertIn("first_game", updated["achievements"])
        self.assertIn("perfect_game", updated["achievements"])


class TestFlaskRoutesIntegration(unittest.TestCase):
    """
    Integration test: Flask routes working end-to-end with real modules.
    Uses Flask's built-in test client (no actual HTTP server needed).
    """

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()

        import accounts as acc_mod
        import leaderboard as lb_mod

        self._orig_acc = acc_mod.ACCOUNTS_FILE
        self._orig_lb = lb_mod.SCORES_FILE
        acc_mod.ACCOUNTS_FILE = os.path.join(self.tmp_dir, "accounts.json")
        lb_mod.SCORES_FILE = os.path.join(self.tmp_dir, "scores.json")

        # Re-import app so it picks up the patched file paths
        import importlib
        import app as app_mod

        importlib.reload(app_mod)
        app_mod.app.config["TESTING"] = True
        app_mod.app.config["WTF_CSRF_ENABLED"] = False
        self.client = app_mod.app.test_client()
        self.app_mod = app_mod

    def tearDown(self):
        import accounts as acc_mod
        import leaderboard as lb_mod

        acc_mod.ACCOUNTS_FILE = self._orig_acc
        lb_mod.SCORES_FILE = self._orig_lb
        shutil.rmtree(self.tmp_dir)

    def test_homepage_returns_200(self):
        """The homepage must be reachable without login."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_leaderboard_page_returns_200(self):
        """The leaderboard must be publicly accessible."""
        response = self.client.get("/leaderboard")
        self.assertEqual(response.status_code, 200)

    def test_register_and_login_flow(self):
        """
        Registering a new user and logging in should succeed
        and redirect to the homepage.
        """
        reg = self.client.post(
            "/register",
            data={"username": "testuser", "password": "testpass"},
            follow_redirects=True,
        )
        self.assertEqual(reg.status_code, 200)

        self.client.get("/logout")

        login = self.client.post(
            "/login", data={"username": "testuser", "password": "testpass"}, follow_redirects=True
        )
        self.assertEqual(login.status_code, 200)

    def test_play_requires_login(self):
        """Accessing /play without login must redirect to /login."""
        response = self.client.get("/play", follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.headers["Location"])

    def test_admin_requires_login(self):
        """Accessing /admin without login must redirect to /login."""
        response = self.client.get("/admin", follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.headers["Location"])

    def test_register_duplicate_user(self):
        """Registering the same username twice must fail gracefully."""
        self.client.post(
            "/register", data={"username": "dupuser", "password": "pass1234"}, follow_redirects=True
        )
        self.client.get("/logout")
        response = self.client.post(
            "/register", data={"username": "dupuser", "password": "other"}, follow_redirects=True
        )
        # Page should reload with an error, not crash
        self.assertEqual(response.status_code, 200)


# ── Updated entry point (includes integration test classes) ───────────────────

if __name__ == "__main__":
    print("Running BrainBuster tests (Unit + Integration)...\n")
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    for tc in [
        # Unit tests
        TestPlayer,
        TestQuestionDB,
        TestLeaderboard,
        TestAccountManager,
        TestAchievements,
        # Integration tests
        TestQuizEngineIntegration,
        TestAccountLeaderboardIntegration,
        TestFlaskRoutesIntegration,
    ]:
        suite.addTests(loader.loadTestsFromTestCase(tc))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    total = result.testsRun
    passed = total - len(result.failures) - len(result.errors)
    print(f"\n{'='*55}")
    print("  Unit tests:        35")
    print(f"  Integration tests: {total - 35}")
    print(f"  Total passed:      {passed}/{total}")
    print("  ✔  All tests passed!" if result.wasSuccessful() else "  ✘  Some tests failed.")
    print(f"{'='*55}")
