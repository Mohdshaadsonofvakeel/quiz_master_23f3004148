from flask import Blueprint, render_template, redirect, flash, url_for, request
from app import db
from flask_login import current_user, login_required
from random import shuffle
from app.models.chapter import Chapter
from app.models.quiz import Quiz
from app.models.score import Score
from app.models.subject import Subject
from app.models.user import User
from datetime import datetime


users_bp = Blueprint('users', __name__)

from sqlalchemy import and_

@users_bp.route("/dashboard")
@login_required
def dashboard():
    scores = Score.query.filter_by(user_id=current_user.id).all()
    total_attempted_quizzes = len(scores)
    average_score = sum([s.total_scored for s in scores]) / total_attempted_quizzes if total_attempted_quizzes > 0 else 0
    attempted_quiz_ids = [score.quiz_id for score in scores]

    # ✅ Use correct field date_of_quiz
    upcoming_quizzes = Quiz.query.filter(
        and_(
            ~Quiz.id.in_(attempted_quiz_ids),
            Quiz.date_of_quiz.isnot(None),
            Quiz.date_of_quiz >= datetime.utcnow()
        )
    ).all()

    # Optional - fetch all quizzes to show status
    all_quizzes = Quiz.query.all()

    return render_template("user/dashboard.html",
                           scores=scores,
                           total_attempted_quizzes=total_attempted_quizzes,
                           average_score=average_score,
                           quizzes=upcoming_quizzes,
                           all_quizzes=all_quizzes,
                           attempted_quiz_ids=attempted_quiz_ids,
                           now=datetime.utcnow())

@users_bp.route("/attempt_quiz/<int:quiz_id>", methods=['GET', 'POST'])
@login_required
def attempt_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = quiz.questions.copy()
    shuffle(questions)
    if request.method == 'POST':
        score = 0
        for question in questions:
            user_answer = request.form.get(f'question_{question.id}')
            if user_answer and int(user_answer) == question.correct_option:
                score += 1
        user_score = Score(
            total_scored=score,
            quiz_id=quiz_id,
            user_id=current_user.id
        )
        db.session.add(user_score)
        db.session.commit()
        flash(f'Quiz completed! Your score: {score} / {len(questions)}', category="success")
        return redirect(url_for("users.quiz_results", quiz_id=quiz_id))
    return render_template("user/attempt_quiz.html", quiz=quiz, questions=questions)

@users_bp.route("/quiz_results/<int:quiz_id>")
@login_required
def quiz_results(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    score = Score.query.filter_by(user_id=current_user.id, quiz_id=quiz_id).first()
    return render_template("user/quiz_results.html", quiz=quiz, score=score)

from collections import defaultdict
from sqlalchemy.sql import extract

@users_bp.route("/leaderboard")
@login_required
def leaderboard():
    users = User.get_all_users()
    leaderboard_data = []
    month_attempts = defaultdict(int)
    subject_attempts = defaultdict(int)

    for user in users:
        scores = Score.query.filter_by(user_id=user.id).all()
        total_score = sum(s.total_scored for s in scores)
        leaderboard_data.append({
            "user_fullname": user.fullname,
            "total_score": total_score
        })

        # Monthly quiz attempts
        for score in scores:
            if score.quiz and score.quiz.date_of_quiz:
                month_name = score.quiz.date_of_quiz.strftime("%B")  # Get month name
                month_attempts[month_name] += 1

            # Subject-wise quiz attempts
            if score.quiz and score.quiz.chapter:
                subject_attempts[score.quiz.chapter.subject.name] += 1

    leaderboard_data.sort(key=lambda x: x['total_score'], reverse=True)

    return render_template(
        "user/leaderboard.html",
        leaderboard_data=leaderboard_data,
        user_fullnames=[x["user_fullname"] for x in leaderboard_data],
        user_total_scores=[x["total_score"] for x in leaderboard_data],
        month_labels=list(month_attempts.keys()),
        month_attempts=list(month_attempts.values()),
        subject_labels=list(subject_attempts.keys()),
        subject_attempts=list(subject_attempts.values())
    )


@users_bp.route("/select-quiz", methods=['GET', 'POST'])
@login_required
def select_quiz():
    subjects = Subject.query.all()
    chapters = Chapter.query.all()
    quizzes = Quiz.query.all()

    if request.method == 'POST':
        subject_id = request.form.get('subject_id')
        chapter_id = request.form.get('chapter_id')

        if subject_id:
            quizzes = Quiz.query.join(Chapter).filter(Chapter.subject_id == subject_id).all()
        if chapter_id:
            quizzes = Quiz.query.filter_by(chapter_id=chapter_id).all()

    return render_template("user/select-quiz.html",
                           subjects=subjects,
                           chapters=chapters,
                           quizzes=quizzes)
@users_bp.route("/quiz_view/<int:quiz_id>")
@login_required
def quiz_view(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    chapter = Chapter.query.get(quiz.chapter_id)
    subject = Subject.query.get(chapter.subject_id)
    return render_template("user/quiz_view.html", quiz=quiz, chapter=chapter, subject=subject)
@users_bp.route('/user/search')
@login_required
def search_results():
    query = request.args.get("q", "").strip()
    if not query:
        flash("Enter a search term.", "warning")
        return redirect(url_for("users.dashboard"))

    # Search logic: Example with SQLAlchemy filters
    subjects = Subject.query.filter(Subject.name.ilike(f"%{query}%")).all()
    quizzes = Quiz.query.filter(Quiz.name.ilike(f"%{query}%")).order_by(Quiz.date_of_quiz.desc()).all()
    scores = Score.query.join(Quiz).filter(
    Quiz.name.ilike(f"%{query}%")).order_by(Score.total_scored.desc()).all()
    return render_template("user/search_results.html", query=query, subjects=subjects, quizzes=quizzes, scores=scores)


@users_bp.route("/score_details")
@login_required
def score_details():
    scores = Score.query.filter_by(user_id=current_user.id).all()
    
    score_data = [
        {
            "quiz_id": score.quiz_id,
            "name": Quiz.query.get(score.quiz_id).name,  # Fetch quiz name
            "num_questions": len(Quiz.query.get(score.quiz_id).questions),
            "date": Quiz.query.get(score.quiz_id).date_of_quiz.strftime('%Y-%m-%d') if Quiz.query.get(score.quiz_id).date_of_quiz else "N/A",
            "user_score": score.total_scored
        }
        for score in scores
    ]

    return render_template("user/score_details.html", user_scores=score_data)
