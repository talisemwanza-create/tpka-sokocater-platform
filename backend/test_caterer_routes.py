
import unittest

from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash

from app import create_app
from extensions import db
from models import User, Caterer


class TestCatererRoutes(unittest.TestCase):

    def setUp(self):
        self.app = create_app({
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite://",
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
            "JWT_SECRET_KEY": "sokocater-test-secret-key-for-unit-tests-2026"
        })

        self.app_context = self.app.app_context()
        self.app_context.push()

        db.create_all()

        self.client = self.app.test_client()

        self.caterer_user = self.create_user(
            email="caterer@example.com",
            role="caterer"
        )

        self.customer_user = self.create_user(
            email="customer@example.com",
            role="customer"
        )

        self.other_caterer_user = self.create_user(
            email="other@example.com",
            role="caterer"
        )

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    # ==================================================
    # HELPER METHODS
    # ==================================================

    def create_user(
        self,
        full_name="Test User",
        email="test@example.com",
        role="customer"
    ):

        user = User(
            full_name=full_name,
            email=email,
            password_hash=generate_password_hash("password123"),
            role=role
        )

        db.session.add(user)
        db.session.commit()

        return user

    def create_token(self, user):

        token = create_access_token(
            identity=str(user.id),
            additional_claims={
                "role": user.role
            }
        )

        return {
            "Authorization": f"Bearer {token}"
        }

    def create_caterer_profile(self, user=None, **overrides):

        if user is None:
            user = self.caterer_user

        data = {
            "user_id": user.id,
            "business_name": "Fresh Foods Catering",
            "description": "Professional catering services",
            "location": "Nairobi",
            "contact_number": "0712345678",
            "business_image": "https://example.com/image.jpg"
        }

        data.update(overrides)

        caterer = Caterer(
            **data,
            verification_status="pending"
        )

        db.session.add(caterer)
        db.session.commit()

        return caterer

    def valid_profile_data(self, user=None):

        if user is None:
            user = self.caterer_user

        return {
            "user_id": user.id,
            "business_name": "Fresh Foods Catering",
            "description": "Professional catering services",
            "location": "Nairobi",
            "contact_number": "0712345678",
            "business_image": "https://example.com/image.jpg"
        }

    # ==================================================
    # PUBLIC GET ROUTES
    # ==================================================

    def test_get_all_caterers_successful(self):

        self.create_caterer_profile()

        response = self.client.get("/api/caterers")

        self.assertEqual(response.status_code, 200)

        data = response.get_json()

        self.assertIn("data", data)
        self.assertEqual(len(data["data"]), 1)

    def test_get_all_caterers_without_authentication(self):

        response = self.client.get("/api/caterers")

        self.assertEqual(response.status_code, 200)

    def test_get_single_caterer_successful(self):

        caterer = self.create_caterer_profile()

        response = self.client.get(
            f"/api/caterers/{caterer.id}"
        )

        self.assertEqual(response.status_code, 200)

        data = response.get_json()

        self.assertEqual(
            data["data"]["business_name"],
            "Fresh Foods Catering"
        )

    def test_get_single_caterer_not_found(self):

        response = self.client.get("/api/caterers/999")

        self.assertEqual(response.status_code, 404)

    # ==================================================
    # CREATE CATERER ROUTE
    # ==================================================

    def test_create_caterer_successful(self):

        response = self.client.post(
            "/api/caterers",
            json=self.valid_profile_data(),
            headers=self.create_token(self.caterer_user)
        )

        self.assertEqual(response.status_code, 201)

        data = response.get_json()

        self.assertEqual(
            data["message"],
            "Caterer created successfully"
        )

        self.assertEqual(
            data["data"]["business_name"],
            "Fresh Foods Catering"
        )

        self.assertEqual(
            data["data"]["verification_status"],
            "pending"
        )

    def test_create_caterer_without_token(self):

        response = self.client.post(
            "/api/caterers",
            json=self.valid_profile_data()
        )

        self.assertEqual(response.status_code, 401)

    def test_customer_cannot_create_caterer_profile(self):

        response = self.client.post(
            "/api/caterers",
            json=self.valid_profile_data(self.customer_user),
            headers=self.create_token(self.customer_user)
        )

        self.assertEqual(response.status_code, 403)

    def test_caterer_cannot_create_profile_for_another_user(self):

        response = self.client.post(
            "/api/caterers",
            json=self.valid_profile_data(self.other_caterer_user),
            headers=self.create_token(self.caterer_user)
        )

        self.assertEqual(response.status_code, 403)

    def test_duplicate_caterer_profile_rejected(self):

        self.create_caterer_profile()

        response = self.client.post(
            "/api/caterers",
            json=self.valid_profile_data(),
            headers=self.create_token(self.caterer_user)
        )

        self.assertEqual(response.status_code, 409)

    def test_create_caterer_with_invalid_data(self):

        data = self.valid_profile_data()
        data["business_name"] = "A"

        response = self.client.post(
            "/api/caterers",
            json=data,
            headers=self.create_token(self.caterer_user)
        )

        self.assertEqual(response.status_code, 400)

    def test_create_caterer_without_json(self):

        response = self.client.post(
            "/api/caterers",
            headers=self.create_token(self.caterer_user)
        )

        self.assertEqual(response.status_code, 400)

    def test_verification_status_cannot_be_supplied(self):

        data = self.valid_profile_data()
        data["verification_status"] = "verified"

        response = self.client.post(
            "/api/caterers",
            json=data,
            headers=self.create_token(self.caterer_user)
        )

        self.assertEqual(response.status_code, 400)

        caterer = Caterer.query.filter_by(
            user_id=self.caterer_user.id
        ).first()

        self.assertIsNone(caterer)

    # ==================================================
    # UPDATE CATERER ROUTE
    # ==================================================

    def test_update_own_caterer_profile_successful(self):

        caterer = self.create_caterer_profile()

        response = self.client.put(
            f"/api/caterers/{caterer.id}",
            json={
                "business_name": "Updated Catering Business"
            },
            headers=self.create_token(self.caterer_user)
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            response.get_json()["data"]["business_name"],
            "Updated Catering Business"
        )

    def test_update_caterer_without_token(self):

        caterer = self.create_caterer_profile()

        response = self.client.put(
            f"/api/caterers/{caterer.id}",
            json={
                "business_name": "Updated Business"
            }
        )

        self.assertEqual(response.status_code, 401)

    def test_customer_cannot_update_caterer_profile(self):

        caterer = self.create_caterer_profile()

        response = self.client.put(
            f"/api/caterers/{caterer.id}",
            json={
                "business_name": "Updated Business"
            },
            headers=self.create_token(self.customer_user)
        )

        self.assertEqual(response.status_code, 403)

    def test_caterer_cannot_update_another_profile(self):

        caterer = self.create_caterer_profile()

        response = self.client.put(
            f"/api/caterers/{caterer.id}",
            json={
                "business_name": "Unauthorized Update"
            },
            headers=self.create_token(self.other_caterer_user)
        )

        self.assertEqual(response.status_code, 403)

    def test_update_nonexistent_caterer(self):

        response = self.client.put(
            "/api/caterers/999",
            json={
                "business_name": "Updated Business"
            },
            headers=self.create_token(self.caterer_user)
        )

        self.assertEqual(response.status_code, 404)

    def test_caterer_cannot_change_profile_ownership(self):

        caterer = self.create_caterer_profile()

        response = self.client.put(
            f"/api/caterers/{caterer.id}",
            json={
                "user_id": self.other_caterer_user.id
            },
            headers=self.create_token(self.caterer_user)
        )

        self.assertEqual(response.status_code, 403)

    # ==================================================
    # DELETE CATERER ROUTE
    # ==================================================

    def test_delete_own_caterer_profile_successful(self):

        caterer = self.create_caterer_profile()

        caterer_id = caterer.id

        response = self.client.delete(
            f"/api/caterers/{caterer_id}",
            headers=self.create_token(self.caterer_user)
        )

        self.assertEqual(response.status_code, 200)

        self.assertIsNone(
            db.session.get(Caterer, caterer_id)
        )

    def test_delete_caterer_without_token(self):

        caterer = self.create_caterer_profile()

        response = self.client.delete(
            f"/api/caterers/{caterer.id}"
        )

        self.assertEqual(response.status_code, 401)

    def test_customer_cannot_delete_caterer_profile(self):

        caterer = self.create_caterer_profile()

        response = self.client.delete(
            f"/api/caterers/{caterer.id}",
            headers=self.create_token(self.customer_user)
        )

        self.assertEqual(response.status_code, 403)

    def test_caterer_cannot_delete_another_profile(self):

        caterer = self.create_caterer_profile()

        response = self.client.delete(
            f"/api/caterers/{caterer.id}",
            headers=self.create_token(self.other_caterer_user)
        )

        self.assertEqual(response.status_code, 403)

    def test_delete_nonexistent_caterer(self):

        response = self.client.delete(
            "/api/caterers/999",
            headers=self.create_token(self.caterer_user)
        )

        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main(verbosity=2)
