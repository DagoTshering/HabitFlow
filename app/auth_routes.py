# app/auth_routes.py
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user
from .models import User

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('habits.dashboard'))
        else:
            flash('Invalid email or password', 'danger')

    return render_template('login.html')


@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
