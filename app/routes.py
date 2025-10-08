from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, abort
from flask_login import login_user, logout_user, current_user, login_required
from . import db
from .models import User, Habit, HabitLog
from .forms import SignupForm, LoginForm, HabitForm
from datetime import date
from sqlalchemy.exc import IntegrityError

bp = Blueprint("routes", __name__)

# --- auth ---
@bp.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("routes.index"))
    form = SignupForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash("Email already registered.", "warning")
            return render_template("signup.html", form=form)
        user = User(name=form.name.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Account created — please log in.", "success")
        return redirect(url_for("routes.login"))
    return render_template("signup.html", form=form)

@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("routes.index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash("Logged in.", "success")
            next_page = request.args.get("next")
            return redirect(next_page or url_for("routes.index"))
        flash("Invalid email or password.", "danger")
    return render_template("login.html", form=form)

@bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out.", "info")
    return redirect(url_for("routes.login"))

# --- dashboard ---
@bp.route("/")
@bp.route("/dashboard")
@login_required
def index():
    habits = current_user.habits.all()
    today = date.today()
    # compute progress: is completed today
    progress = []
    for h in habits:
        completed = h.completed_on(today)
        total = h.completion_count()
        progress.append({"habit": h, "completed_today": completed, "total": total})
    return render_template("index.html", progress=progress, today=today)

# --- add habit ---
@bp.route("/habit/new", methods=["GET", "POST"])
@login_required
def add_habit():
    form = HabitForm()
    if form.validate_on_submit():
        h = Habit(user_id=current_user.id, name=form.name.data, description=form.description.data, frequency=form.frequency.data)
        db.session.add(h)
        db.session.commit()
        flash("Habit added.", "success")
        return redirect(url_for("routes.index"))
    return render_template("add_edit_habit.html", form=form, title="Add Habit")

# --- edit habit ---
@bp.route("/habit/<int:habit_id>/edit", methods=["GET", "POST"])
@login_required
def edit_habit(habit_id):
    h = Habit.query.get_or_404(habit_id)
    if h.owner != current_user:
        abort(403)
    form = HabitForm(obj=h)
    if form.validate_on_submit():
        h.name = form.name.data
        h.description = form.description.data
        h.frequency = form.frequency.data
        db.session.commit()
        flash("Habit updated.", "success")
        return redirect(url_for("routes.index"))
    return render_template("add_edit_habit.html", form=form, title="Edit Habit")

# --- delete habit ---
@bp.route("/habit/<int:habit_id>/delete", methods=["POST"])
@login_required
def delete_habit(habit_id):
    h = Habit.query.get_or_404(habit_id)
    if h.owner != current_user:
        abort(403)
    db.session.delete(h)
    db.session.commit()
    flash("Habit deleted.", "info")
    return redirect(url_for("routes.index"))

# --- mark complete/uncomplete ---
@bp.route("/habit/<int:habit_id>/toggle", methods=["POST"])
@login_required
def toggle_habit(habit_id):
    h = Habit.query.get_or_404(habit_id)
    if h.owner != current_user:
        abort(403)
    today = date.today()
    existing = h.logs.filter_by(date_completed=today).first()
    if existing:
        db.session.delete(existing)
        db.session.commit()
        flash(f"Marked '{h.name}' incomplete for {today}.", "warning")
        return redirect(url_for("routes.index"))
    else:
        log = HabitLog(habit_id=h.id, date_completed=today)
        db.session.add(log)
        try:
            db.session.commit()
            flash(f"Marked '{h.name}' complete for {today}.", "success")
        except IntegrityError:
            db.session.rollback()
            flash("Already marked.", "info")
    return redirect(url_for("routes.index"))

# --- view habit details & history ---
@bp.route("/habit/<int:habit_id>")
@login_required
def view_habit(habit_id):
    h = Habit.query.get_or_404(habit_id)
    if h.owner != current_user:
        abort(403)
    logs = h.logs.order_by(HabitLog.date_completed.desc()).limit(60).all()
    # simple streak calculation (consecutive days including today)
    streak = 0
    from datetime import timedelta
    check_day = date.today()
    while True:
        if h.logs.filter_by(date_completed=check_day).first():
            streak += 1
            check_day -= timedelta(days=1)
        else:
            break
    return render_template("view_habit.html", habit=h, logs=logs, streak=streak)

# --- profile ---
@bp.route("/profile")
@login_required
def profile():
    return render_template("profile.html")
