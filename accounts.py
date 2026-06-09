"""
accounts.py – Benutzerverwaltung für BrainBuster

Verantwortlich für Registrierung, Login und Profilpflege.
Konten werden als JSON-Datei auf der Festplatte gespeichert.

Sicherheitshinweise:
  - Passwörter werden niemals im Klartext gespeichert, sondern als
    SHA-256-Hash. Das bedeutet: Selbst wenn jemand Zugriff auf
    accounts.json erhält, kann er die echten Passwörter nicht lesen.
  - Das Profil, das an andere Module weitergegeben wird, enthält
    niemals den Passwort-Hash (get_profile() entfernt ihn aktiv).

Warum JSON statt einer echten Datenbank?
  Für diesen Prototyp reicht JSON aus. Es braucht keine Installation
  (kein PostgreSQL, SQLite-Setup etc.) und ist direkt lesbar.
  In einer Produktionsversion würde man auf SQLite oder PostgreSQL
  wechseln und bcrypt für das Password-Hashing verwenden.
"""

import json
import os
import hashlib
from datetime import datetime
from typing import Optional

# Pfad zur Datendatei – liegt im data/-Unterordner neben dieser Datei
ACCOUNTS_FILE = os.path.join(os.path.dirname(__file__), "data", "accounts.json")


def _hash_password(password: str) -> str:
    """
    Gibt den SHA-256-Hash eines Passworts als Hex-String zurück.

    SHA-256 wurde gewählt, weil er in der Python-Standardbibliothek
    verfügbar ist (kein extra Paket nötig) und für diesen Prototyp
    ausreichend sicher ist. In Produktion würde man bcrypt bevorzugen,
    da es absichtlich langsam ist und Brute-Force-Angriffe erschwert.

    Args:
        password: Klartext-Passwort vom Nutzer

    Returns:
        64-stelliger Hex-String (SHA-256-Digest)
    """
    return hashlib.sha256(password.encode()).hexdigest()


class AccountManager:
    """
    Verwaltet alle Benutzerkonten: Anlegen, Einloggen, Statistiken aktualisieren.

    Datenstruktur in accounts.json:
    {
      "benutzername": {
        "password_hash": "sha256-hex-string",
        "created_at":    "2025-01-01 12:00",
        "total_score":   150,
        "games_played":  5,
        "achievements":  ["first_game", "century"]
      }
    }
    """

    def __init__(self):
        """Lädt bestehende Konten beim Start aus der JSON-Datei."""
        self.accounts = self._load()

    def _load(self) -> dict:
        """
        Liest die Kontodaten von der Festplatte.
        Gibt ein leeres Dictionary zurück, falls die Datei fehlt oder beschädigt ist.
        So startet das Spiel auch ohne vorhandene Datei problemlos.
        """
        if os.path.exists(ACCOUNTS_FILE):
            try:
                with open(ACCOUNTS_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                # Beschädigte Datei → frisch starten statt abstürzen
                pass
        return {}

    def _save(self):
        """
        Schreibt alle Konten auf die Festplatte.
        os.makedirs stellt sicher, dass das data/-Verzeichnis existiert,
        auch beim ersten Start der Anwendung.
        """
        os.makedirs(os.path.dirname(ACCOUNTS_FILE), exist_ok=True)
        with open(ACCOUNTS_FILE, "w", encoding="utf-8") as f:
            json.dump(self.accounts, f, indent=2, ensure_ascii=False)

    def register(self, username: str, password: str) -> tuple[bool, str]:
        """
        Legt ein neues Benutzerkonto an.

        Validierungsregeln:
          - Benutzername: mind. 3 Zeichen, darf noch nicht existieren
          - Passwort: mind. 4 Zeichen

        Args:
            username: Gewünschter Benutzername (wird getrimmt)
            password: Gewünschtes Passwort im Klartext

        Returns:
            (True, Erfolgsmeldung) oder (False, Fehlermeldung)
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

        # Neues Konto anlegen – Passwort wird sofort gehasht, niemals im Klartext speichern
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
        Überprüft Benutzername und Passwort.

        Das eingegebene Passwort wird gehasht und mit dem gespeicherten
        Hash verglichen – so muss der Hash nie entschlüsselt werden.

        Args:
            username: Benutzername
            password: Eingegebenes Passwort im Klartext

        Returns:
            (True, Erfolgsmeldung) oder (False, Fehlermeldung)
        """
        if username not in self.accounts:
            return False, "Unknown username."
        if self.accounts[username]["password_hash"] != _hash_password(password):
            return False, "Wrong password."
        return True, "Login successful."

    def get_profile(self, username: str) -> Optional[dict]:
        """
        Gibt eine Kopie des Benutzerprofils zurück – ohne den Passwort-Hash.

        Der Hash wird aktiv entfernt, damit er niemals versehentlich an
        Templates oder andere Module weitergegeben wird.

        Args:
            username: Benutzername

        Returns:
            Dict mit Profildaten (inkl. 'username'-Schlüssel) oder None
        """
        if username not in self.accounts:
            return None
        profile = dict(self.accounts[username])
        profile.pop("password_hash", None)  # Hash nie nach außen geben
        profile["username"] = username       # Für Einfachheit direkt hinzufügen
        return profile

    def update_stats(self, username: str, score: int):
        """
        Aktualisiert Gesamtpunktestand und Spielanzahl nach einer Runde.
        Wird in app.py nach jedem Spielende aufgerufen.

        Args:
            username: Benutzername des Spielers
            score:    Punkte, die in der letzten Runde erzielt wurden
        """
        if username not in self.accounts:
            return
        self.accounts[username]["total_score"] += score
        self.accounts[username]["games_played"] += 1
        self._save()

    def add_achievement(self, username: str, achievement_id: str):
        """
        Verleiht einem Benutzer ein Achievement (ohne Duplikate).
        Die Duplikatprüfung ist hier zusätzlich zur Prüfung in achievements.py,
        um doppelte Einträge auch bei direkten API-Aufrufen zu verhindern.

        Args:
            username:       Benutzername
            achievement_id: ID des Achievements (z.B. "first_game")
        """
        if username not in self.accounts:
            return
        if achievement_id not in self.accounts[username]["achievements"]:
            self.accounts[username]["achievements"].append(achievement_id)
            self._save()

    def user_exists(self, username: str) -> bool:
        """Gibt True zurück, wenn ein Konto mit diesem Namen existiert."""
        return username in self.accounts
