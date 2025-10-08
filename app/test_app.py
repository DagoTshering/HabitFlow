"""
Tests for the HabitFlow application
Tests authentication, habit CRUD operations, and habit tracking
"""
import pytest
from datetime import date, timedelta
from models import User, Habit, HabitLog


class TestAuthentication:
    """Test user authentication features"""
    
    def test_register_user(self, client):
        """Test user registration"""
        response = client.post('/signup', data={
            'name': 'New User',
            'email': 'newuser@example.com',
            'password': 'newpass123',
            'confirm': 'newpass123'
        }, follow_redirects=True)
        assert response.status_code == 200
        
        # Check user was created
        user = User.query.filter_by(email='newuser@example.com').first()
        assert user is not None
        assert user.name == 'New User'
        assert user.check_password('newpass123')
    
    def test_register_duplicate_email(self, client, test_user):
        """Test registration with duplicate email"""
        response = client.post('/signup', data={
            'name': 'Another User',
            'email': 'test@example.com',  # Already exists
            'password': 'newpass123',
            'confirm': 'newpass123'
        })
        assert b'Email already registered' in response.data
    
    def test_login_success(self, client, test_user):
        """Test successful login"""
        response = client.post('/login', data={
            'email': 'test@example.com',
            'password': 'testpass123'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Dashboard' in response.data
    
    def test_login_invalid_credentials(self, client, test_user):
        """Test login with invalid credentials"""
        response = client.post('/login', data={
            'email': 'test@example.com',
            'password': 'wrongpass'
        })
        assert b'Invalid email or password' in response.data
    
    def test_logout(self, client, authenticated_user):
        """Test user logout"""
        response = client.get('/logout', follow_redirects=True)
        assert response.status_code == 200
        
        # Try to access protected page
        response = client.get('/dashboard')
        assert response.status_code == 302  # Redirect to login


class TestHabitManagement:
    """Test habit CRUD operations"""
    
    def test_dashboard_access(self, client, authenticated_user):
        """Test dashboard access for authenticated user"""
        response = client.get('/dashboard')
        assert response.status_code == 200
        assert b'Dashboard' in response.data
    
    def test_create_habit(self, client, authenticated_user):
        """Test habit creation"""
        response = client.post('/habits/add', data={
            'name': 'Test Habit',
            'description': 'This is a test habit',
            'frequency': 'daily'
        }, follow_redirects=True)
        assert response.status_code == 200
        
        # Check habit was created
        habit = Habit.query.filter_by(name='Test Habit').first()
        assert habit is not None
        assert habit.user_id == authenticated_user.id
        assert habit.frequency == 'daily'
    
    def test_create_habit_missing_name(self, client, authenticated_user):
        """Test habit creation without name"""
        response = client.post('/habits/add', data={
            'name': '',
            'description': 'This is a test habit',
            'frequency': 'daily'
        })
        assert b'This field is required' in response.data
    
    def test_edit_habit(self, client, authenticated_user):
        """Test habit editing"""
        # Create a habit first
        habit = Habit(
            name='Original Habit',
            description='Original description',
            frequency='daily',
            user_id=authenticated_user.id
        )
        from app import db
        db.session.add(habit)
        db.session.commit()
        
        # Edit the habit
        response = client.post(f'/habits/{habit.id}/edit', data={
            'name': 'Updated Habit',
            'description': 'Updated description',
            'frequency': 'weekly'
        }, follow_redirects=True)
        assert response.status_code == 200
        
        # Check habit was updated
        updated_habit = Habit.query.get(habit.id)
        assert updated_habit.name == 'Updated Habit'
        assert updated_habit.frequency == 'weekly'
    
    def test_delete_habit(self, client, authenticated_user):
        """Test habit deletion"""
        # Create a habit first
        habit = Habit(
            name='Habit to Delete',
            user_id=authenticated_user.id
        )
        from app import db
        db.session.add(habit)
        db.session.commit()
        habit_id = habit.id
        
        # Delete the habit
        response = client.post(f'/habits/{habit_id}/delete', follow_redirects=True)
        assert response.status_code == 200
        
        # Check habit was deleted
        deleted_habit = Habit.query.get(habit_id)
        assert deleted_habit is None


class TestHabitTracking:
    """Test habit completion tracking"""
    
    def test_toggle_habit_completion(self, client, authenticated_user):
        """Test marking habit as completed"""
        # Create a habit first
        habit = Habit(
            name='Test Tracking',
            user_id=authenticated_user.id
        )
        from app import db
        db.session.add(habit)
        db.session.commit()
        
        # Mark as completed
        response = client.post(f'/habits/{habit.id}/toggle', follow_redirects=True)
        assert response.status_code == 200
        
        # Check completion was logged
        log = HabitLog.query.filter_by(habit_id=habit.id).first()
        assert log is not None
        assert log.date_completed == date.today()
    
    def test_toggle_habit_unmark(self, client, authenticated_user):
        """Test unmarking completed habit"""
        # Create a habit with completion log
        habit = Habit(
            name='Test Unmark',
            user_id=authenticated_user.id
        )
        from app import db
        db.session.add(habit)
        db.session.commit()
        
        # Add completion log
        log = HabitLog(habit_id=habit.id, date_completed=date.today())
        db.session.add(log)
        db.session.commit()
        
        # Unmark completion
        response = client.post(f'/habits/{habit.id}/toggle', follow_redirects=True)
        assert response.status_code == 200
        
        # Check completion was removed
        log = HabitLog.query.filter_by(habit_id=habit.id).first()
        assert log is None
    
    def test_habit_completion_count(self, client, authenticated_user):
        """Test habit completion count calculation"""
        habit = Habit(
            name='Test Count',
            user_id=authenticated_user.id
        )
        from app import db
        db.session.add(habit)
        db.session.commit()
        
        # Add multiple completion logs
        for i in range(3):
            log = HabitLog(
                habit_id=habit.id,
                date_completed=date.today() - timedelta(days=i)
            )
            db.session.add(log)
        db.session.commit()
        
        assert habit.completion_count() == 3
    
    def test_habit_completed_on_method(self, client, authenticated_user):
        """Test completed_on method"""
        habit = Habit(
            name='Test Completed On',
            user_id=authenticated_user.id
        )
        from app import db
        db.session.add(habit)
        db.session.commit()
        
        # Add completion for today
        log = HabitLog(habit_id=habit.id, date_completed=date.today())
        db.session.add(log)
        db.session.commit()
        
        assert habit.completed_on(date.today()) == True
        assert habit.completed_on(date.today() - timedelta(days=1)) == False


class TestHabitViews:
    """Test habit detail views"""
    
    def test_view_habit_details(self, client, authenticated_user):
        """Test viewing habit details"""
        habit = Habit(
            name='Test Habit Details',
            description='Test description',
            frequency='daily',
            user_id=authenticated_user.id
        )
        from app import db
        db.session.add(habit)
        db.session.commit()
        
        # Add some completion logs
        for i in range(2):
            log = HabitLog(
                habit_id=habit.id,
                date_completed=date.today() - timedelta(days=i)
            )
            db.session.add(log)
        db.session.commit()
        
        response = client.get(f'/habits/{habit.id}')
        assert response.status_code == 200
        assert b'Test Habit Details' in response.data
        assert b'Test description' in response.data
        assert b'Current streak' in response.data


class TestSecurity:
    """Test security measures"""
    
    def test_unauthorized_dashboard_access(self, client):
        """Test accessing dashboard without authentication"""
        response = client.get('/dashboard')
        assert response.status_code == 302  # Redirect to login
    
    def test_unauthorized_habit_access(self, client, test_user):
        """Test accessing another user's habit"""
        # Create a habit for test_user
        habit = Habit(
            name='Private Habit',
            user_id=test_user.id
        )
        from app import db
        db.session.add(habit)
        db.session.commit()
        
        # Create and login as different user
        other_user = User(
            name='Other User',
            email='other@example.com'
        )
        other_user.set_password('otherpass')
        db.session.add(other_user)
        db.session.commit()
        
        client.post('/login', data={
            'email': 'other@example.com',
            'password': 'otherpass'
        })
        
        # Try to access the habit
        response = client.get(f'/habits/{habit.id}')
        assert response.status_code == 404  # Should not be found
    
    def test_unauthorized_habit_edit(self, client, test_user):
        """Test editing another user's habit"""
        # Create a habit for test_user
        habit = Habit(
            name='Private Habit',
            user_id=test_user.id
        )
        from app import db
        db.session.add(habit)
        db.session.commit()
        
        # Create and login as different user
        other_user = User(
            name='Other User',
            email='other@example.com'
        )
        other_user.set_password('otherpass')
        db.session.add(other_user)
        db.session.commit()
        
        client.post('/login', data={
            'email': 'other@example.com',
            'password': 'otherpass'
        })
        
        # Try to edit the habit
        response = client.post(f'/habits/{habit.id}/edit', data={
            'name': 'Hacked Habit'
        })
        assert response.status_code == 404  # Should not be found


class TestHabitConstraints:
    """Test habit model constraints"""
    
    def test_unique_habit_log_constraint(self, client, authenticated_user):
        """Test unique constraint on habit logs"""
        habit = Habit(
            name='Test Constraint',
            user_id=authenticated_user.id
        )
        from app import db
        db.session.add(habit)
        db.session.commit()
        
        # Add first log
        log1 = HabitLog(habit_id=habit.id, date_completed=date.today())
        db.session.add(log1)
        db.session.commit()
        
        # Try to add duplicate log
        log2 = HabitLog(habit_id=habit.id, date_completed=date.today())
        db.session.add(log2)
        
        # This should raise an integrity error
        with pytest.raises(Exception):
            db.session.commit()
        
        db.session.rollback()


@pytest.fixture
def test_user():
    """Create a test user"""
    from app import db
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
    """Create an authenticated test user"""
    client.post('/login', data={
        'email': 'test@example.com',
        'password': 'testpass123'
    })
    return test_user


if __name__ == '__main__':
    pytest.main(['-v'])