import pytest
from app import create_app, db
from models import User, Habit, HabitLog


@pytest.fixture(scope='module')
def test_client():
    """Create test client"""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()


@pytest.fixture
def init_database(test_client):
    """Initialize database for tests"""
    # Create all tables
    db.create_all()
    
    yield db
    
    # Clean up after tests
    db.session.remove()
    db.drop_all()


@pytest.fixture
def test_user(init_database):
    """Create a test user"""
    user = User(
        name='Test User',
        email='test@example.com'
    )
    user.set_password('testpass123')
    db.session.add(user)
    db.session.commit()
    return user