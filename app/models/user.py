from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)  # ✅ Add this back
    password_hash = db.Column(db.String(200), nullable=False)
    fullname = db.Column(db.String(150))
    qualification = db.Column(db.String(100))
    dob = db.Column(db.Date)
    is_admin = db.Column(db.Boolean, default=False)


    @property
    def is_active(self):
        return True  # ✅ Required by Flask-Login



    scores = db.relationship('Score', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @classmethod
    def get_all_users(cls):
        return cls.query.filter(cls.username != "admin@quiz.com").all()