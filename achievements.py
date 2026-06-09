"""
achievements.py – Achievement-System für BrainBuster

Definiert alle verfügbaren Achievements und prüft nach jedem Spiel,
welche davon neu freigeschaltet wurden.

Designentscheidung – reine Funktion statt Klasse:
  check_achievements() ist eine reine Funktion (keine Seiteneffekte,
  gleiches Input → gleiches Output). Das macht sie leicht testbar und
  unabhängig vom Rest der Anwendung. Der AccountManager kümmert sich
  um das tatsächliche Speichern der Achievements.

Erweiterbarkeit:
  Neue Achievements können einfach dem ACHIEVEMENTS-Dict hinzugefügt
  und in check_achievements() mit einer Bedingung verknüpft werden.
  Kein anderer Code muss geändert werden.
"""

from typing import Optional

# Zentrales Verzeichnis aller Achievements.
# Schlüssel = interne ID (wird in accounts.json gespeichert)
# Wert = Anzeigeinformationen für die Weboberfläche und das Profil
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
    Prüft nach einem Spiel, welche Achievements neu freigeschaltet wurden.

    Die Funktion prüft alle Bedingungen und gibt nur die IDs zurück,
    die NOCH NICHT in der existing-Liste enthalten sind. Das verhindert,
    dass ein Achievement mehrfach angezeigt wird.

    Args:
        games_played:  Gesamtanzahl gespielter Runden (inkl. aktuelle)
        total_score:   Gesamtpunktestand des Spielers (inkl. aktuelle Runde)
        current_score: Punkte aus der aktuellen Runde (aktuell nicht genutzt,
                       aber für zukünftige Score-basierte Achievements vorbereitet)
        correct:       Richtige Antworten in der aktuellen Runde
        total:         Gesamtfragen in der aktuellen Runde
        fast_answers:  Antworten unter 3 Sekunden in der aktuellen Runde
        existing:      Liste bereits freigeschalteter Achievement-IDs

    Returns:
        Liste der neu freigeschalteten Achievement-IDs (kann leer sein)
    """
    newly_unlocked = []

    def unlock(achievement_id: str):
        """Hilfsfunktion: fügt ein Achievement hinzu, falls noch nicht vorhanden."""
        if achievement_id not in existing and achievement_id not in newly_unlocked:
            newly_unlocked.append(achievement_id)

    # Erstes abgeschlossenes Spiel
    if games_played >= 1:
        unlock("first_game")

    # Alle Fragen in einer Runde richtig beantwortet
    if total > 0 and correct == total:
        unlock("perfect_game")

    # Mindestens 3 Fragen in unter 3 Sekunden beantwortet
    if fast_answers >= 3:
        unlock("speed_demon")

    # Kumulierter Punktestand von 100 erreicht
    if total_score >= 100:
        unlock("century")

    # Kumulierter Punktestand von 500 erreicht
    if total_score >= 500:
        unlock("scholar")

    # 10 Spiele gespielt
    if games_played >= 10:
        unlock("veteran")

    # 80% Genauigkeit in einer Runde mit mindestens 5 Fragen
    # (min. 5 Fragen verhindert, dass 1/1 = 100% das Achievement auslöst)
    accuracy = (correct / total * 100) if total >= 5 else 0
    if accuracy >= 80:
        unlock("quiz_master")

    return newly_unlocked


def get_achievement_details(achievement_id: str) -> Optional[dict]:
    """
    Gibt die Anzeigedaten (Name, Beschreibung, Icon) für eine Achievement-ID zurück.

    Args:
        achievement_id: Interne ID (z.B. "first_game")

    Returns:
        Dict mit name/description/icon, oder None wenn ID unbekannt
    """
    return ACHIEVEMENTS.get(achievement_id)


def get_all_achievements() -> dict:
    """
    Gibt das vollständige Achievement-Verzeichnis zurück.
    Wird im Profil verwendet, um alle Achievements (inkl. gesperrte) anzuzeigen.
    """
    return ACHIEVEMENTS
