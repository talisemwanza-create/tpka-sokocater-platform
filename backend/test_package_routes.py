
import unittest
from decimal import Decimal

from app import create_app
from extensions import db
from models import User, Caterer, Package
from flask_jwt_extended import create_access_token


class TestPackageRoutes(unittest.TestCase):

    def setUp(self):

        self.app = create_app({
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite://",
            "JWT_SECRET_KEY": "sokocater-test-secret-key-for-unit-tests-2026"
        })

        self.client = self.app.test_client()

        self.app_context = self.app.app_context()
        self.app_context.push()

        db.create_all()

        # Create customer user.
        self.customer = User(
            full_name="Test Customer",
            email="customer@test.com",
            password_hash="hashedpassword",
            role="customer"
        )

        # Create first caterer user.
        self.caterer_user = User(
            full_name="Test Caterer",
            email="caterer@test.com",
            password_hash="hashedpassword",
            role="caterer"
        )

        # Create second caterer user.
        self.other_caterer_user = User(
            full_name="Other Caterer",
            email="other@test.com",
            password_hash="hashedpassword",
            role="caterer"
        )

        db.session.add_all([
            self.customer,
            self.caterer_user,
            self.other_caterer_user
        ])

        db.session.commit()

        # Create caterer profiles.
        self.caterer = Caterer(
            user_id=self.caterer_user.id,
            business_name="Test Catering",
            location="Nairobi",
            verification_status="pending"
        )

        self.other_caterer = Caterer(
            user_id=self.other_caterer_user.id,
            business_name="Other Catering",
            location="Nairobi",
            verification_status="pending"
        )

        db.session.add_all([
            self.caterer,
            self.other_caterer
        ])

        db.session.commit()

        # Create a package owned by the first caterer.
        self.package = Package(
            caterer_id=self.caterer.id,
            package_name="Wedding Package",
            description="A wedding catering package",
            price_per_guest=Decimal("1500.00"),
            minimum_guests=20,
            maximum_guests=200
        )

        db.session.add(self.package)
        db.session.commit()

        # Generate authentication tokens.
        self.caterer_token = create_access_token(
            identity=str(self.caterer_user.id),
            additional_claims={"role": "caterer"}
        )

        self.other_caterer_token = create_access_token(
            identity=str(self.other_caterer_user.id),
            additional_claims={"role": "caterer"}
        )

        self.customer_token = create_access_token(
            identity=str(self.customer.id),
            additional_claims={"role": "customer"}
        )

        self.caterer_headers = {
            "Authorization": f"Bearer {self.caterer_token}"
        }

        self.other_caterer_headers = {
            "Authorization": f"Bearer {self.other_caterer_token}"
        }

        self.customer_headers = {
            "Authorization": f"Bearer {self.customer_token}"
        }

        self.valid_package_data = {
            "caterer_id": self.caterer.id,
            "package_name": "Birthday Package",
            "description": "Birthday catering package",
            "price_per_guest": "1200.00",
            "minimum_guests": 10,
            "maximum_guests": 100
        }

    def tearDown(self):

        db.session.remove()
        db.drop_all()

        self.app_context.pop()

    # ==========================================
    # GET ALL PACKAGES
    # ==========================================

    def test_get_all_packages(self):

        response = self.client.get("/api/packages")

        self.assertEqual(response.status_code, 200)
        self.assertIn("data", response.json)
        self.assertEqual(len(response.json["data"]), 1)

    # ==========================================
    # GET SINGLE PACKAGE
    # ==========================================

    def test_get_single_package(self):

        response = self.client.get(
            f"/api/packages/{self.package.id}"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json["data"]["package_name"],
            "Wedding Package"
        )

    def test_get_nonexistent_package(self):

        response = self.client.get("/api/packages/999")

        self.assertEqual(response.status_code, 404)

    # ==========================================
    # CREATE PACKAGE
    # ==========================================

    def test_caterer_can_create_package(self):

        response = self.client.post(
            "/api/packages",
            json=self.valid_package_data,
            headers=self.caterer_headers
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.json["data"]["package_name"],
            "Birthday Package"
        )

    def test_create_package_without_token(self):

        response = self.client.post(
            "/api/packages",
            json=self.valid_package_data
        )

        self.assertEqual(response.status_code, 401)

    def test_customer_cannot_create_package(self):

        response = self.client.post(
            "/api/packages",
            json=self.valid_package_data,
            headers=self.customer_headers
        )

        self.assertEqual(response.status_code, 403)

    def test_caterer_without_profile_cannot_create_package(self):

        user = User(
            full_name="No Profile Caterer",
            email="noprofile@test.com",
            password_hash="hashedpassword",
            role="caterer"
        )

        db.session.add(user)
        db.session.commit()

        token = create_access_token(
            identity=str(user.id),
            additional_claims={"role": "caterer"}
        )

        response = self.client.post(
            "/api/packages",
            json=self.valid_package_data,
            headers={"Authorization": f"Bearer {token}"}
        )

        self.assertEqual(response.status_code, 403)

    def test_caterer_cannot_create_package_for_another_caterer(self):

        data = self.valid_package_data.copy()
        data["caterer_id"] = self.other_caterer.id

        response = self.client.post(
            "/api/packages",
            json=data,
            headers=self.caterer_headers
        )

        self.assertEqual(response.status_code, 403)

    def test_create_package_with_invalid_data(self):

        data = self.valid_package_data.copy()
        data["package_name"] = "A"

        response = self.client.post(
            "/api/packages",
            json=data,
            headers=self.caterer_headers
        )

        self.assertEqual(response.status_code, 400)

    def test_create_package_without_json(self):

        response = self.client.post(
            "/api/packages",
            headers=self.caterer_headers
        )

        self.assertEqual(response.status_code, 400)

    # ==========================================
    # UPDATE PACKAGE
    # ==========================================

    def test_caterer_can_update_own_package(self):

        response = self.client.put(
            f"/api/packages/{self.package.id}",
            json={"package_name": "Updated Wedding Package"},
            headers=self.caterer_headers
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json["data"]["package_name"],
            "Updated Wedding Package"
        )

    def test_update_package_without_token(self):

        response = self.client.put(
            f"/api/packages/{self.package.id}",
            json={"package_name": "Updated Package"}
        )

        self.assertEqual(response.status_code, 401)

    def test_customer_cannot_update_package(self):

        response = self.client.put(
            f"/api/packages/{self.package.id}",
            json={"package_name": "Updated Package"},
            headers=self.customer_headers
        )

        self.assertEqual(response.status_code, 403)

    def test_caterer_cannot_update_another_caterers_package(self):

        response = self.client.put(
            f"/api/packages/{self.package.id}",
            json={"package_name": "Changed Package"},
            headers=self.other_caterer_headers
        )

        self.assertEqual(response.status_code, 403)

    def test_update_nonexistent_package(self):

        response = self.client.put(
            "/api/packages/999",
            json={"package_name": "Updated Package"},
            headers=self.caterer_headers
        )

        self.assertEqual(response.status_code, 404)

    def test_caterer_cannot_transfer_package_to_another_caterer(self):

        response = self.client.put(
            f"/api/packages/{self.package.id}",
            json={"caterer_id": self.other_caterer.id},
            headers=self.caterer_headers
        )

        self.assertEqual(response.status_code, 403)

    def test_update_package_with_invalid_data(self):

        response = self.client.put(
            f"/api/packages/{self.package.id}",
            json={"package_name": "A"},
            headers=self.caterer_headers
        )

        self.assertEqual(response.status_code, 400)

    def test_update_package_without_json(self):

        response = self.client.put(
            f"/api/packages/{self.package.id}",
            headers=self.caterer_headers
        )

        self.assertEqual(response.status_code, 400)

    # ==========================================
    # DELETE PACKAGE
    # ==========================================

    def test_caterer_can_delete_own_package(self):

        response = self.client.delete(
            f"/api/packages/{self.package.id}",
            headers=self.caterer_headers
        )

        self.assertEqual(response.status_code, 200)

        deleted_package = db.session.get(
            Package,
            self.package.id
        )

        self.assertIsNone(deleted_package)

    def test_delete_package_without_token(self):

        response = self.client.delete(
            f"/api/packages/{self.package.id}"
        )

        self.assertEqual(response.status_code, 401)

    def test_customer_cannot_delete_package(self):

        response = self.client.delete(
            f"/api/packages/{self.package.id}",
            headers=self.customer_headers
        )

        self.assertEqual(response.status_code, 403)

    def test_caterer_cannot_delete_another_caterers_package(self):

        response = self.client.delete(
            f"/api/packages/{self.package.id}",
            headers=self.other_caterer_headers
        )

        self.assertEqual(response.status_code, 403)

    def test_delete_nonexistent_package(self):

        response = self.client.delete(
            "/api/packages/999",
            headers=self.caterer_headers
        )

        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main(verbosity=2)
