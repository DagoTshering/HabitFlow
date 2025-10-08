"""
Tests for the HabitFlow application
Tests authentication, habit CRUD operations, and habit tracking
"""
import pytest
from datetime import date, timedelta


class TestAuthentication:
    """Test user authentication features"""
    
    def test_register_user(self, client, app):
        """Test user registration"""
        with app.app_context():
            response = client.post('/signup', data={
                'name': 'New User',
                'email': 'newuser@example.com',
                'password': 'newpass123',
                'confirm': 'newpass123'
            }, follow_redirects=True)
            assert response.status_code == 200
            
            # Check user was created
            from app.models import User
            user = User.query.filter_by(email='newuser@example.com').first()
            assert user is not None
            assert user.name == 'New User'
    
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
        assert response.status_code == 200
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
    
    def test_create_habit(self, client, authenticated_user, app):
        """Test habit creation"""
        with app.app_context():
            response = client.post('/add_habit', data={
                'name': 'Test Habit',
                'description': 'This is a test habit',
                'frequency': 'daily'
            }, follow_redirects=True)
            assert response.status_code == 200
            
            # Check habit was created
            from app.models import Habit
            habit = Habit.query.filter_by(name='Test Habit').first()
            assert habit is not None
            assert habit.user_id == authenticated_user.id
            assert habit.frequency == 'daily'
    
    def test_create_habit_missing_name(self, client, authenticated_user):
        """Test habit creation without name"""
        response = client.post('/add_habit', data={
            'name': '',
            'description': 'This is a test habit',
            'frequency': 'daily'
        })
        assert response.status_code == 200
        assert b'This field is required' in response.data
    
    def test_edit_habit(self, client, authenticated_user, app, test_habit):
        """Test habit editing"""
        with app.app_context():
            # Edit the habit
            response = client.post(f'/edit_habit/{test_habit.id}', data={
                'name': 'Updated Habit',
                'description': 'Updated description',
                'frequency': 'weekly'
            }, follow_redirects=True)
            assert response.status_code == 200
            
            # Check habit was updated
            from app.models import Habit
            updated_habit = Habit.query.get(test_habit.id)
            assert updated_habit.name == 'Updated Habit'
            assert updated_habit.frequency == 'weekly'
    
    def test_delete_habit(self, client, authenticated_user, app, test_habit):
        """Test habit deletion"""
        with app.app_context():
            habit_id = test_habit.id
            
            # Delete the habit
            response = client.post(f'/delete_habit/{habit_id}', follow_redirects=True)
            assert response.status_code == 200
            
            # Check habit was deleted
            from app.models import Habit
            deleted_habit = Habit.query.get(habit_id)
            assert deleted_habit is None


class TestHabitTracking:
    """Test habit completion tracking"""
    
    def test_toggle_habit_completion(self, client, authenticated_user, app, test_habit):
        """Test marking habit as completed"""
        with app.app_context():
            # Mark as completed
            response = client.post(f'/toggle_habit/{test_habit.id}', follow_redirects=True)
            assert response.status_code == 200
            
            # Check completion was logged
            from app.models import HabitLog
            log = HabitLog.query.filter_by(habit_id=test_habit.id).first()
            assert log is not None
            assert log.date_completed == date.today()
    
    def test_toggle_habit_unmark(self, client, authenticated_user, app, test_habit):
        """Test unmarking completed habit"""
        with app.app_context():
            from app.models import HabitLog, db
            
            # Add completion log
            log = HabitLog(habit_id=test_habit.id, date_completed=date.today())
            db.session.add(log)
            db.session.commit()
            
            # Unmark completion
            response = client.post(f'/toggle_habit/{test_habit.id}', follow_redirects=True)
            assert response.status_code == 200
            
            # Check completion was removed
            log = HabitLog.query.filter_by(habit_id=test_habit.id).first()
            assert log is None
    
    def test_habit_completion_count(self, app, test_habit):
        """Test habit completion count calculation"""
        with app.app_context():
            from app.models import HabitLog, db
            
            # Add multiple completion logs
            for i in range(3):
                log = HabitLog(
                    habit_id=test_habit.id,
                    date_completed=date.today() - timedelta(days=i)
                )
                db.session.add(log)
            db.session.commit()
            
            assert test_habit.completion_count() == 3
    
    def test_habit_completed_on_method(self, app, test_habit):
        """Test completed_on method"""
        with app.app_context():
            from app.models import HabitLog, db
            
            # Add completion for today
            log = HabitLog(habit_id=test_habit.id, date_completed=date.today())
            db.session.add(log)
            db.session.commit()
            
            assert test_habit.completed_on(date.today()) == True
            assert test_habit.completed_on(date.today() - timedelta(days=1)) == False


class TestHabitViews:
    """Test habit detail views"""
    
    def test_view_habit_details(self, client, authenticated_user, test_habit, app):
        """Test viewing habit details"""
        with app.app_context():
            from app.models import HabitLog, db
            
            # Add some completion logs
            for i in range(2):
                log = HabitLog(
                    habit_id=test_habit.id,
                    date_completed=date.today() - timedelta(days=i)
                )
                db.session.add(log)
            db.session.commit()
            
            response = client.get(f'/view_habit/{test_habit.id}')
            assert response.status_code == 200
            assert b'Test Habit' in response.data
            assert b'Test description' in response.data


class TestSecurity:
    """Test security measures"""
    
    def test_unauthorized_dashboard_access(self, client):
        """Test accessing dashboard without authentication"""
        response = client.get('/dashboard')
        assert response.status_code == 302  # Redirect to login
    
    def test_unauthorized_habit_access(self, client, app):
        """Test accessing another user's habit"""
        with app.app_context():
            from app.models import User, Habit, db
            
            # Create first user and habit
            user1 = User(name='User 1', email='user1@example.com')
            user1.set_password('pass123')
            db.session.add(user1)
            
            habit = Habit(name='Private Habit', user_id=user1.id)
            db.session.add(habit)
            db.session.commit()
            
            # Create second user
            user2 = User(name='User 2', email='user2@example.com')
            user2.set_password('pass123')
            db.session.add(user2)
            db.session.commit()
            
            # Login as second user
            client.post('/login', data={
                'email': 'user2@example.com',
                'password': 'pass123'
            })
            
            # Try to access the first user's habit
            response = client.get(f'/view_habit/{habit.id}')
            assert response.status_code == 404  # Should not be found


if __name__ == '__main__':
    pytest.main(['-v'])