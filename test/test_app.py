"""
Comprehensive test suite for HabitFlow application.
Tests authentication, habit management, and core functionality.
"""
import pytest
from datetime import date, timedelta
from app import create_app, db
from app.models import User, Habit, HabitLog


@pytest.fixture(scope='function')
def app():
    """Create and configure a test app instance."""
    test_app = create_app()
    test_app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False,
        "SECRET_KEY": "test-secret-key"
    })
    
    with test_app.app_context():
        db.create_all()
        yield test_app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Test client for the app."""
    return app.test_client()


@pytest.fixture
def test_user(app):
    """Create a test user."""
    user = User(name="Test User", email="test@example.com")
    user.set_password("testpass123")
    db.session.add(user)
    db.session.commit()
    return user


# ============================================================================
# Authentication Tests
# ============================================================================

class TestAuthentication:
    """Test user authentication flows."""
    
    def test_signup_page_loads(self, client):
        """Test signup page renders correctly."""
        response = client.get("/signup")
        assert response.status_code == 200
        assert b"Sign up" in response.data or b"Create Account" in response.data
    
    def test_successful_signup(self, client):
        """Test user can sign up successfully."""
        response = client.post("/signup", data={
            "name": "New User",
            "email": "newuser@example.com",
            "password": "password123",
            "confirm": "password123"
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b"Account created" in response.data or b"please log in" in response.data
        
        # Verify user was created in database
        user = User.query.filter_by(email="newuser@example.com").first()
        assert user is not None
        assert user.name == "New User"
    
    def test_signup_duplicate_email(self, client, test_user):
        """Test signup fails with duplicate email."""
        response = client.post("/signup", data={
            "name": "Another User",
            "email": "test@example.com",
            "password": "password123",
            "confirm": "password123"
        }, follow_redirects=True)
        
        assert b"already registered" in response.data.lower() or b"already" in response.data.lower()
    
    def test_login_page_loads(self, client):
        """Test login page renders correctly."""
        response = client.get("/login")
        assert response.status_code == 200
        assert b"Login" in response.data or b"Sign in" in response.data
    
    def test_successful_login(self, client, test_user):
        """Test user can log in successfully."""
        response = client.post("/login", data={
            "email": "test@example.com",
            "password": "testpass123"
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b"Logged in" in response.data or b"Dashboard" in response.data
    
    def test_login_invalid_email(self, client):
        """Test login fails with invalid email."""
        response = client.post("/login", data={
            "email": "nonexistent@example.com",
            "password": "wrongpass"
        }, follow_redirects=True)
        
        assert b"Invalid" in response.data
    
    def test_login_invalid_password(self, client, test_user):
        """Test login fails with wrong password."""
        response = client.post("/login", data={
            "email": "test@example.com",
            "password": "wrongpassword"
        }, follow_redirects=True)
        
        assert b"Invalid" in response.data
    
    def test_logout(self, client, test_user):
        """Test user can log out."""
        # Login first
        client.post("/login", data={
            "email": "test@example.com",
            "password": "testpass123"
        })
        
        # Then logout
        response = client.get("/logout", follow_redirects=True)
        assert response.status_code == 200
        assert b"Logged out" in response.data or b"Login" in response.data


# ============================================================================
# Dashboard Tests
# ============================================================================

class TestDashboard:
    """Test dashboard functionality."""
    
    def test_dashboard_requires_login(self, client):
        """Test dashboard redirects to login when not authenticated."""
        response = client.get("/dashboard", follow_redirects=True)
        assert b"Login" in response.data or b"Sign in" in response.data
    
    def test_dashboard_loads_when_logged_in(self, client, test_user):
        """Test dashboard loads for logged-in users."""
        client.post("/login", data={
            "email": "test@example.com",
            "password": "testpass123"
        })
        
        response = client.get("/dashboard")
        assert response.status_code == 200
        assert b"Dashboard" in response.data
    
    def test_dashboard_shows_empty_state(self, client, test_user):
        """Test dashboard shows empty state when no habits exist."""
        client.post("/login", data={
            "email": "test@example.com",
            "password": "testpass123"
        })
        
        response = client.get("/dashboard")
        assert b"No habits" in response.data or b"first habit" in response.data
    
    def test_root_redirects_to_dashboard(self, client, test_user):
        """Test root URL redirects to dashboard when logged in."""
        client.post("/login", data={
            "email": "test@example.com",
            "password": "testpass123"
        })
        
        response = client.get("/", follow_redirects=False)
        assert response.status_code in [200, 302]


# ============================================================================
# Habit CRUD Tests
# ============================================================================

class TestHabitManagement:
    """Test habit creation, reading, updating, and deletion."""
    
    def test_add_habit_page_requires_login(self, client):
        """Test add habit page requires authentication."""
        response = client.get("/habit/new", follow_redirects=True)
        assert b"Login" in response.data
    
    def test_add_habit_page_loads(self, client, test_user):
        """Test add habit page loads correctly."""
        client.post("/login", data={
            "email": "test@example.com",
            "password": "testpass123"
        })
        
        response = client.get("/habit/new")
        assert response.status_code == 200
        assert b"Add" in response.data or b"Habit" in response.data
    
    def test_create_habit_successfully(self, client, test_user):
        """Test creating a new habit."""
        client.post("/login", data={
            "email": "test@example.com",
            "password": "testpass123"
        })
        
        response = client.post("/habit/new", data={
            "name": "Morning Meditation",
            "description": "Meditate for 10 minutes",
            "frequency": "daily"
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b"Habit added" in response.data or b"Morning Meditation" in response.data
        
        # Verify habit was created in database
        habit = Habit.query.filter_by(name="Morning Meditation").first()
        assert habit is not None
        assert habit.description == "Meditate for 10 minutes"
        assert habit.frequency == "daily"
    
    def test_edit_habit_page_loads(self, client, test_user):
        """Test edit habit page loads correctly."""
        # Login
        client.post("/login", data={
            "email": "test@example.com",
            "password": "testpass123"
        })
        
        # Create a habit first
        habit = Habit(
            user_id=test_user.id,
            name="Test Habit",
            description="Test Description",
            frequency="daily"
        )
        db.session.add(habit)
        db.session.commit()
        habit_id = habit.id
        
        response = client.get(f"/habit/{habit_id}/edit")
        assert response.status_code == 200
        assert b"Edit" in response.data or b"Test Habit" in response.data
    
    def test_update_habit_successfully(self, client, test_user):
        """Test updating an existing habit."""
        # Login
        client.post("/login", data={
            "email": "test@example.com",
            "password": "testpass123"
        })
        
        # Create a habit first
        habit = Habit(
            user_id=test_user.id,
            name="Original Name",
            description="Original Description",
            frequency="daily"
        )
        db.session.add(habit)
        db.session.commit()
        habit_id = habit.id
        
        response = client.post(f"/habit/{habit_id}/edit", data={
            "name": "Updated Name",
            "description": "Updated Description",
            "frequency": "weekly"
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b"Habit updated" in response.data or b"Updated Name" in response.data
        
        # Verify habit was updated in database
        habit = Habit.query.get(habit_id)
        assert habit.name == "Updated Name"
        assert habit.description == "Updated Description"
        assert habit.frequency == "weekly"
    
    def test_delete_habit_successfully(self, client, test_user):
        """Test deleting a habit."""
        # Login
        client.post("/login", data={
            "email": "test@example.com",
            "password": "testpass123"
        })
        
        # Create a habit first
        habit = Habit(
            user_id=test_user.id,
            name="Habit to Delete",
            description="Will be deleted",
            frequency="daily"
        )
        db.session.add(habit)
        db.session.commit()
        habit_id = habit.id
        
        response = client.post(f"/habit/{habit_id}/delete", follow_redirects=True)
        
        assert response.status_code == 200
        assert b"Habit deleted" in response.data
        
        # Verify habit was deleted from database
        habit = Habit.query.get(habit_id)
        assert habit is None
    
    def test_cannot_edit_other_users_habit(self, client):
        """Test user cannot edit another user's habit."""
        # Create two users
        user1 = User(name="User One", email="user1@example.com")
        user1.set_password("pass123")
        user2 = User(name="User Two", email="user2@example.com")
        user2.set_password("pass123")
        db.session.add_all([user1, user2])
        db.session.commit()
        
        # Create habit for user1
        habit = Habit(
            user_id=user1.id,
            name="User1's Habit",
            description="Private habit",
            frequency="daily"
        )
        db.session.add(habit)
        db.session.commit()
        habit_id = habit.id
        
        # Login as user2
        client.post("/login", data={
            "email": "user2@example.com",
            "password": "pass123"
        })
        
        # Try to edit user1's habit
        response = client.get(f"/habit/{habit_id}/edit")
        assert response.status_code == 403


# ============================================================================
# Habit Completion Tests
# ============================================================================

class TestHabitCompletion:
    """Test habit completion tracking functionality."""
    
    def test_mark_habit_complete(self, client, test_user):
        """Test marking a habit as complete."""
        # Login
        client.post("/login", data={
            "email": "test@example.com",
            "password": "testpass123"
        })
        
        # Create a habit
        habit = Habit(
            user_id=test_user.id,
            name="Test Habit",
            description="Test",
            frequency="daily"
        )
        db.session.add(habit)
        db.session.commit()
        habit_id = habit.id
        
        response = client.post(f"/habit/{habit_id}/toggle", follow_redirects=True)
        
        assert response.status_code == 200
        assert b"complete" in response.data.lower() or b"Marked" in response.data
        
        # Verify log was created
        log = HabitLog.query.filter_by(
            habit_id=habit_id,
            date_completed=date.today()
        ).first()
        assert log is not None
    
    def test_mark_habit_incomplete(self, client, test_user):
        """Test marking a completed habit as incomplete."""
        # Login
        client.post("/login", data={
            "email": "test@example.com",
            "password": "testpass123"
        })
        
        # Create a habit and mark it complete
        habit = Habit(
            user_id=test_user.id,
            name="Test Habit",
            description="Test",
            frequency="daily"
        )
        db.session.add(habit)
        db.session.commit()
        
        log = HabitLog(habit_id=habit.id, date_completed=date.today())
        db.session.add(log)
        db.session.commit()
        habit_id = habit.id
        
        response = client.post(f"/habit/{habit_id}/toggle", follow_redirects=True)
        
        assert response.status_code == 200
        assert b"incomplete" in response.data.lower() or b"Marked" in response.data
        
        # Verify log was deleted
        log = HabitLog.query.filter_by(
            habit_id=habit_id,
            date_completed=date.today()
        ).first()
        assert log is None
    
    def test_view_habit_details(self, client, test_user):
        """Test viewing habit details page."""
        # Login
        client.post("/login", data={
            "email": "test@example.com",
            "password": "testpass123"
        })
        
        # Create a habit with some completion logs
        habit = Habit(
            user_id=test_user.id,
            name="Detailed Habit",
            description="Habit with history",
            frequency="daily"
        )
        db.session.add(habit)
        db.session.commit()
        
        # Add some completion logs
        for i in range(3):
            log = HabitLog(
                habit_id=habit.id,
                date_completed=date.today() - timedelta(days=i)
            )
            db.session.add(log)
        db.session.commit()
        habit_id = habit.id
        
        response = client.get(f"/habit/{habit_id}")
        assert response.status_code == 200
        assert b"Detailed Habit" in response.data
        assert b"Habit with history" in response.data
        assert b"Streak" in response.data or b"streak" in response.data


# ============================================================================
# Model Tests
# ============================================================================

class TestModels:
    """Test database models."""
    
    def test_user_password_hashing(self):
        """Test user password is properly hashed."""
        user = User(name="Test", email="test@example.com")
        user.set_password("mypassword")
        
        assert user.password_hash != "mypassword"
        assert user.check_password("mypassword")
        assert not user.check_password("wrongpassword")
    
    def test_habit_completed_on_method(self, test_user):
        """Test habit's completed_on method."""
        habit = Habit(
            user_id=test_user.id,
            name="Test Habit",
            frequency="daily"
        )
        db.session.add(habit)
        db.session.commit()
        
        today = date.today()
        yesterday = today - timedelta(days=1)
        
        # Not completed yet
        assert not habit.completed_on(today)
        
        # Mark as completed today
        log = HabitLog(habit_id=habit.id, date_completed=today)
        db.session.add(log)
        db.session.commit()
        
        assert habit.completed_on(today)
        assert not habit.completed_on(yesterday)
    
    def test_habit_completion_count(self, test_user):
        """Test habit's completion_count method."""
        habit = Habit(
            user_id=test_user.id,
            name="Test Habit",
            frequency="daily"
        )
        db.session.add(habit)
        db.session.commit()
        
        assert habit.completion_count() == 0
        
        # Add some completions
        for i in range(5):
            log = HabitLog(
                habit_id=habit.id,
                date_completed=date.today() - timedelta(days=i)
            )
            db.session.add(log)
        db.session.commit()
        
        assert habit.completion_count() == 5
    
    def test_habit_cascade_delete(self, test_user):
        """Test that deleting a habit deletes its logs."""
        habit = Habit(
            user_id=test_user.id,
            name="Test Habit",
            frequency="daily"
        )
        db.session.add(habit)
        db.session.commit()
        
        # Add some logs
        for i in range(3):
            log = HabitLog(
                habit_id=habit.id,
                date_completed=date.today() - timedelta(days=i)
            )
            db.session.add(log)
        db.session.commit()
        
        habit_id = habit.id
        
        # Verify logs exist
        assert HabitLog.query.filter_by(habit_id=habit_id).count() == 3
        
        # Delete habit
        db.session.delete(habit)
        db.session.commit()
        
        # Verify logs were also deleted
        assert HabitLog.query.filter_by(habit_id=habit_id).count() == 0


# ============================================================================
# Profile Tests
# ============================================================================

class TestProfile:
    """Test user profile functionality."""
    
    def test_profile_page_requires_login(self, client):
        """Test profile page requires authentication."""
        response = client.get("/profile", follow_redirects=True)
        assert b"Login" in response.data
    
    def test_profile_page_loads(self, client, test_user):
        """Test profile page loads for logged-in users."""
        client.post("/login", data={
            "email": "test@example.com",
            "password": "testpass123"
        })
        
        response = client.get("/profile")
        assert response.status_code == 200
        assert b"Profile" in response.data
        assert b"Test User" in response.data or b"test@example.com" in response.data