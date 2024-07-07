import unittest
from app import create_app
from models import User, Organization, db

class UserRegistrationLoginTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(test=True)
        with self.app.app_context():
            # Create tables
            db.create_all()
        from views import app_views
        self.app.register_blueprint(app_views)
        self.client = self.app.test_client()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_register_user_success_with_default_organization(self):
        response = self.client.post('/register', json={
            'firstName': 'John',
            'lastName': 'Doe',
            'email': 'john.doe@example.com',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('accessToken', data)
        self.assertEqual(data['user']['firstName'], 'John')
        user = User.query.filter_by(email='john.doe@example.com').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.organizations[0].name, "John's Organisation")

    def test_login_user_success(self):
        # First, register a user
        self.client.post('/register', json={
            'firstName': 'Jane',
            'lastName': 'Doe',
            'email': 'jane.doe@example.com',
            'password': 'password123'
        })
        # Then, try to log in
        response = self.client.post('/login', json={
            'email': 'jane.doe@example.com',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('accessToken', data)
        self.assertEqual(data['user']['email'], 'jane.doe@example.com')

    def test_register_user_fail_missing_fields(self):
        required_fields = ['firstName', 'lastName', 'email', 'password']
        for field in required_fields:
            payload = {
                'firstName': 'Test',
                'lastName': 'User',
                'email': 'test.user@example.com',
                'password': 'password123'
            }
            payload.pop(field)
            response = self.client.post('/register', json=payload)
            self.assertEqual(response.status_code, 422)
            data = response.get_json()
            self.assertIn('errors', data)
            self.assertTrue(any(error['field'] == field for error in data['errors']))

    def test_register_user_fail_duplicate_email(self):
        # Register a user
        self.client.post('/register', json={
            'firstName': 'Test',
            'lastName': 'User',
            'email': 'test.user@example.com',
            'password': 'password123'
        })
        # Try to register another user with the same email
        response = self.client.post('/register', json={
            'firstName': 'Test2',
            'lastName': 'User2',
            'email': 'test.user@example.com',
            'password': 'password1234'
        })
        self.assertEqual(response.status_code, 422)
        data = response.get_json()
        self.assertIn('errors', data)
        self.assertTrue(any(error['message'] == 'Duplicate email' for error in data['errors']))

if __name__ == '__main__':
    unittest.main()