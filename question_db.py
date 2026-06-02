"""
Question database - loads questions from JSON file and provides
category/question access. Falls back to built-in questions if the
file is missing or the Open Trivia DB is unreachable.
"""

import json
import os
import random
import urllib.request
import urllib.error
from typing import Optional

DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "questions.json")

# Built-in fallback questions so the game works without internet
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
    """Manages quiz questions stored in a JSON file."""

    def __init__(self):
        self.questions = self._load_questions()

    def _load_questions(self) -> list:
        """Load questions from the JSON file, or fall back to built-ins."""
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
        """Return a sorted list of unique categories."""
        return sorted(set(q["category"] for q in self.questions))

    def get_question_count(self, category: str) -> int:
        """Return the number of questions in a given category."""
        return sum(1 for q in self.questions if q["category"] == category)

    def get_questions(self, category: str, count: Optional[int] = None) -> list:
        """
        Return a shuffled list of questions for a category.
        If category is 'random', pull from all categories.
        """
        if category == "random":
            pool = list(self.questions)
        else:
            pool = [q for q in self.questions if q["category"] == category]

        random.shuffle(pool)

        if count is not None:
            pool = pool[:count]

        return pool

    def add_question(self, category: str, question: str, options: list, answer: int):
        """
        Add a new question to the database and persist to file.
        answer is the 0-based index of the correct option.
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
        """Persist questions to the JSON data file."""
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.questions, f, indent=2, ensure_ascii=False)


def fetch_questions_from_opentdb(amount: int = 20, category_id: int = 9) -> list:
    """
    Fetch questions from the Open Trivia Database API.
    Returns a list of question dicts compatible with our format,
    or an empty list on failure.
    """
    url = (
        f"https://opentdb.com/api.php?amount={amount}"
        f"&category={category_id}&type=multiple"
    )
    try:
        with urllib.request.urlopen(url, timeout=5) as resp:
            data = json.loads(resp.read().decode())
        questions = []
        for item in data.get("results", []):
            options = item["incorrect_answers"] + [item["correct_answer"]]
            random.shuffle(options)
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
        return []
