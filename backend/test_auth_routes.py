
import unittest

from flask_jwt_extended import decode_token
from werkzeug.security import check_password_hash

from app import create_app
from extensions import db
from models import User


class TestAuthenticationRoutes(unittest.TestCase):

    def setUp(self):
        self.app = create_app({
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite://",
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
            "JWT_SECRET_KEY": "sokocater-test-secret-key-for-unit-tests-2026",
            "JWT_ACCESS_TOKEN_EXPIRES": 3600
        })

        self.app_context = self.app.app_context()
        self.app_context.push()

        db.create_all()

        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def register_user(self, **overrides):
        data = {
            "full_name": "Test Customer",
            "email": "customer@example.com",
            "password": "password123",
            "phone_number": "0712345678",
            "role": "customer"
        }

        data.update(overrides)

        return self.client.post(
            "/api/auth/register",
            json=data
        )

    def create_user(self, **overrides):
        data = {
            "full_name": "Test Customer",
            "email": "customer@example.com",
            "password": "password123",
            "role": "customer"
        }

        data.update(overrides)

        user = User(
            full_name=data["full_name"],
            email=data["email"],
            password_hash=__import__(
                "werkzeug.security",
                fromlist=["generate_password_hash"]
            ).generate_password_hash(data["password"]),
            role=data["role"]
        )

        db.session.add(user)
        db.session.commit()

        return user

    # REGISTRATION TESTS

    def test_customer_registration_successful(self):
        response = self.register_user()

        self.assertEqual(response.status_code, 201)

        data = response.get_json()

        self.assertEqual(
            data["message"],
            "User registered successfully"
        )

        self.assertEqual(
            data["user"]["email"],
            "customer@example.com"
        )

        self.assertEqual(
            data["user"]["role"],
            "customer"
        )

    def test_caterer_registration_successful(self):
        response = self.register_user(
            full_name="Test Caterer",
            email="caterer@example.com",
            role="caterer"
        )

        self.assertEqual(response.status_code, 201)

        data = response.get_json()

        self.assertEqual(
            data["user"]["role"],
            "caterer"
        )

    def test_password_is_hashed(self):
        self.register_user()

        user = User.query.filter_by(
            email="customer@example.com"
        ).first()

        self.assertIsNotNone(user)

        self.assertNotEqual(
            user.password_hash,
            "password123"
        )

        self.assertTrue(
            check_password_hash(
                user.password_hash,
                "password123"
            )
        )

    def test_duplicate_email_is_rejected(self):
        self.register_user()

        response = self.register_user()

        self.assertEqual(response.status_code, 409)

        self.assertEqual(
            response.get_json()["error"],
            "Email already registered"
        )

    def test_email_is_case_insensitive(self):
        self.register_user(
            email="CUSTOMER@example.com"
        )

        response = self.register_user(
            email="customer@example.com"
        )

        self.assertEqual(response.status_code, 409)

    def test_invalid_registration_data_is_rejected(self):
        response = self.register_user(
            full_name="A"
        )

        self.assertEqual(response.status_code, 400)

    def test_invalid_registration_role_is_rejected(self):
        response = self.register_user(
            role="admin"
        )

        self.assertEqual(response.status_code, 400)

    def test_short_password_is_rejected(self):
        response = self.register_user(
            password="123"
        )

        self.assertEqual(response.status_code, 400)

    def test_registration_without_json_is_rejected(self):
        response = self.client.post(
            "/api/auth/register"
        )

        self.assertEqual(response.status_code, 400)

    def test_registration_with_invalid_json_is_rejected(self):
        response = self.client.post(
            "/api/auth/register",
            data="invalid json",
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 400)

    # LOGIN TESTS

    def test_login_successful(self):
        self.create_user()

        response = self.client.post(
            "/api/auth/login",
            json={
                "email": "customer@example.com",
                "password": "password123"
            }
        )

        self.assertEqual(response.status_code, 200)

        data = response.get_json()

        self.assertEqual(
            data["message"],
            "Login successful"
        )

        self.assertIn("access_token", data)

        self.assertEqual(
            data["user"]["email"],
            "customer@example.com"
        )

    def test_login_generates_valid_jwt(self):
        self.create_user()

        response = self.client.post(
            "/api/auth/login",
            json={
                "email": "customer@example.com",
                "password": "password123"
            }
        )

        token = response.get_json()["access_token"]

        decoded_token = decode_token(token)

        self.assertEqual(
            decoded_token["sub"],
            "1"
        )

        self.assertEqual(
            decoded_token["role"],
            "customer"
        )

    def test_login_with_incorrect_password_is_rejected(self):
        self.create_user()

        response = self.client.post(
            "/api/auth/login",
            json={
                "email": "customer@example.com",
                "password": "wrongpassword"
            }
        )

        self.assertEqual(response.status_code, 401)

        self.assertEqual(
            response.get_json()["error"],
            "Invalid email or password"
        )

    def test_login_with_unknown_email_is_rejected(self):
        response = self.client.post(
            "/api/auth/login",
            json={
                "email": "unknown@example.com",
                "password": "password123"
            }
        )

        self.assertEqual(response.status_code, 401)

    def test_login_with_missing_password_is_rejected(self):
        self.create_user()

        response = self.client.post(
            "/api/auth/login",
            json={
                "email": "customer@example.com"
            }
        )

        self.assertEqual(response.status_code, 400)

    def test_login_with_missing_email_is_rejected(self):
        response = self.client.post(
            "/api/auth/login",
            json={
                "password": "password123"
            }
        )

        self.assertEqual(response.status_code, 400)

    def test_login_without_json_is_rejected(self):
        response = self.client.post(
            "/api/auth/login"
        )

        self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main(verbosity=2)
