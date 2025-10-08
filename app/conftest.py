import pytest
import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app import create_app, db
from app.models import User, Habit, HabitLog


@pytest.fixture(scope='function')
def app():
    """Create application for the tests."""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SECRET_KEY'] = 'test-secret-key'
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create test CLI runner."""
    return app.test_cli_runner()


@pytest.fixture
def test_user(app):
    """Create a test user."""
    with app.app_context():
        user = User(
            name='Test User',
            email='test@example.com'
        )
        user.set_password('testpass123')
        db.session.add(user)
        db.session.commit()
        return user


@pytest.fixture
def authenticated_user(client, test_user):
    """Create an authenticated test user session."""
    client.post('/login', data={
        'email': 'test@example.com',
        'password': 'testpass123'
    }, follow_redirects=True)
    return test_user


@pytest.fixture
def test_habit(app, test_user):
    """Create a test habit."""
    with app.app_context():
        habit = Habit(
            name='Test Habit',
            description='Test description',
            frequency='daily',
            user_id=test_user.id
        )
        db.session.add(habit)
        db.session.commit()
        return habit