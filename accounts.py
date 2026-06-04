"""
accounts.py - User account management with registration, login and profiles.
Passwords are stored as SHA-256 hashes (no plaintext).
"""

import json
import os
import hashlib
from datetime import datetime
from typing import Optional

ACCOUNTS_FILE = os.path.join(os.path.dirname(__file__), "data", "accounts.json")


def _hash_password(password: str) -> str:
    """Return a SHA-256 hex digest of the given password."""
    return hashlib.sha256(password.encode()).hexdigest()


class AccountManager:
    """Manages player accounts: registration, login, profile updates."""

    def __init__(self):
        self.accounts = self._load()

    def _load(self) -> dict:
        """Load accounts from disk, returning empty dict on failure."""
        if os.path.exists(ACCOUNTS_FILE):
            try:
                with open(ACCOUNTS_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return {}

    def _save(self):
        """Persist all accounts to disk."""
        os.makedirs(os.path.dirname(ACCOUNTS_FILE), exist_ok=True)
        with open(ACCOUNTS_FILE, "w", encoding="utf-8") as f:
            json.dump(self.accounts, f, indent=2, ensure_ascii=False)

    def register(self, username: str, password: str) -> tuple[bool, str]:
        """
        Register a new user.
        Returns (success: bool, message: str).
        """
        username = username.strip()
        if not username or not password:
            return False, "Username and password are required."
        if len(username) < 3:
            return False, "Username must be at least 3 characters."
        if len(password) < 4:
            return False, "Password must be at least 4 characters."
        if username in self.accounts:
            return False, "Username already taken."

        self.accounts[username] = {
            "password_hash": _hash_password(password),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "total_score": 0,
            "games_played": 0,
            "achievements": [],
        }
        self._save()
        return True, "Account created successfully."

    def login(self, username: str, password: str) -> tuple[bool, str]:
        """
        Validate login credentials.
        Returns (success: bool, message: str).
        """
        if username not in self.accounts:
            return False, "Unknown username."
        if self.accounts[username]["password_hash"] != _hash_password(password):
            return False, "Wrong password."
        return True, "Login successful."

    def get_profile(self, username: str) -> Optional[dict]:
        """Return a copy of the user's profile, or None if not found."""
        if username not in self.accounts:
            return None
        profile = dict(self.accounts[username])
        profile.pop("password_hash", None)  # never expose the hash
        profile["username"] = username
        return profile

    def update_stats(self, username: str, score: int):
        """Add score and increment games_played for a user after a game."""
        if username not in self.accounts:
            return
        self.accounts[username]["total_score"] += score
        self.accounts[username]["games_played"] += 1
        self._save()

    def add_achievement(self, username: str, achievement_id: str):
        """Grant an achievement to a user (no duplicates)."""
        if username not in self.accounts:
            return
        if achievement_id not in self.accounts[username]["achievements"]:
            self.accounts[username]["achievements"].append(achievement_id)
            self._save()

    def user_exists(self, username: str) -> bool:
        return username in self.accounts
