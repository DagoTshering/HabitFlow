from datetime import date
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import UniqueConstraint
from app import db, login_manager

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    habits = db.relationship("Habit", backref="owner", cascade="all, delete-orphan", lazy="dynamic")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Habit(db.Model):
    __tablename__ = "habits"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = db.Column(db.String(140), nullable=False)
    description = db.Column(db.Text)
    frequency = db.Column(db.String(20), default="daily")  # 'daily' or 'weekly'

    logs = db.relationship("HabitLog", backref="habit", cascade="all, delete-orphan", lazy="dynamic")

    def completed_on(self, day):
        return self.logs.filter_by(date_completed=day).first() is not None

    def completion_count(self):
        return self.logs.count()

class HabitLog(db.Model):
    __tablename__ = "habit_logs"
    id = db.Column(db.Integer, primary_key=True)
    habit_id = db.Column(db.Integer, db.ForeignKey("habits.id", ondelete="CASCADE"), nullable=False)
    date_completed = db.Column(db.Date, nullable=False)

    __table_args__ = (
        UniqueConstraint('habit_id', 'date_completed', name='_habit_date_uc'),
    )