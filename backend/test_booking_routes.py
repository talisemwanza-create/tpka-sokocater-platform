
import unittest
from datetime import date
from decimal import Decimal

from app import create_app
from extensions import db
from models import User, Caterer, Package, Booking, BookingItem
from flask_jwt_extended import create_access_token


class TestBookingRoutes(unittest.TestCase):

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

        # Create users.
        self.customer = User(
            full_name="Test Customer",
            email="customer@test.com",
            password_hash="hashedpassword",
            role="customer"
        )

        self.other_customer = User(
            full_name="Other Customer",
            email="othercustomer@test.com",
            password_hash="hashedpassword",
            role="customer"
        )

        self.caterer_user = User(
            full_name="Test Caterer",
            email="caterer@test.com",
            password_hash="hashedpassword",
            role="caterer"
        )

        self.other_caterer_user = User(
            full_name="Other Caterer",
            email="othercaterer@test.com",
            password_hash="hashedpassword",
            role="caterer"
        )

        self.admin = User(
            full_name="Test Admin",
            email="admin@test.com",
            password_hash="hashedpassword",
            role="admin"
        )

        db.session.add_all([
            self.customer,
            self.other_customer,
            self.caterer_user,
            self.other_caterer_user,
            self.admin
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

        # Create packages.
        self.package = Package(
            caterer_id=self.caterer.id,
            package_name="Wedding Package",
            description="Wedding catering package",
            price_per_guest=Decimal("1500.00"),
            minimum_guests=20,
            maximum_guests=200
        )

        self.other_package = Package(
            caterer_id=self.other_caterer.id,
            package_name="Birthday Package",
            description="Birthday catering package",
            price_per_guest=Decimal("1200.00"),
            minimum_guests=10,
            maximum_guests=100
        )

        db.session.add_all([
            self.package,
            self.other_package
        ])

        db.session.commit()

        # Create an existing booking.
        # SQLAlchemy Date columns require Python date objects.
        self.booking = Booking(
            customer_id=self.customer.id,
            caterer_id=self.caterer.id,
            event_date=date(2027, 6, 15),
            event_type="Wedding",
            event_location="Nairobi",
            guest_count=50,
            estimated_total=Decimal("75000.00")
        )

        db.session.add(self.booking)
        db.session.commit()

        # Create the booking item.
        self.booking_item = BookingItem(
            booking_id=self.booking.id,
            package_id=self.package.id,
            addon_id=None,
            quantity=50,
            unit_price=Decimal("1500.00")
        )

        db.session.add(self.booking_item)
        db.session.commit()

        # Create authentication tokens.
        self.customer_token = create_access_token(
            identity=str(self.customer.id),
            additional_claims={"role": "customer"}
        )

        self.other_customer_token = create_access_token(
            identity=str(self.other_customer.id),
            additional_claims={"role": "customer"}
        )

        self.caterer_token = create_access_token(
            identity=str(self.caterer_user.id),
            additional_claims={"role": "caterer"}
        )

        self.other_caterer_token = create_access_token(
            identity=str(self.other_caterer_user.id),
            additional_claims={"role": "caterer"}
        )

        self.admin_token = create_access_token(
            identity=str(self.admin.id),
            additional_claims={"role": "admin"}
        )

        # Authorization headers.
        self.customer_headers = {
            "Authorization": f"Bearer {self.customer_token}"
        }

        self.other_customer_headers = {
            "Authorization": f"Bearer {self.other_customer_token}"
        }

        self.caterer_headers = {
            "Authorization": f"Bearer {self.caterer_token}"
        }

        self.other_caterer_headers = {
            "Authorization": f"Bearer {self.other_caterer_token}"
        }

        self.admin_headers = {
            "Authorization": f"Bearer {self.admin_token}"
        }

        # Valid booking request data.
        # Keep event_date as a string because this is JSON input.
        self.valid_booking_data = {
            "caterer_id": self.caterer.id,
            "package_id": self.package.id,
            "event_date": "2027-08-20",
            "event_type": "Birthday",
            "event_location": "Nairobi",
            "guest_count": 40
        }

    def tearDown(self):

        db.session.remove()
        db.drop_all()

        self.app_context.pop()

    # ==================================================
    # GET ALL BOOKINGS
    # ==================================================

    def test_customer_can_view_own_bookings(self):

        response = self.client.get(
            "/api/bookings",
            headers=self.customer_headers
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json["data"]), 1)

    def test_caterer_can_view_own_bookings(self):

        response = self.client.get(
            "/api/bookings",
            headers=self.caterer_headers
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json["data"]), 1)

    def test_customer_without_token_cannot_view_bookings(self):

        response = self.client.get("/api/bookings")

        self.assertEqual(response.status_code, 401)

    def test_admin_cannot_view_all_bookings(self):

        response = self.client.get(
            "/api/bookings",
            headers=self.admin_headers
        )

        self.assertEqual(response.status_code, 403)

    def test_caterer_without_profile_cannot_view_bookings(self):

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

        response = self.client.get(
            "/api/bookings",
            headers={"Authorization": f"Bearer {token}"}
        )

        self.assertEqual(response.status_code, 404)

    # ==================================================
    # GET ONE BOOKING
    # ==================================================

    def test_customer_can_view_own_booking(self):

        response = self.client.get(
            f"/api/bookings/{self.booking.id}",
            headers=self.customer_headers
        )

        self.assertEqual(response.status_code, 200)

    def test_customer_cannot_view_another_customers_booking(self):

        response = self.client.get(
            f"/api/bookings/{self.booking.id}",
            headers=self.other_customer_headers
        )

        self.assertEqual(response.status_code, 403)

    def test_caterer_can_view_own_booking(self):

        response = self.client.get(
            f"/api/bookings/{self.booking.id}",
            headers=self.caterer_headers
        )

        self.assertEqual(response.status_code, 200)

    def test_caterer_cannot_view_another_caterers_booking(self):

        response = self.client.get(
            f"/api/bookings/{self.booking.id}",
            headers=self.other_caterer_headers
        )

        self.assertEqual(response.status_code, 403)

    def test_get_booking_without_token(self):

        response = self.client.get(
            f"/api/bookings/{self.booking.id}"
        )

        self.assertEqual(response.status_code, 401)

    def test_get_nonexistent_booking(self):

        response = self.client.get(
            "/api/bookings/999",
            headers=self.customer_headers
        )

        self.assertEqual(response.status_code, 404)

    def test_admin_cannot_view_single_booking(self):

        response = self.client.get(
            f"/api/bookings/{self.booking.id}",
            headers=self.admin_headers
        )

        self.assertEqual(response.status_code, 403)

    # ==================================================
    # CREATE BOOKING
    # ==================================================

    def test_customer_can_create_booking(self):

        response = self.client.post(
            "/api/bookings",
            json=self.valid_booking_data,
            headers=self.customer_headers
        )

        self.assertEqual(response.status_code, 201)

        self.assertEqual(
            response.json["data"]["guest_count"],
            40
        )

        self.assertEqual(
            response.json["data"]["estimated_total"],
            "60000.00"
        )

    def test_create_booking_without_token(self):

        response = self.client.post(
            "/api/bookings",
            json=self.valid_booking_data
        )

        self.assertEqual(response.status_code, 401)

    def test_caterer_cannot_create_booking(self):

        response = self.client.post(
            "/api/bookings",
            json=self.valid_booking_data,
            headers=self.caterer_headers
        )

        self.assertEqual(response.status_code, 403)

    def test_admin_cannot_create_booking(self):

        response = self.client.post(
            "/api/bookings",
            json=self.valid_booking_data,
            headers=self.admin_headers
        )

        self.assertEqual(response.status_code, 403)

    def test_create_booking_without_json(self):

        response = self.client.post(
            "/api/bookings",
            headers=self.customer_headers
        )

        self.assertEqual(response.status_code, 400)

    def test_create_booking_with_invalid_data(self):

        data = self.valid_booking_data.copy()
        data["guest_count"] = 0

        response = self.client.post(
            "/api/bookings",
            json=data,
            headers=self.customer_headers
        )

        self.assertEqual(response.status_code, 400)

    def test_create_booking_with_nonexistent_caterer(self):

        data = self.valid_booking_data.copy()
        data["caterer_id"] = 999

        response = self.client.post(
            "/api/bookings",
            json=data,
            headers=self.customer_headers
        )

        self.assertEqual(response.status_code, 404)

    def test_create_booking_with_nonexistent_package(self):

        data = self.valid_booking_data.copy()
        data["package_id"] = 999

        response = self.client.post(
            "/api/bookings",
            json=data,
            headers=self.customer_headers
        )

        self.assertEqual(response.status_code, 400)

    def test_create_booking_with_package_from_another_caterer(self):

        data = self.valid_booking_data.copy()
        data["package_id"] = self.other_package.id

        response = self.client.post(
            "/api/bookings",
            json=data,
            headers=self.customer_headers
        )

        self.assertEqual(response.status_code, 400)

    def test_create_booking_below_minimum_guests(self):

        data = self.valid_booking_data.copy()
        data["guest_count"] = 10

        response = self.client.post(
            "/api/bookings",
            json=data,
            headers=self.customer_headers
        )

        self.assertEqual(response.status_code, 400)

    def test_create_booking_above_maximum_guests(self):

        data = self.valid_booking_data.copy()
        data["guest_count"] = 250

        response = self.client.post(
            "/api/bookings",
            json=data,
            headers=self.customer_headers
        )

        self.assertEqual(response.status_code, 400)

    # ==================================================
    # UPDATE BOOKING
    # ==================================================

    def test_customer_can_update_own_booking(self):

        response = self.client.put(
            f"/api/bookings/{self.booking.id}",
            json={"event_location": "Mombasa"},
            headers=self.customer_headers
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json["data"]["event_location"],
            "Mombasa"
        )

    def test_customer_cannot_update_another_customers_booking(self):

        response = self.client.put(
            f"/api/bookings/{self.booking.id}",
            json={"event_location": "Mombasa"},
            headers=self.other_customer_headers
        )

        self.assertEqual(response.status_code, 403)

    def test_caterer_can_update_booking_status(self):

        response = self.client.put(
            f"/api/bookings/{self.booking.id}",
            json={"status": "accepted"},
            headers=self.caterer_headers
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json["data"]["status"],
            "accepted"
        )

    def test_caterer_cannot_update_another_caterers_booking(self):

        response = self.client.put(
            f"/api/bookings/{self.booking.id}",
            json={"status": "accepted"},
            headers=self.other_caterer_headers
        )

        self.assertEqual(response.status_code, 403)

    def test_caterer_cannot_update_booking_details(self):

        response = self.client.put(
            f"/api/bookings/{self.booking.id}",
            json={"event_location": "Mombasa"},
            headers=self.caterer_headers
        )

        self.assertEqual(response.status_code, 400)

    def test_caterer_cannot_set_invalid_booking_status(self):

        response = self.client.put(
            f"/api/bookings/{self.booking.id}",
            json={"status": "invalid"},
            headers=self.caterer_headers
        )

        self.assertEqual(response.status_code, 400)

    def test_customer_cannot_update_booking_status(self):

        response = self.client.put(
            f"/api/bookings/{self.booking.id}",
            json={"status": "accepted"},
            headers=self.customer_headers
        )

        self.assertEqual(response.status_code, 403)

    def test_update_booking_without_token(self):

        response = self.client.put(
            f"/api/bookings/{self.booking.id}",
            json={"event_location": "Mombasa"}
        )

        self.assertEqual(response.status_code, 401)

    def test_update_nonexistent_booking(self):

        response = self.client.put(
            "/api/bookings/999",
            json={"event_location": "Mombasa"},
            headers=self.customer_headers
        )

        self.assertEqual(response.status_code, 404)

    def test_update_booking_without_json(self):

        response = self.client.put(
            f"/api/bookings/{self.booking.id}",
            headers=self.customer_headers
        )

        self.assertEqual(response.status_code, 400)

    def test_customer_can_update_guest_count_and_total(self):

        response = self.client.put(
            f"/api/bookings/{self.booking.id}",
            json={"guest_count": 60},
            headers=self.customer_headers
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json["data"]["guest_count"],
            60
        )
        self.assertEqual(
            response.json["data"]["estimated_total"],
            "90000.00"
        )

    def test_customer_cannot_update_server_controlled_fields(self):

        response = self.client.put(
            f"/api/bookings/{self.booking.id}",
            json={"customer_id": self.other_customer.id},
            headers=self.customer_headers
        )

        self.assertEqual(response.status_code, 403)

    # ==================================================
    # DELETE BOOKING
    # ==================================================

    def test_customer_can_delete_own_booking(self):

        response = self.client.delete(
            f"/api/bookings/{self.booking.id}",
            headers=self.customer_headers
        )

        self.assertEqual(response.status_code, 200)

        deleted_booking = db.session.get(
            Booking,
            self.booking.id
        )

        self.assertIsNone(deleted_booking)

    def test_customer_cannot_delete_another_customers_booking(self):

        response = self.client.delete(
            f"/api/bookings/{self.booking.id}",
            headers=self.other_customer_headers
        )

        self.assertEqual(response.status_code, 403)

    def test_caterer_cannot_delete_booking(self):

        response = self.client.delete(
            f"/api/bookings/{self.booking.id}",
            headers=self.caterer_headers
        )

        self.assertEqual(response.status_code, 403)

    def test_admin_cannot_delete_booking(self):

        response = self.client.delete(
            f"/api/bookings/{self.booking.id}",
            headers=self.admin_headers
        )

        self.assertEqual(response.status_code, 403)

    def test_delete_booking_without_token(self):

        response = self.client.delete(
            f"/api/bookings/{self.booking.id}"
        )

        self.assertEqual(response.status_code, 401)

    def test_delete_nonexistent_booking(self):

        response = self.client.delete(
            "/api/bookings/999",
            headers=self.customer_headers
        )

        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main(verbosity=2)
