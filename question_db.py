"""
question_db.py – Fragedatenbank für BrainBuster

Verwaltet alle Quizfragen: Laden, Speichern, Filtern nach Kategorie
und optionaler Abruf aus der Open Trivia Database API.

Datenformat einer Frage (JSON):
    {
        "category": "Science",
        "question": "What is H2O?",
        "options":  ["Water", "Oxygen", "Hydrogen", "Salt"],
        "answer":   0          ← 0-basierter Index der richtigen Antwort
    }

Warum JSON statt einer echten Datenbank?
    Für diesen Prototyp reicht JSON vollständig aus: keine Datenbankinstallation,
    direktes Lesen/Schreiben, portabel auf allen Betriebssystemen.
    Das Format ist einfach genug, dass das Lehrerteam Fragen auch manuell
    in der Datei ergänzen kann. In einer Produktionsversion würde man
    SQLite oder PostgreSQL verwenden.

Warum eingebaute Fallback-Fragen?
    Das Spiel soll auch ohne Internetverbindung und ohne vorhandene
    questions.json funktionieren. Die 15 Fallback-Fragen decken alle
    Grundkategorien ab und ermöglichen sofortiges Spielen.
"""

import json
import os
import random
import urllib.request
import urllib.error
from typing import Optional

# Pfad zur Fragedatei – liegt im data/-Unterordner neben dieser Datei
DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "questions.json")

# Eingebaute Fallback-Fragen für den Offline-Betrieb.
# Jede Frage hat genau 4 Antwortoptionen und einen 0-basierten Korrektheitsindex.
FALLBACK_QUESTIONS = [
    {
        "category": "Science",
        "question": "What is the chemical symbol for water?",
        "options": ["H2O", "CO2", "NaCl", "O2"],
        "answer": 0,
    },
    {
        "category": "Science",
        "question": "How many planets are in our solar system?",
        "options": ["7", "8", "9", "10"],
        "answer": 1,
    },
    {
        "category": "Science",
        "question": "What gas do plants absorb from the atmosphere?",
        "options": ["Oxygen", "Nitrogen", "Carbon Dioxide", "Hydrogen"],
        "answer": 2,
    },
    {
        "category": "History",
        "question": "In which year did World War II end?",
        "options": ["1943", "1944", "1945", "1946"],
        "answer": 2,
    },
    {
        "category": "History",
        "question": "Who was the first person to walk on the moon?",
        "options": ["Buzz Aldrin", "Yuri Gagarin", "Neil Armstrong", "John Glenn"],
        "answer": 2,
    },
    {
        "category": "History",
        "question": "Which empire was ruled by Julius Caesar?",
        "options": ["Greek", "Roman", "Ottoman", "Byzantine"],
        "answer": 1,
    },
    {
        "category": "Geography",
        "question": "What is the capital of Australia?",
        "options": ["Sydney", "Melbourne", "Brisbane", "Canberra"],
        "answer": 3,
    },
    {
        "category": "Geography",
        "question": "Which is the longest river in the world?",
        "options": ["Amazon", "Yangtze", "Mississippi", "Nile"],
        "answer": 3,
    },
    {
        "category": "Geography",
        "question": "On which continent is the Sahara Desert located?",
        "options": ["Asia", "South America", "Africa", "Australia"],
        "answer": 2,
    },
    {
        "category": "Technology",
        "question": "What does 'CPU' stand for?",
        "options": [
            "Central Processing Unit",
            "Computer Personal Unit",
            "Central Program Utility",
            "Core Processing Unit",
        ],
        "answer": 0,
    },
    {
        "category": "Technology",
        "question": "Which programming language is known as the 'language of the web'?",
        "options": ["Python", "Java", "JavaScript", "C++"],
        "answer": 2,
    },
    {
        "category": "Technology",
        "question": "What does 'HTML' stand for?",
        "options": [
            "Hyper Text Markup Language",
            "High Transfer Machine Language",
            "Hyper Transfer Meta Language",
            "Home Tool Markup Language",
        ],
        "answer": 0,
    },
    {
        "category": "Sports",
        "question": "How many players are on a standard soccer team?",
        "options": ["9", "10", "11", "12"],
        "answer": 2,
    },
    {
        "category": "Sports",
        "question": "In which sport would you perform a 'slam dunk'?",
        "options": ["Volleyball", "Basketball", "Tennis", "Baseball"],
        "answer": 1,
    },
    {
        "category": "Sports",
        "question": "How many rings are on the Olympic flag?",
        "options": ["4", "5", "6", "7"],
        "answer": 1,
    },
]


class QuestionDB:
    """
    Lädt, speichert und filtert Quizfragen aus einer JSON-Datei.

    Beim ersten Start ohne vorhandene questions.json werden die eingebauten
    Fallback-Fragen verwendet. Über das Admin-Backend oder add_question()
    hinzugefügte Fragen werden dauerhaft in data/questions.json gespeichert.
    """

    def __init__(self):
        """Lädt Fragen beim Start – aus Datei oder Fallback."""
        self.questions = self._load_questions()

    def _load_questions(self) -> list:
        """
        Versucht, Fragen aus data/questions.json zu laden.
        Fällt auf die eingebauten Fragen zurück, wenn:
          - die Datei nicht existiert (erster Start)
          - die Datei beschädigt/ungültiges JSON enthält
        """
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    print(f"Loaded {len(data)} questions from database.")
                    return data
            except (json.JSONDecodeError, KeyError):
                print("Warning: questions.json is malformed. Using built-in questions.")

        print("Using built-in question set.")
        return FALLBACK_QUESTIONS

    def get_categories(self) -> list:
        """
        Gibt alle vorhandenen Kategorien alphabetisch sortiert zurück.
        Verwendet ein Set, um Duplikate zu vermeiden.
        """
        return sorted(set(q["category"] for q in self.questions))

    def get_question_count(self, category: str) -> int:
        """
        Zählt die Fragen einer bestimmten Kategorie.
        Wird in der Kategorienauswahl (Konsole) für die Anzeige verwendet.
        """
        return sum(1 for q in self.questions if q["category"] == category)

    def get_questions(self, category: str, count: Optional[int] = None) -> list:
        """
        Gibt eine zufällig gemischte Liste von Fragen zurück.

        Wenn category == "random", werden Fragen aus allen Kategorien gemischt.
        random.shuffle() mischt die Liste in-place, daher wird zuerst eine
        Kopie erstellt (list(...)), um die Original-Liste unverändert zu lassen.

        Args:
            category: Kategoriename oder "random" für alle Kategorien
            count:    Maximale Anzahl zurückgegebener Fragen (None = alle)

        Returns:
            Gemischte Liste von Frage-Dicts
        """
        if category == "random":
            pool = list(self.questions)  # Kopie, damit Original unverändert bleibt
        else:
            pool = [q for q in self.questions if q["category"] == category]

        random.shuffle(pool)

        if count is not None:
            pool = pool[:count]

        return pool

    def add_question(self, category: str, question: str, options: list, answer: int):
        """
        Fügt eine neue Frage zur Datenbank hinzu und speichert sie dauerhaft.

        Args:
            category: Kategorie der Frage (kann neue oder bestehende sein)
            question: Fragetext
            options:  Liste von genau 4 Antwortoptionen
            answer:   0-basierter Index der richtigen Antwort (0–3)
        """
        new_q = {
            "category": category,
            "question": question,
            "options": options,
            "answer": answer,
        }
        self.questions.append(new_q)
        self._save_questions()
        print(f"Question added to category '{category}'.")

    def _save_questions(self):
        """
        Schreibt alle Fragen in data/questions.json.
        ensure_ascii=False erlaubt Umlaute und Sonderzeichen direkt im JSON.
        """
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.questions, f, indent=2, ensure_ascii=False)


def fetch_questions_from_opentdb(amount: int = 20, category_id: int = 9) -> list:
    """
    Ruft Fragen von der Open Trivia Database API ab (https://opentdb.com).

    Die API gibt Fragen mit einer richtigen und drei falschen Antworten
    zurück. Diese Funktion mischt die Optionen und merkt sich den neuen
    Index der richtigen Antwort, damit das interne Format eingehalten wird.

    Warum urllib statt requests?
        urllib ist in der Python-Standardbibliothek enthalten –
        kein extra Paket nötig.

    Args:
        amount:      Anzahl der abzurufenden Fragen (max. 50 bei opentdb)
        category_id: Kategorie-ID der Open Trivia DB (9 = General Knowledge)

    Returns:
        Liste von Frage-Dicts im internen Format, oder [] bei Fehler
    """
    url = f"https://opentdb.com/api.php?amount={amount}" f"&category={category_id}&type=multiple"
    try:
        with urllib.request.urlopen(url, timeout=5) as resp:  # nosec B310
            data = json.loads(resp.read().decode())
        questions = []
        for item in data.get("results", []):
            # Richtige + falsche Antworten zusammenführen und mischen
            options = item["incorrect_answers"] + [item["correct_answer"]]
            random.shuffle(options)
            # Den neuen Index der richtigen Antwort nach dem Mischen finden
            correct_index = options.index(item["correct_answer"])
            questions.append(
                {
                    "category": item["category"],
                    "question": item["question"],
                    "options": options,
                    "answer": correct_index,
                }
            )
        return questions
    except (urllib.error.URLError, json.JSONDecodeError, KeyError):
        # Bei Netzwerkfehler oder unerwartetem API-Format: leer zurückgeben
        return []
