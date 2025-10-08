from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length

class SignupForm(FlaskForm):
    name = StringField("Full name", validators=[DataRequired(), Length(max=120)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    confirm = PasswordField("Confirm password", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Sign Up")

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Log In")

class HabitForm(FlaskForm):
    name = StringField("Habit name", validators=[DataRequired(), Length(max=140)])
    description = TextAreaField("Description", validators=[Length(max=1000)])
    frequency = SelectField("Frequency", choices=[("daily", "Daily"), ("weekly", "Weekly")], validators=[DataRequired()])
    submit = SubmitField("Save")
