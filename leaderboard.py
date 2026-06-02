"""
Leaderboard - persists and displays high scores across sessions.
"""

import json
import os
from datetime import datetime
from typing import Optional

SCORES_FILE = os.path.join(os.path.dirname(__file__), "data", "scores.json")
MAX_ENTRIES = 10  # Top entries to keep


class Leaderboard:
    """Stores and displays the global high-score leaderboard."""

    def __init__(self):
        self.entries = self._load()

    def _load(self) -> list:
        """Load scores from file, returning an empty list on failure."""
        if os.path.exists(SCORES_FILE):
            try:
                with open(SCORES_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return []

    def _save(self):
        """Persist the current leaderboard to disk."""
        os.makedirs(os.path.dirname(SCORES_FILE), exist_ok=True)
        with open(SCORES_FILE, "w", encoding="utf-8") as f:
            json.dump(self.entries, f, indent=2, ensure_ascii=False)

    def add_entry(self, name: str, score: int, category: str, mode: str):
        """Add a new score entry and keep only the top MAX_ENTRIES."""
        entry = {
            "name": name,
            "score": score,
            "category": category,
            "mode": mode,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
        self.entries.append(entry)
        # Sort descending by score
        self.entries.sort(key=lambda e: e["score"], reverse=True)
        self.entries = self.entries[:MAX_ENTRIES]
        self._save()

    def display(self, filter_mode: Optional[str] = None):
        """Print the leaderboard table to the console."""
        entries = self.entries
        if filter_mode:
            entries = [e for e in entries if e["mode"] == filter_mode]

        print("\n" + "═" * 60)
        print("  🏆  LEADERBOARD  🏆")
        print("═" * 60)

        if not entries:
            print("  No scores yet. Be the first!")
        else:
            print(f"  {'Rank':<5} {'Name':<15} {'Score':<8} {'Category':<15} {'Date'}")
            print("  " + "-" * 56)
            for rank, entry in enumerate(entries, 1):
                print(
                    f"  {rank:<5} {entry['name']:<15} {entry['score']:<8} "
                    f"{entry['category']:<15} {entry['date']}"
                )

        print("═" * 60)
