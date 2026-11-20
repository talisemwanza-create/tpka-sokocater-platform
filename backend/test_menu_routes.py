
import unittest

from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash

from app import create_app
from extensions import db
from models import User, Caterer, Menu


class TestMenuRoutes(unittest.TestCase):

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

        # Create test users.
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

        self.caterer_without_profile = self.create_user(
            email="no-profile@example.com",
            role="caterer"
        )

        # Create caterer profiles.
        self.caterer = self.create_caterer_profile(
            self.caterer_user
        )

        self.other_caterer = self.create_caterer_profile(
            self.other_caterer_user,
            business_name="Other Catering Business"
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

    def create_caterer_profile(
        self,
        user,
        **overrides
    ):

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

    def create_menu(self, caterer=None, **overrides):

        if caterer is None:
            caterer = self.caterer

        data = {
            "caterer_id": caterer.id,
            "menu_name": "Wedding Menu",
            "description": "A special wedding catering menu"
        }

        data.update(overrides)

        menu = Menu(**data)

        db.session.add(menu)
        db.session.commit()

        return menu

    def valid_menu_data(self, caterer=None):

        if caterer is None:
            caterer = self.caterer

        return {
            "caterer_id": caterer.id,
            "menu_name": "Wedding Menu",
            "description": "A special wedding catering menu"
        }

    # ==================================================
    # PUBLIC GET ROUTES
    # ==================================================

    def test_get_all_menus_successful(self):

        self.create_menu()

        response = self.client.get("/api/menus")

        self.assertEqual(response.status_code, 200)

        data = response.get_json()

        self.assertIn("data", data)
        self.assertEqual(len(data["data"]), 1)

    def test_get_all_menus_without_authentication(self):

        response = self.client.get("/api/menus")

        self.assertEqual(response.status_code, 200)

    def test_get_single_menu_successful(self):

        menu = self.create_menu()

        response = self.client.get(
            f"/api/menus/{menu.id}"
        )

        self.assertEqual(response.status_code, 200)

        data = response.get_json()

        self.assertEqual(
            data["data"]["menu_name"],
            "Wedding Menu"
        )

    def test_get_single_menu_not_found(self):

        response = self.client.get("/api/menus/999")

        self.assertEqual(response.status_code, 404)

    # ==================================================
    # CREATE MENU ROUTE
    # ==================================================

    def test_create_menu_successful(self):

        response = self.client.post(
            "/api/menus",
            json=self.valid_menu_data(),
            headers=self.create_token(self.caterer_user)
        )

        self.assertEqual(response.status_code, 201)

        data = response.get_json()

        self.assertEqual(
            data["message"],
            "Menu created successfully"
        )

        self.assertEqual(
            data["data"]["menu_name"],
            "Wedding Menu"
        )

        self.assertEqual(
            data["data"]["caterer_id"],
            self.caterer.id
        )

    def test_create_menu_without_token(self):

        response = self.client.post(
            "/api/menus",
            json=self.valid_menu_data()
        )

        self.assertEqual(response.status_code, 401)

    def test_customer_cannot_create_menu(self):

        response = self.client.post(
            "/api/menus",
            json=self.valid_menu_data(),
            headers=self.create_token(self.customer_user)
        )

        self.assertEqual(response.status_code, 403)

    def test_caterer_without_profile_cannot_create_menu(self):

        response = self.client.post(
            "/api/menus",
            json=self.valid_menu_data(),
            headers=self.create_token(
                self.caterer_without_profile
            )
        )

        self.assertEqual(response.status_code, 403)

    def test_caterer_cannot_create_menu_for_another_caterer(self):

        response = self.client.post(
            "/api/menus",
            json=self.valid_menu_data(self.other_caterer),
            headers=self.create_token(self.caterer_user)
        )

        self.assertEqual(response.status_code, 403)

    def test_create_menu_with_invalid_data(self):

        data = self.valid_menu_data()
        data["menu_name"] = "A"

        response = self.client.post(
            "/api/menus",
            json=data,
            headers=self.create_token(self.caterer_user)
        )

        self.assertEqual(response.status_code, 400)

    def test_create_menu_without_json(self):

        response = self.client.post(
            "/api/menus",
            headers=self.create_token(self.caterer_user)
        )

        self.assertEqual(response.status_code, 400)

    # ==================================================
    # UPDATE MENU ROUTE
    # ==================================================

    def test_update_own_menu_successful(self):

        menu = self.create_menu()

        response = self.client.put(
            f"/api/menus/{menu.id}",
            json={
                "menu_name": "Updated Wedding Menu"
            },
            headers=self.create_token(self.caterer_user)
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            response.get_json()["data"]["menu_name"],
            "Updated Wedding Menu"
        )

    def test_update_menu_without_token(self):

        menu = self.create_menu()

        response = self.client.put(
            f"/api/menus/{menu.id}",
            json={
                "menu_name": "Updated Menu"
            }
        )

        self.assertEqual(response.status_code, 401)

    def test_customer_cannot_update_menu(self):

        menu = self.create_menu()

        response = self.client.put(
            f"/api/menus/{menu.id}",
            json={
                "menu_name": "Unauthorized Update"
            },
            headers=self.create_token(self.customer_user)
        )

        self.assertEqual(response.status_code, 403)

    def test_caterer_cannot_update_another_caterers_menu(self):

        menu = self.create_menu(self.other_caterer)

        response = self.client.put(
            f"/api/menus/{menu.id}",
            json={
                "menu_name": "Unauthorized Update"
            },
            headers=self.create_token(self.caterer_user)
        )

        self.assertEqual(response.status_code, 403)

    def test_update_nonexistent_menu(self):

        response = self.client.put(
            "/api/menus/999",
            json={
                "menu_name": "Updated Menu"
            },
            headers=self.create_token(self.caterer_user)
        )

        self.assertEqual(response.status_code, 404)

    def test_caterer_cannot_transfer_menu_to_another_caterer(self):

        menu = self.create_menu()

        response = self.client.put(
            f"/api/menus/{menu.id}",
            json={
                "caterer_id": self.other_caterer.id
            },
            headers=self.create_token(self.caterer_user)
        )

        self.assertEqual(response.status_code, 403)

    def test_update_menu_with_invalid_data(self):

        menu = self.create_menu()

        response = self.client.put(
            f"/api/menus/{menu.id}",
            json={
                "menu_name": "A"
            },
            headers=self.create_token(self.caterer_user)
        )

        self.assertEqual(response.status_code, 400)

    # ==================================================
    # DELETE MENU ROUTE
    # ==================================================

    def test_delete_own_menu_successful(self):

        menu = self.create_menu()

        menu_id = menu.id

        response = self.client.delete(
            f"/api/menus/{menu_id}",
            headers=self.create_token(self.caterer_user)
        )

        self.assertEqual(response.status_code, 200)

        self.assertIsNone(
            db.session.get(Menu, menu_id)
        )

    def test_delete_menu_without_token(self):

        menu = self.create_menu()

        response = self.client.delete(
            f"/api/menus/{menu.id}"
        )

        self.assertEqual(response.status_code, 401)

    def test_customer_cannot_delete_menu(self):

        menu = self.create_menu()

        response = self.client.delete(
            f"/api/menus/{menu.id}",
            headers=self.create_token(self.customer_user)
        )

        self.assertEqual(response.status_code, 403)

    def test_caterer_cannot_delete_another_caterers_menu(self):

        menu = self.create_menu(self.other_caterer)

        response = self.client.delete(
            f"/api/menus/{menu.id}",
            headers=self.create_token(self.caterer_user)
        )

        self.assertEqual(response.status_code, 403)

    def test_delete_nonexistent_menu(self):

        response = self.client.delete(
            "/api/menus/999",
            headers=self.create_token(self.caterer_user)
        )

        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main(verbosity=2)
