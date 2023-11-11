import unittest
from app import app
import json

class TestYourFlaskApp(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()

    def test_login_google_valid_token(self):
        # Mock a valid Google login request with a valid token and client_id
        valid_token = 'valid_google_token'
        client_id = 'your_client_id'
        data = {
            'token': valid_token,
            'client_id': client_id
        }
        response = self.app.post('/login-google', json=data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'UserEmail', response.data)  # Change 'UserEmail' to the expected response key

    def test_login_google_invalid_token(self):
        # Mock a Google login request with an invalid token
        invalid_token = 'invalid_google_token'
        client_id = 'your_client_id'
        data = {
            'token': invalid_token,
            'client_id': client_id
        }
        response = self.app.post('/login-google', json=data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Email not available', response.data)  # Adjust the expected response

    def test_login_valid_credentials(self):
        # Mock a login request with valid email and password
        valid_credentials = {
            'email': 'user@example.com',
            'password': 'password123'
        }
        response = self.app.post('/login', json=valid_credentials)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'token', response.data)  # Adjust the expected response

    def test_login_invalid_credentials(self):
        # Mock a login request with invalid email and password
        invalid_credentials = {
            'email': 'user@example.com',
            'password': 'wrong_password'
        }
        response = self.app.post('/login', json=invalid_credentials)
        self.assertEqual(response.status_code, 401)
        self.assertIn(b'Invalid credentials', response.data)  # Adjust the expected response

    def test_register_valid_user(self):
        # Mock a registration request with a valid email and password
        valid_user = {
            'email': 'newuser@example.com',
            'password': 'password123'
        }
        response = self.app.post('/register', json=valid_user)
        self.assertEqual(response.status_code, 201)
        self.assertIn(b'email', response.data)  # Adjust the expected response

    def test_register_existing_user(self):
        # Mock a registration request with an email that already exists
        existing_user = {
            'email': 'user@example.com',
            'password': 'password123'
        }
        response = self.app.post('/register', json=existing_user)
        self.assertEqual(response.status_code, 409)
        self.assertIn(b'User with the same email already exists', response.data)  # Adjust the expected response

    def test_register_invalid_email(self):
        # Mock a registration request with an invalid email format
        invalid_user = {
            'email': 'invalid-email',
            'password': 'password123'
        }
        response = self.app.post('/register', json=invalid_user)
        self.assertEqual(response.status_code, 422)
        self.assertIn(b'Invalid email format', response.data)  # Adjust the expected response

if __name__ == '__main__':
    unittest.main()
