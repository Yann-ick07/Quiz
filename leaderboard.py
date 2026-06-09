"""
leaderboard.py – Globale Rangliste für BrainBuster

Speichert die besten Spielresultate sitzungsübergreifend in einer
JSON-Datei und stellt sie für Web-UI und Konsolenausgabe bereit.

Warum nur die Top 10?
  Die Rangliste soll motivieren, nicht entmutigen. Eine unbegrenzt
  wachsende Liste würde außerdem die Datei mit der Zeit aufblähen.
  MAX_ENTRIES kann einfach erhöht werden, wenn gewünscht.

Warum JSON statt SQLite?
  Für diesen Prototyp ist JSON ausreichend: keine Datenbankverbindung
  nötig, direkt menschenlesbar, einfach zu debuggen. Bei gleichzeitigen
  Zugriffen (echter Mehrspieler-Server) würde man auf eine echte DB wechseln.
"""

import json
import os
from datetime import datetime
from typing import Optional

# Pfad zur Ranglisten-Datei (wird automatisch angelegt)
SCORES_FILE = os.path.join(os.path.dirname(__file__), "data", "scores.json")

# Maximale Anzahl Einträge in der Rangliste
MAX_ENTRIES = 10


class Leaderboard:
    """
    Verwaltet die globale Highscore-Rangliste.

    Einträge werden nach Punktzahl absteigend sortiert.
    Nur die besten MAX_ENTRIES Einträge werden behalten.
    """

    def __init__(self):
        """Lädt die bestehende Rangliste beim Start aus der JSON-Datei."""
        self.entries = self._load()

    def _load(self) -> list:
        """
        Liest die Rangliste von der Festplatte.
        Gibt eine leere Liste zurück, falls die Datei fehlt oder beschädigt ist.
        """
        if os.path.exists(SCORES_FILE):
            try:
                with open(SCORES_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return []

    def _save(self):
        """
        Schreibt die aktuelle Rangliste auf die Festplatte.
        exist_ok=True verhindert einen Fehler, wenn data/ noch nicht existiert.
        """
        os.makedirs(os.path.dirname(SCORES_FILE), exist_ok=True)
        with open(SCORES_FILE, "w", encoding="utf-8") as f:
            json.dump(self.entries, f, indent=2, ensure_ascii=False)

    def add_entry(self, name: str, score: int, category: str, mode: str):
        """
        Fügt einen neuen Eintrag hinzu, sortiert die Liste und kürzt auf MAX_ENTRIES.

        Das Sortieren nach jedem Eintrag ist einfacher als eine
        Einfügesortierung, da die Liste klein ist (max. 10 Einträge).

        Args:
            name:     Spielername
            score:    Erzielte Punkte
            category: Gewählte Kategorie (z.B. "Science" oder "random")
            mode:     Spielmodus ("solo", "time_attack" oder "multiplayer")
        """
        entry = {
            "name": name,
            "score": score,
            "category": category,
            "mode": mode,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
        self.entries.append(entry)

        # Absteigend nach Punktzahl sortieren, dann auf MAX_ENTRIES kürzen
        self.entries.sort(key=lambda e: e["score"], reverse=True)
        self.entries = self.entries[:MAX_ENTRIES]
        self._save()

    def display(self, filter_mode: Optional[str] = None):
        """
        Gibt die Rangliste formatiert auf der Konsole aus.
        Wird in main.py am Ende jeder Runde und im Hauptmenü aufgerufen.

        Args:
            filter_mode: Wenn angegeben, werden nur Einträge dieses Modus angezeigt.
        """
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
