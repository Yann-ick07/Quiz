"""
app.py - Flask web application for BrainBuster.
Provides a full web UI with accounts, gameplay, leaderboard,
admin backend and achievements.

Run with: python app.py
Then open: http://localhost:5000
"""

import time
import os
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
)
from accounts import AccountManager
from question_db import QuestionDB
from leaderboard import Leaderboard
from achievements import (
    check_achievements,
    check_hardcore_completion,
    get_all_achievements,
    get_achievement_details,
)

app = Flask(__name__)
app.secret_key = "brainbuster-secret-key-change-in-production"

# Custom Jinja2 filter so templates can use options|enumerate
app.jinja_env.filters["enumerate"] = enumerate

# Shared instances (app-level singletons)
account_mgr = AccountManager()
question_db = QuestionDB()
leaderboard = Leaderboard()


# ── Helpers ──────────────────────────────────────────────────────────────────


def login_required(f):
    """Decorator: redirect to login if user is not in session."""
    from functools import wraps

    @wraps(f)
    def decorated(*args, **kwargs):
        if "username" not in session:
            flash("Please log in first.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return decorated


def get_current_user() -> dict | None:
    """Return the logged-in user's profile, or None."""
    if "username" in session:
        return account_mgr.get_profile(session["username"])
    return None


# ── Auth routes ───────────────────────────────────────────────────────────────


@app.route("/")
def index():
    user = get_current_user()
    return render_template(
        "index.html",
        user=user,
        categories=question_db.get_categories(),
        top_scores=leaderboard.entries[:5],
    )


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        ok, msg = account_mgr.register(username, password)
        if ok:
            session["username"] = username
            flash("Account created! Welcome to BrainBuster.", "success")
            return redirect(url_for("index"))
        flash(msg, "danger")
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        ok, msg = account_mgr.login(username, password)
        if ok:
            session["username"] = username
            flash(f"Welcome back, {username}!", "success")
            return redirect(url_for("index"))
        flash(msg, "danger")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out.", "info")
    return redirect(url_for("index"))


# ── Profile ───────────────────────────────────────────────────────────────────


@app.route("/profile")
@login_required
def profile():
    user = get_current_user()
    all_achievements = get_all_achievements()
    return render_template("profile.html", user=user, all_achievements=all_achievements)


# ── Game routes ───────────────────────────────────────────────────────────────


@app.route("/play", methods=["GET", "POST"])
@login_required
def play():
    """Game setup page: choose category and mode."""
    categories = question_db.get_categories()
    return render_template("play.html", categories=categories, user=get_current_user())


@app.route("/game/start", methods=["POST"])
@login_required
def game_start():
    """Initialize a new game session and redirect to first question."""
    category = request.form.get("category", "random")
    mode = request.form.get("mode", "solo")

    # Hardcore uses ALL questions, other modes use 10
    if mode == "hardcore":
        questions = question_db.get_questions(category)
    else:
        questions = question_db.get_questions(category, count=10)

    if not questions:
        flash("No questions found for this category.", "warning")
        return redirect(url_for("play"))

    session["game"] = {
        "questions": questions,
        "current": 0,
        "score": 0,
        "correct": 0,
        "fast_answers": 0,
        "category": category,
        "mode": mode,
        "start_time": time.time(),
        "answers": [],
        "hardcore_failed": False,
    }
    return redirect(url_for("game_question"))


@app.route("/game/question")
@login_required
def game_question():
    """Display the current question."""
    game = session.get("game")
    if not game:
        return redirect(url_for("play"))

    idx = game["current"]
    questions = game["questions"]

    if idx >= len(questions):
        return redirect(url_for("game_result"))

    q = questions[idx]
    import html

    question_text = html.unescape(q["question"])
    options = [html.unescape(opt) for opt in q["options"]]

    return render_template(
        "question.html",
        question=question_text,
        options=options,
        question_number=idx + 1,
        total_questions=len(questions),
        score=game["score"],
        category=game["category"],
        mode=game["mode"],
        user=get_current_user(),
    )


@app.route("/game/answer", methods=["POST"])
@login_required
def game_answer():
    """Process a submitted answer and advance to the next question."""
    game = session.get("game")
    if not game:
        return redirect(url_for("play"))

    idx = game["current"]
    q = game["questions"][idx]
    chosen = int(request.form.get("answer", -1))
    answer_time = float(request.form.get("answer_time", 10))

    correct = chosen == q["answer"]
    points = 0

    if correct:
        speed_bonus = 0
        if answer_time < 5:
            speed_bonus = int(5 * (1 - answer_time / 5))
        points = 10 + speed_bonus
        game["score"] += points
        game["correct"] += 1
        if answer_time < 3:
            game["fast_answers"] += 1

    import html

    game["answers"].append(
        {
            "question": html.unescape(q["question"]),
            "chosen": chosen,
            "correct_index": q["answer"],
            "options": [html.unescape(o) for o in q["options"]],
            "was_correct": correct,
            "points": points,
            "time": round(answer_time, 1),
        }
    )

    game["current"] += 1

    # Hardcore mode: a wrong answer immediately ends the game
    if game["mode"] == "hardcore" and not correct:
        game["hardcore_failed"] = True
        session["game"] = game
        session.modified = True
        return redirect(url_for("game_result"))

    session["game"] = game  # persist changes back to session
    session.modified = True

    return redirect(url_for("game_question"))


@app.route("/game/result")
@login_required
def game_result():
    """Show end-of-game summary, update stats and check achievements."""
    game = session.get("game")
    if not game:
        return redirect(url_for("play"))

    username = session["username"]
    score = game["score"]
    correct = game["correct"]
    total = len(game["questions"])
    category = game["category"]
    mode = game["mode"]

    # Update persistent account stats
    account_mgr.update_stats(username, score)
    leaderboard.add_entry(username, score, category, mode)

    # Check for newly unlocked achievements
    profile = account_mgr.get_profile(username)
    hardcore_failed = game.get("hardcore_failed", False)

    if mode == "hardcore" and not hardcore_failed:
        # Clean hardcore run: check for hardcore_survivor + normal achievements
        new_achievements = check_hardcore_completion(
            games_played=profile["games_played"],
            total_score=profile["total_score"],
            correct=correct,
            total=total,
            fast_answers=game["fast_answers"],
            existing=profile["achievements"],
        )
    else:
        new_achievements = check_achievements(
            games_played=profile["games_played"],
            total_score=profile["total_score"],
            current_score=score,
            correct=correct,
            total=total,
            fast_answers=game["fast_answers"],
            existing=profile["achievements"],
        )
    for ach_id in new_achievements:
        account_mgr.add_achievement(username, ach_id)

    new_ach_details = [get_achievement_details(a) for a in new_achievements]

    session.pop("game", None)

    hardcore_failed = game.get("hardcore_failed", False)

    return render_template(
        "result.html",
        score=score,
        correct=correct,
        total=total,
        accuracy=round((correct / total * 100) if total else 0),
        answers=game["answers"],
        new_achievements=new_ach_details,
        leaderboard=leaderboard.entries[:10],
        user=get_current_user(),
        mode=mode,
        hardcore_failed=hardcore_failed,
    )


# ── Leaderboard ───────────────────────────────────────────────────────────────


@app.route("/leaderboard")
def leaderboard_page():
    return render_template("leaderboard.html", entries=leaderboard.entries, user=get_current_user())


# ── Admin backend ─────────────────────────────────────────────────────────────


@app.route("/admin")
@login_required
def admin():
    """Admin page: view and manage questions."""
    return render_template(
        "admin.html",
        questions=question_db.questions,
        categories=question_db.get_categories(),
        user=get_current_user(),
    )


@app.route("/admin/add", methods=["POST"])
@login_required
def admin_add_question():
    """Add a new question via the admin form."""
    category = request.form.get("category", "").strip()
    new_category = request.form.get("new_category", "").strip()
    question_text = request.form.get("question", "").strip()
    options = [
        request.form.get("option_a", "").strip(),
        request.form.get("option_b", "").strip(),
        request.form.get("option_c", "").strip(),
        request.form.get("option_d", "").strip(),
    ]
    correct = int(request.form.get("correct", 0))

    # Use new category if provided
    final_category = new_category if new_category else category

    if not final_category or not question_text or not all(options):
        flash("All fields are required.", "danger")
        return redirect(url_for("admin"))

    question_db.add_question(final_category, question_text, options, correct)
    flash("Question added successfully.", "success")
    return redirect(url_for("admin"))


@app.route("/admin/delete/<int:question_index>", methods=["POST"])
@login_required
def admin_delete_question(question_index):
    """Delete a question by its index."""
    if 0 <= question_index < len(question_db.questions):
        removed = question_db.questions.pop(question_index)
        question_db._save_questions()
        flash(f"Question deleted: {removed['question'][:50]}...", "success")
    else:
        flash("Question not found.", "danger")
    return redirect(url_for("admin"))


@app.route("/admin/edit/<int:question_index>", methods=["GET", "POST"])
@login_required
def admin_edit_question(question_index):
    """Edit an existing question."""
    if question_index < 0 or question_index >= len(question_db.questions):
        flash("Question not found.", "danger")
        return redirect(url_for("admin"))

    if request.method == "POST":
        q = question_db.questions[question_index]
        q["category"] = request.form.get("category", q["category"]).strip()
        q["question"] = request.form.get("question", q["question"]).strip()
        q["options"] = [
            request.form.get("option_a", "").strip(),
            request.form.get("option_b", "").strip(),
            request.form.get("option_c", "").strip(),
            request.form.get("option_d", "").strip(),
        ]
        q["answer"] = int(request.form.get("correct", 0))
        question_db._save_questions()
        flash("Question updated.", "success")
        return redirect(url_for("admin"))

    question = question_db.questions[question_index]
    return render_template(
        "edit_question.html",
        question=question,
        index=question_index,
        categories=question_db.get_categories(),
        user=get_current_user(),
    )


# ── Multiplayer (simple same-device 2-player mode) ────────────────────────────


@app.route("/multiplayer", methods=["GET", "POST"])
@login_required
def multiplayer_setup():
    """Setup page for local 2-player multiplayer."""
    categories = question_db.get_categories()
    return render_template("multiplayer_setup.html", categories=categories, user=get_current_user())


@app.route("/multiplayer/start", methods=["POST"])
@login_required
def multiplayer_start():
    """Start a 2-player game session."""
    player2_name = request.form.get("player2", "Player 2").strip() or "Player 2"
    category = request.form.get("category", "random")

    questions = question_db.get_questions(category, count=10)
    if not questions:
        flash("No questions found.", "warning")
        return redirect(url_for("multiplayer_setup"))

    session["mp_game"] = {
        "questions": questions,
        "current": 0,
        "player1": {"name": session["username"], "score": 0, "correct": 0},
        "player2": {"name": player2_name, "score": 0, "correct": 0},
        "category": category,
        "current_player": 1,  # whose turn (1 or 2)
    }
    return redirect(url_for("multiplayer_question"))


@app.route("/multiplayer/question")
@login_required
def multiplayer_question():
    """Show a question for the current multiplayer turn."""
    mp = session.get("mp_game")
    if not mp:
        return redirect(url_for("multiplayer_setup"))

    idx = mp["current"]
    if idx >= len(mp["questions"]):
        return redirect(url_for("multiplayer_result"))

    q = mp["questions"][idx]
    import html

    question_text = html.unescape(q["question"])
    options = [html.unescape(opt) for opt in q["options"]]
    current_player = mp[f"player{mp['current_player']}"]

    return render_template(
        "multiplayer_question.html",
        question=question_text,
        options=options,
        question_number=idx + 1,
        total_questions=len(mp["questions"]),
        current_player=current_player,
        player_num=mp["current_player"],
        p1=mp["player1"],
        p2=mp["player2"],
        user=get_current_user(),
    )


@app.route("/multiplayer/answer", methods=["POST"])
@login_required
def multiplayer_answer():
    """Handle a multiplayer answer and alternate turns."""
    mp = session.get("mp_game")
    if not mp:
        return redirect(url_for("multiplayer_setup"))

    idx = mp["current"]
    q = mp["questions"][idx]
    chosen = int(request.form.get("answer", -1))
    pnum = mp["current_player"]
    player_key = f"player{pnum}"

    if chosen == q["answer"]:
        mp[player_key]["score"] += 10
        mp[player_key]["correct"] += 1

    # Alternate: both players answer the same question, then advance
    if pnum == 1:
        mp["current_player"] = 2
    else:
        mp["current_player"] = 1
        mp["current"] += 1  # both players done with this question

    session["mp_game"] = mp
    session.modified = True
    return redirect(url_for("multiplayer_question"))


@app.route("/multiplayer/result")
@login_required
def multiplayer_result():
    """Show the multiplayer final scores."""
    mp = session.get("mp_game")
    if not mp:
        return redirect(url_for("multiplayer_setup"))

    p1 = mp["player1"]
    p2 = mp["player2"]
    total = len(mp["questions"])

    if p1["score"] > p2["score"]:
        winner = p1["name"]
    elif p2["score"] > p1["score"]:
        winner = p2["name"]
    else:
        winner = "Tie!"

    # Save the logged-in player's score to leaderboard
    leaderboard.add_entry(p1["name"], p1["score"], mp["category"], "multiplayer")
    account_mgr.update_stats(p1["name"], p1["score"])

    session.pop("mp_game", None)
    return render_template(
        "multiplayer_result.html", p1=p1, p2=p2, winner=winner, total=total, user=get_current_user()
    )


if __name__ == "__main__":
    print("\n  BrainBuster Web App")
    print("  Open http://localhost:5000 in your browser\n")
    debug_mode = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", debug=debug_mode, port=5000)
