#!/usr/bin/env python3
"""
BrainBuster - A console-based quiz game
Usage: python main.py [h]
  h  - Show help/controls
"""

import sys
import time

from quiz_engine import QuizEngine
from leaderboard import Leaderboard
from question_db import QuestionDB
from player import Player

HELP_TEXT = """
╔══════════════════════════════════════════════════════╗
║            BrainBuster - Help & Controls             ║
╠══════════════════════════════════════════════════════╣
║  Start game:    python main.py                       ║
║  Show help:     python main.py h                     ║
╠══════════════════════════════════════════════════════╣
║  In-game controls:                                   ║
║    1-4         Answer a question (A/B/C/D)           ║
║    h           Show this help during the game        ║
║    q           Quit current game                     ║
╠══════════════════════════════════════════════════════╣
║  Scoring:                                            ║
║    Correct answer:    +10 points                     ║
║    Speed bonus:       up to +5 points (fast answer)  ║
║    Wrong answer:      0 points                       ║
╚══════════════════════════════════════════════════════╝
"""


def show_help():
    """Display help text."""
    print(HELP_TEXT)


def show_banner():
    """Display the game banner."""
    print("""
██████╗ ██████╗  █████╗ ██╗███╗   ██╗    ██████╗ ██╗   ██╗███████╗████████╗███████╗██████╗
██╔══██╗██╔══██╗██╔══██╗██║████╗  ██║    ██╔══██╗██║   ██║██╔════╝╚══██╔══╝██╔════╝██╔══██╗
██████╔╝██████╔╝███████║██║██╔██╗ ██║    ██████╔╝██║   ██║███████╗   ██║   █████╗  ██████╔╝
██╔══██╗██╔══██╗██╔══██║██║██║╚██╗██║    ██╔══██╗██║   ██║╚════██║   ██║   ██╔══╝  ██╔══██╗
██████╔╝██║  ██║██║  ██║██║██║ ╚████║    ██████╔╝╚██████╔╝███████║   ██║   ███████╗██║  ██║
╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝    ╚═════╝  ╚═════╝ ╚══════╝   ╚═╝   ╚══════╝╚═╝  ╚═╝
    """)
    print("              Test your knowledge. Challenge your friends.\n")


def get_player_name() -> str:
    """Prompt the player for their name."""
    while True:
        try:
            name = input("Enter your name (or press Enter for 'Anonymous'): ").strip()
        except KeyboardInterrupt:
            print("\n\nGoodbye!\n")
            sys.exit(0)
        if not name:
            return "Anonymous"
        if len(name) <= 20:
            return name
        print("Name must be 20 characters or less. Try again.")


def select_category(db: QuestionDB) -> str:
    """Let the player choose a quiz category."""
    categories = db.get_categories()
    print("\n── Available Categories ──")
    for i, cat in enumerate(categories, 1):
        count = db.get_question_count(cat)
        print(f"  {i}. {cat} ({count} questions)")
    print("  0. Random (mixed categories)")

    while True:
        try:
            choice = input("\nSelect a category (0 to mix): ").strip()
        except KeyboardInterrupt:
            print("\n\nReturning to menu.\n")
            return None
        if choice == "0":
            return "random"
        if choice.isdigit() and 1 <= int(choice) <= len(categories):
            return categories[int(choice) - 1]
        print("Invalid choice. Please try again.")


def select_game_mode() -> str:
    """Let the player choose single player or vs. time mode."""
    print("\n── Game Mode ──")
    print("  1. Solo (answer 10 questions)")
    print("  2. Time Attack (as many as possible in 60 seconds)")

    while True:
        try:
            choice = input("\nSelect mode: ").strip()
        except KeyboardInterrupt:
            print("\n\nReturning to menu.\n")
            return None
        if choice == "1":
            return "solo"
        if choice == "2":
            return "time_attack"
        print("Please enter 1 or 2.")


def play_game(player: Player, db: QuestionDB, leaderboard: Leaderboard):
    """Run a full game session."""
    category = select_category(db)
    if category is None:
        return  # Ctrl+C während Kategorienwahl

    mode = select_game_mode()
    if mode is None:
        return  # Ctrl+C während Modusauswahl

    print(f"\nGet ready, {player.name}! Starting in 3...")
    for i in (2, 1):
        time.sleep(0.6)
        print(f"{i}...")
    time.sleep(0.6)
    print("GO!\n")

    engine = QuizEngine(db, player, mode, category)
    engine.run()

    final_score = player.current_score
    leaderboard.add_entry(player.name, final_score, category, mode)
    leaderboard.display()


def main():
    """Entry point for BrainBuster."""
    # Handle 'h' argument for help
    if len(sys.argv) > 1 and sys.argv[1].lower() == "h":
        show_help()
        return

    show_banner()

    db = QuestionDB()
    leaderboard = Leaderboard()

    print("Type 'h' at any prompt for help.\n")

    player_name = get_player_name()
    player = Player(player_name)

    while True:
        print(f"\n── Main Menu ── (Hi, {player.name}!)")
        print("  1. Play")
        print("  2. View Leaderboard")
        print("  3. Help")
        print("  4. Quit")

        try:
            choice = input("\nYour choice: ").strip().lower()
        except KeyboardInterrupt:
            print("\n\nThanks for playing BrainBuster! Goodbye!\n")
            break

        if choice == "h" or choice == "3":
            show_help()
        elif choice == "1":
            player.reset_score()
            play_game(player, db, leaderboard)
        elif choice == "2":
            leaderboard.display()
        elif choice == "4" or choice == "q":
            print("\nThanks for playing BrainBuster! Goodbye!\n")
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
