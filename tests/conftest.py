"""
Pytest configuration and shared fixtures for HabitFlow tests.
"""
import pytest
from datetime import date
from app import create_app, db
from app.models import User, Habit, HabitLog


@pytest.fixture(scope='session')
def app():
    """Create application for the tests."""
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False,
        "SECRET_KEY": "test-secret-key-for-testing"
    })
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def _db(app):
    """Create a fresh database for each test."""
    with app.app_context():
        db.create_all()
        yield db
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app, _db):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """A test CLI runner for the app."""
    return app.test_cli_runner()


@pytest.fixture
def test_user(app, _db):
    """Create a test user in the database."""
    with app.app_context():
        user = User(name="Test User", email="test@example.com")
        user.set_password("testpass123")
        db.session.add(user)
        db.session.commit()
        
        # Refresh to get ID
        db.session.refresh(user)
        user_id = user.id
        
        yield user
        
        # Cleanup
        user = db.session.get(User, user_id)
        if user:
            db.session.delete(user)
            db.session.commit()


@pytest.fixture
def logged_in_client(client, test_user):
    """A test client with a logged-in user."""
    client.post("/login", data={
        "email": "test@example.com",
        "password": "testpass123"
    })
    return client


@pytest.fixture
def sample_habit(app, test_user, _db):
    """Create a sample habit for testing."""
    with app.app_context():
        habit = Habit(
            user_id=test_user.id,
            name="Sample Habit",
            description="A test habit",
            frequency="daily"
        )
        db.session.add(habit)
        db.session.commit()
        
        db.session.refresh(habit)
        habit_id = habit.id
        
        yield habit
        
        # Cleanup
        habit = db.session.get(Habit, habit_id)
        if habit:
            db.session.delete(habit)
            db.session.commit()


@pytest.fixture
def completed_habit(app, sample_habit, _db):
    """Create a habit that's been completed today."""
    with app.app_context():
        log = HabitLog(
            habit_id=sample_habit.id,
            date_completed=date.today()
        )
        db.session.add(log)
        db.session.commit()
        
        yield sample_habit