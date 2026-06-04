"""
achievements.py - Achievement system for BrainBuster.
Defines all achievements and checks which ones a player has earned.
"""

from typing import Optional

# All available achievements: id -> { name, description, icon }
ACHIEVEMENTS = {
    "first_game": {
        "name": "First Steps",
        "description": "Complete your first game.",
        "icon": "🎮",
    },
    "perfect_game": {
        "name": "Perfect Mind",
        "description": "Answer all questions correctly in a game.",
        "icon": "🏆",
    },
    "speed_demon": {
        "name": "Speed Demon",
        "description": "Answer 3 questions in under 3 seconds each.",
        "icon": "⚡",
    },
    "century": {
        "name": "Century",
        "description": "Reach a total score of 100 points.",
        "icon": "💯",
    },
    "scholar": {
        "name": "Scholar",
        "description": "Reach a total score of 500 points.",
        "icon": "🎓",
    },
    "veteran": {
        "name": "Veteran",
        "description": "Play 10 games.",
        "icon": "🎖️",
    },
    "quiz_master": {
        "name": "Quiz Master",
        "description": "Score 80% accuracy in a game with at least 5 questions.",
        "icon": "🧠",
    },
}


def check_achievements(
    games_played: int,
    total_score: int,
    current_score: int,
    correct: int,
    total: int,
    fast_answers: int,
    existing: list,
) -> list:
    """
    Evaluate which new achievements the player has earned.
    Returns a list of newly unlocked achievement IDs.
    """
    newly_unlocked = []

    def unlock(achievement_id: str):
        if achievement_id not in existing and achievement_id not in newly_unlocked:
            newly_unlocked.append(achievement_id)

    if games_played >= 1:
        unlock("first_game")

    if total > 0 and correct == total:
        unlock("perfect_game")

    if fast_answers >= 3:
        unlock("speed_demon")

    if total_score >= 100:
        unlock("century")

    if total_score >= 500:
        unlock("scholar")

    if games_played >= 10:
        unlock("veteran")

    accuracy = (correct / total * 100) if total >= 5 else 0
    if accuracy >= 80:
        unlock("quiz_master")

    return newly_unlocked


def get_achievement_details(achievement_id: str) -> Optional[dict]:
    """Return the full details dict for a given achievement ID."""
    return ACHIEVEMENTS.get(achievement_id)


def get_all_achievements() -> dict:
    """Return the full achievements catalogue."""
    return ACHIEVEMENTS
