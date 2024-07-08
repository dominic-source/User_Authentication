import unittest
import uuid
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
        response = self.client.post('/auth/register', json={
            'firstName': 'John',
            'lastName': 'Doe',
            'email': 'john.doe@example.com',
            'password': 'password123'
        })

        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertIn('accessToken', data['data'])
        self.assertEqual(data['data']['user']['firstName'], 'John')
        with self.app.app_context():
            user = User.query.filter_by(email='john.doe@example.com').first()
            # filter out organizations
            self.assertIsNotNone(user)
            self.assertEqual(user.organizations[0].name, "John's Organisation")

    def test_login_user_success(self):
        # First, register a user
        self.client.post('/auth/register', json={
            'firstName': 'Jane',
            'lastName': 'Doe',
            'email': 'jane.doe@example.com',
            'password': 'password123'
        })
        # Then, try to log in
        response = self.client.post('/auth/login', json={
            'email': 'jane.doe@example.com',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('accessToken', data['data'])
        expected = {
            "user": {
                'firstName': 'Jane',
                'lastName': 'Doe',
                'email': 'jane.doe@example.com',
                'password': 'password123'
            }
        }
        self.assertEqual(data['data']['user']['firstName'], 'Jane')
        self.assertEqual(data['data']['user']['lastName'], 'Doe')
        self.assertEqual(data['data']['user']['email'], 'jane.doe@example.com')
        self.assertNotIn('password', data['data']['user'])
        self.assertIn('userId', data['data']['user'])

    def test_login_user_unsuccess(self):
        # First, register a user
        self.client.post('/auth/register', json={
            'firstName': 'Jane',
            'lastName': 'Doe',
            'email': 'jane.doe@example.com',
            'password': 'password123'
        })
        # Then, try to log in
        response = self.client.post('/auth/login', json={
            'email': 'jane.doe@example.com',
            'password': 'password12'
        })
        self.assertEqual(response.status_code, 401)
        data = response.get_json()
        expected = {
            "status": "Bad request",
            "message": "Authentication failed",
            "statusCode": 401
        }
        self.assertEqual(data, expected)

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
            response = self.client.post('/auth/register', json=payload)
            self.assertEqual(response.status_code, 422)
            data = response.get_json()
            self.assertIn('errors', data)
            self.assertTrue(any(error['field'] == field for error in data['errors']))

    def test_register_user_fail_duplicate_email(self):
        # Register a user
        self.client.post('/auth/register', json={
            'firstName': 'Test',
            'lastName': 'User',
            'email': 'test.user@example.com',
            'password': 'password123'
        })
        # Try to register another user with the same email
        response = self.client.post('/auth/register', json={
            'firstName': 'Test2',
            'lastName': 'User2',
            'email': 'test.user@example.com',
            'password': 'password1234'
        })
        self.assertEqual(response.status_code, 422)
        data = response.get_json()
        self.assertIn('errors', data)
        self.assertTrue(any(error['message'] == 'Email already exists' for error in data['errors']))



class UserOrganizationTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(test=True)
        with self.app.app_context():
            # Create tables
            db.create_all()
        from views import app_views
        self.app.register_blueprint(app_views)
        self.client = self.app.test_client()
        
        # First, register a user
        self.client.post('/auth/register', json={
            'firstName': 'John',
            'lastName': 'Doe',
            'email': 'john.doe@example.com',
            'password': 'password123'
        })
        
        # First, register a user
        response = self.client.post('/auth/register', json={
            'firstName': 'John2',
            'lastName': 'Doe2',
            'email': 'john.doe2@example.com',
            'password': 'password123'
        })
        self.userId = response.get_json()['data']['user']['userId']

        # Then, try to log in
        resp = self.client.post('/auth/login', json={
            'email': 'john.doe@example.com',
            'password': 'password123'
        })
        data = resp.get_json()
        self.accessToken= data['data']['accessToken']

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_create_organization_success(self):
        # Then, create an organization and add authorization header with the access token
        response = self.client.post('/api/organisations', json={
            'name': 'Johns Company'
        }, headers={'Authorization': f'Bearer {self.accessToken}'})
        
        data = response.get_json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(data['data']['name'], 'Johns Company')
        self.assertEqual(data['data']['description'], None)
        self.assertIn('orgId', data['data'])
        with self.app.app_context():
            user = User.query.filter_by(firstName='John').first()
            self.assertIsNotNone(user)

    # Organisation - Ensure users can’t see data from organisations they don’t have access to.
    def test_user_not_found(self):
        response3 = self.client.post('/api/organisations/:orgId/users', json={
                            "userId": "fakecredentials"
                            }, headers={"Authorization": f"Bearer {self.accessToken}"})
        data = response3.get_json()
        self.assertEqual(response3.status_code, 404)
        self.assertIn('The User was not found', data['message'])

    # def test_organization_not_found(self):
    #     # Assume a valid user session setup
    #     response4 = self.client.post('/api/organisations/invalid_org_id/users', json={
    #             "userId": "fakecredentials"
    #         }, headers={"Authorization": f"Bearer {self.accessToken}"})
    #     data = response4.get_json()        
    #     self.assertEqual(response4.status_code, 404)
    #     self.assertIn('Organization not found', data['message'])

    # def test_adding_user_not_found(self):
    #     # Assume a valid user and organization setup
    #     response3 = self.client.post('/api/organisations/valid_org_id/users', json={
    #         'userId': 'nvalid_user_id'}, headers={"Authorization": f"Bearer {self.accessToken}"})
    #     data = response3.get_json()
    #     self.assertEqual(response3.status_code, 404)
    #     self.assertIn('The User was not found', data['message'])

    # def test_successful_addition(self):
    #     # Assume a valid user, organization, and user to add setup
    #     with self.app.app_context():
    #         user = User.query.filter_by(firstName='John').first()
    #         self.orgId = user.organizations[0].orgId
    #         response3 = self.client.post(f'/api/organisations/{self.orgId}/users', json={
    #             "userId": self.userId }, headers={"Authorization": f"Bearer {self.accessToken}"})
    #     data = response3.get_json()
    #     self.assertEqual(response3.status_code, 200)
    #     self.assertIn('User added to organization successfully', data['message'])

    # def test_unauthorized_access(self):
    #     # Assume a user session setup that does not belong to the organization
    #     with self.app.app_context():
    #         organization = Organization(orgId=str(uuid.uuid4()), name='ortherOrganization', description='description')
    #         db.session.add(organization)
    #         db.session.commit()
    #         url = f'/api/organisations/{organization.orgId}/users'
    #         response2 = self.client.post(url,
    #                                 json={"userId": self.userId},
    #                                 headers={"Authorization": f"Bearer {self.accessToken}"})
    #     data = response2.get_json()
    #     self.assertEqual(response2.status_code, 404)
    #     self.assertIn('You are not in this organization', data['message'])


if __name__ == '__main__':
    unittest.main()