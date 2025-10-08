import pytest
from app import create_app, db
from app.models import User, Habit

@pytest.fixture
def client():
    # Create a test app
    app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"})
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()

def register_user(client, name="Test User", email="test@example.com", password="test123"):
    return client.post("/signup", data={
        "name": name,
        "email": email,
        "password": password,
        "confirm_password": password
    }, follow_redirects=True)

def login_user(client, email="test@example.com", password="test123"):
    return client.post("/login", data={
        "email": email,
        "password": password
    }, follow_redirects=True)

# --- Auth Tests ---
def test_signup_and_login(client):
    # Sign up
    rv = register_user(client)
    assert b"Account created" in rv.data

    # Log in
    rv = login_user(client)
    assert b"Logged in." in rv.data

def test_login_invalid_credentials(client):
    rv = login_user(client, email="wrong@example.com", password="wrong")
    assert b"Invalid email or password" in rv.data

# --- Dashboard Tests ---
def test_dashboard_requires_login(client):
    rv = client.get("/dashboard", follow_redirects=True)
    assert b"Login" in rv.data

def test_dashboard_access_after_login(client):
    register_user(client)
    login_user(client)
    rv = client.get("/dashboard")
    assert rv.status_code == 200
    assert b"dashboard" in rv.data.lower()

# --- Habit Tests ---
def test_add_habit(client):
    register_user(client)
    login_user(client)
    rv = client.post("/habit/new", data={
        "name": "Morning Run",
        "description": "Run 2km every morning",
        "frequency": "Daily"
    }, follow_redirects=True)
    assert b"Habit added." in rv.data

    # Check if habit exists in DB
    with client.application.app_context():
        habit = Habit.query.filter_by(name="Morning Run").first()
        assert habit is not None

def test_toggle_habit_completion(client):
    register_user(client)
    login_user(client)

    # Add habit
    client.post("/habit/new", data={
        "name": "Meditation",
        "description": "10 min mindfulness",
        "frequency": "Daily"
    }, follow_redirects=True)

    with client.application.app_context():
        habit = Habit.query.filter_by(name="Meditation").first()
        habit_id = habit.id

    # Mark habit as complete
    rv = client.post(f"/habit/{habit_id}/toggle", follow_redirects=True)
    assert b"Marked" in rv.data

    # Unmark habit
    rv = client.post(f"/habit/{habit_id}/toggle", follow_redirects=True)
    assert b"incomplete" in rv.data

def test_view_habit_page(client):
    register_user(client)
    login_user(client)

    client.post("/habit/new", data={
        "name": "Yoga",
        "description": "Stretching",
        "frequency": "Daily"
    }, follow_redirects=True)

    with client.application.app_context():
        habit = Habit.query.filter_by(name="Yoga").first()
        habit_id = habit.id

    rv = client.get(f"/habit/{habit_id}")
    assert b"Yoga" in rv.data
    assert rv.status_code == 200
