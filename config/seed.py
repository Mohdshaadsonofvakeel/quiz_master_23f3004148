from application_files import db
from datetime import datetime
from application_files.models.chapter import Chapter
from application_files.models.question import Question
from application_files.models.quiz import Quiz
from application_files.models.score import Score
from application_files.models.subject import Subject
from application_files.models.user import User

# Sample data to better testion the application
# and to ensure the application is working as expected
# and to ensure the application is working as expected
# and to ensure the application is working as expected  


# Expanded users data
users_data = [
    {"username": f"user{i}", "email": f"user{i}@example.com", "password": "password", "fullname": f"User {i}", "qualification": "B.Sc", "dob": datetime(1990 + (i % 10), i % 12 + 1, i % 28 + 1)} for i in range(1, 21)
]

# Expanded subjects data
subjects_data = [
    {"name": f"Subject {i}", "description": f"Description for Subject {i}."} for i in range(1, 21)
]

# Expanded chapters data
chapters_data = [
    {"name": f"Chapter {i}", "description": f"Description for Chapter {i}.", "subject_id": (i % 20) + 1} for i in range(1, 21)
]

# Expanded quizzes data
quizzes_data = [
    {"name": f"Quiz {i}", "date_of_quiz": datetime(2025, i % 12 + 1, i % 28 + 1), "time_duration": (10 + i % 5) * 60, "chapter_id": (i % 20) + 1} for i in range(1, 21)
]

# Expanded questions data
questions_data = []
for i in range(1, 21):
    questions_data.append(
        {"question_statement": f"Question {i} for Quiz {(i % 20) + 1}",
         "option1": "Option A", "option2": "Option B", "option3": "Option C", "option4": "Option D", 
         "correct_option": (i % 4) + 1, "quiz_id": (i % 20) + 1}
    )

# Expanded attempts data
attempts_data = [
    {"user_id": (i % 20) + 1, "quiz_id": (i % 20) + 1, "total_scored": i % 5} for i in range(1, 21)
]

print("Data processing complete! We are ready to test the application.")
# Function to seed the database




def seed_database():
    # Add users
    for user_data in users_data:
        user = User(
            username=user_data["username"],
            fullname=user_data["fullname"],
            email=user_data["email"],
            qualification=user_data["qualification"],
            dob=user_data["dob"]
        )
        user.set_password(user_data["password"])
        db.session.add(user)
    
    # Add subjects
    for subject_data in subjects_data:
        subject = Subject(
            name=subject_data["name"],
            description=subject_data["description"]
        )
        db.session.add(subject)
    
    # Add chapters
    for chapter_data in chapters_data:
        chapter = Chapter(
            name=chapter_data["name"],
            description=chapter_data["description"],
            subject_id=chapter_data["subject_id"]
        )
        db.session.add(chapter)
    
    # Add quizzes
    for quiz_data in quizzes_data:
        quiz = Quiz(
            name=quiz_data["name"],
            date_of_quiz=quiz_data["date_of_quiz"],
            time_duration=quiz_data["time_duration"],
            chapter_id=quiz_data["chapter_id"]
        )
        db.session.add(quiz)
    
    # Add questions
    for question_data in questions_data:
        question = Question(
            question_statement=question_data["question_statement"],
            option1=question_data["option1"],
            option2=question_data["option2"],
            option3=question_data["option3"],
            option4=question_data["option4"],
            correct_option=question_data["correct_option"],
            quiz_id=question_data["quiz_id"]
        )
        db.session.add(question)
    
    # Add attempts
    for attempt_data in attempts_data:
        attempt = Score(
            user_id=attempt_data["user_id"],
            quiz_id=attempt_data["quiz_id"],
            total_scored=attempt_data["total_scored"]
        )
        db.session.add(attempt)
    
    db.session.commit()