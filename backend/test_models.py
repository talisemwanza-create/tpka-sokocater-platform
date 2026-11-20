
import unittest

from datetime import date
from decimal import Decimal

from sqlalchemy import event, inspect
from sqlalchemy.exc import IntegrityError

from app import create_app
from extensions import db

from models import (
    User,
    CatererProfile,
    Menu,
    MenuItem,
    Package,
    PackageItem,
    AddOn,
    Booking,
    BookingItem,
    Availability,
    Payment,
    Review,
    Notification
)


class TestSokoCaterModels(unittest.TestCase):

    def setUp(self):

        self.app = create_app({
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite://",
            "SQLALCHEMY_TRACK_MODIFICATIONS": False
        })

        self.app_context = self.app.app_context()
        self.app_context.push()

        # Enable foreign key constraints in the test SQLite database.
        event.listen(
            db.engine,
            "connect",
            self.enable_foreign_keys
        )

        db.create_all()

    @staticmethod
    def enable_foreign_keys(connection, connection_record):
        cursor = connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    def tearDown(self):

        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    # --------------------------------------------------
    # HELPER 1: CREATE A SAMPLE CATERER
    # --------------------------------------------------

    def create_sample_caterer(self):

        user = User(
            full_name="Kate Caterer",
            email="kate@example.com",
            password_hash="hashed_password",
            phone_number="0712345678",
            role="caterer"
        )

        db.session.add(user)
        db.session.flush()

        caterer = CatererProfile(
            user_id=user.id,
            business_name="Kate's Catering",
            location="Nairobi",
            description="Professional catering services",
            contact_number="0712345678",
            verification_status="pending"
        )

        db.session.add(caterer)
        db.session.flush()

        return user, caterer

    # --------------------------------------------------
    # HELPER 2: CREATE A SAMPLE CUSTOMER
    # --------------------------------------------------

    def create_sample_customer(self, email="customer@example.com"):

        customer = User(
            full_name="Test Customer",
            email=email,
            password_hash="hashed_password",
            phone_number="0798765432",
            role="customer"
        )

        db.session.add(customer)
        db.session.flush()

        return customer

    # --------------------------------------------------
    # HELPER 3: CREATE A SAMPLE PACKAGE
    # --------------------------------------------------

    def create_sample_package(self, caterer):

        package = Package(
            caterer_id=caterer.id,
            package_name="Wedding Package",
            description="Complete wedding catering package",
            price_per_guest=Decimal("1500.00"),
            minimum_guests=20,
            maximum_guests=200
        )

        db.session.add(package)
        db.session.flush()

        return package

    # --------------------------------------------------
    # HELPER 4: CREATE A SAMPLE BOOKING
    # --------------------------------------------------

    def create_sample_booking(self, customer, caterer):

        booking = Booking(
            customer_id=customer.id,
            caterer_id=caterer.id,
            event_date=date(2027, 5, 20),
            event_type="Wedding",
            event_location="Nairobi",
            guest_count=100,
            estimated_total=Decimal("150000.00"),
            status="pending"
        )

        db.session.add(booking)
        db.session.flush()

        return booking

    # --------------------------------------------------
    # TEST 1: ALL 13 MODELS CAN BE IMPORTED
    # --------------------------------------------------

    def test_all_models_imported(self):

        model_classes = [
            User,
            CatererProfile,
            Menu,
            MenuItem,
            Package,
            PackageItem,
            AddOn,
            Booking,
            BookingItem,
            Availability,
            Payment,
            Review,
            Notification
        ]

        self.assertEqual(len(model_classes), 13)

    # --------------------------------------------------
    # TEST 2: ALL 13 DATABASE TABLES ARE CREATED
    # --------------------------------------------------

    def test_all_tables_created(self):

        inspector = inspect(db.engine)

        expected_tables = {
            "users",
            "caterer_profiles",
            "menus",
            "menu_items",
            "packages",
            "package_items",
            "add_ons",
            "bookings",
            "booking_items",
            "availability",
            "payments",
            "reviews",
            "notifications"
        }

        actual_tables = set(inspector.get_table_names())

        self.assertEqual(actual_tables, expected_tables)

    # --------------------------------------------------
    # TEST 3: ALL MODEL RELATIONSHIPS WORK
    # --------------------------------------------------

    def test_model_relationships(self):

        caterer_user, caterer = self.create_sample_caterer()
        customer = self.create_sample_customer()

        # Create menu and menu item.
        menu = Menu(
            caterer_id=caterer.id,
            menu_name="Wedding Menu",
            description="Wedding food selection"
        )

        db.session.add(menu)
        db.session.flush()

        menu_item = MenuItem(
            menu_id=menu.id,
            item_name="Chicken",
            description="Roasted chicken",
            price=Decimal("500.00")
        )

        db.session.add(menu_item)
        db.session.flush()

        # Create package and package item.
        package = self.create_sample_package(caterer)

        package_item = PackageItem(
            package_id=package.id,
            menu_item_id=menu_item.id
        )

        db.session.add(package_item)

        # Create add-on.
        addon = AddOn(
            caterer_id=caterer.id,
            addon_name="Extra Drinks",
            description="Additional drinks",
            price=Decimal("200.00")
        )

        db.session.add(addon)
        db.session.flush()

        # Create booking.
        booking = self.create_sample_booking(customer, caterer)

        # Add selected package to booking.
        booking_item = BookingItem(
            booking_id=booking.id,
            package_id=package.id,
            addon_id=None,
            quantity=100,
            unit_price=Decimal("1500.00")
        )

        db.session.add(booking_item)

        # Create availability.
        availability = Availability(
            caterer_id=caterer.id,
            available_date=date(2027, 5, 20),
            status="available"
        )

        db.session.add(availability)

        # Create payment.
        payment = Payment(
            booking_id=booking.id,
            amount=Decimal("50000.00"),
            payment_method="M-Pesa",
            transaction_reference="TEST-TRANSACTION-001",
            payment_status="successful"
        )

        db.session.add(payment)

        # Create review.
        review = Review(
            customer_id=customer.id,
            caterer_id=caterer.id,
            booking_id=booking.id,
            rating=5,
            comment="Excellent catering service"
        )

        db.session.add(review)

        # Create notification.
        notification = Notification(
            user_id=customer.id,
            message="Your booking has been received",
            notification_type="booking",
            is_read=False
        )

        db.session.add(notification)

        db.session.commit()

        # User and caterer profile.
        self.assertEqual(
            caterer_user.caterer_profile.id,
            caterer.id
        )
        self.assertEqual(caterer.user.id, caterer_user.id)

        # Caterer and menu.
        self.assertEqual(caterer.menus[0].menu_name, "Wedding Menu")
        self.assertEqual(menu.caterer.id, caterer.id)

        # Menu and menu item.
        self.assertEqual(menu.menu_items[0].item_name, "Chicken")
        self.assertEqual(menu_item.menu.id, menu.id)

        # Caterer and package.
        self.assertEqual(
            caterer.packages[0].package_name,
            "Wedding Package"
        )
        self.assertEqual(package.caterer.id, caterer.id)

        # Package and package item.
        self.assertEqual(package.package_items[0].id, package_item.id)
        self.assertEqual(package_item.package.id, package.id)

        # Package item and menu item.
        self.assertEqual(package_item.menu_item.id, menu_item.id)

        # Caterer and add-on.
        self.assertEqual(caterer.addons[0].id, addon.id)
        self.assertEqual(addon.caterer.id, caterer.id)

        # Customer and booking.
        self.assertEqual(customer.bookings[0].id, booking.id)
        self.assertEqual(booking.customer.id, customer.id)

        # Caterer and booking.
        self.assertEqual(booking.caterer.id, caterer.id)

        # Booking and booking item.
        self.assertEqual(booking.booking_items[0].id, booking_item.id)
        self.assertEqual(booking_item.booking.id, booking.id)

        # Booking item and package.
        self.assertEqual(booking_item.package.id, package.id)

        # Caterer and availability.
        self.assertEqual(
            caterer.availability_records[0].id,
            availability.id
        )
        self.assertEqual(availability.caterer.id, caterer.id)

        # Booking and payment.
        self.assertEqual(booking.payments[0].id, payment.id)
        self.assertEqual(payment.booking.id, booking.id)

        # Customer and review.
        self.assertEqual(customer.reviews[0].id, review.id)
        self.assertEqual(review.customer.id, customer.id)

        # Caterer and review.
        self.assertEqual(caterer.reviews[0].id, review.id)

        # Booking and review.
        self.assertEqual(booking.review.id, review.id)
        self.assertEqual(review.booking.id, booking.id)

        # User and notification.
        self.assertEqual(
            customer.notifications[0].id,
            notification.id
        )
        self.assertEqual(notification.user.id, customer.id)

    # --------------------------------------------------
    # TEST 4: FOREIGN KEY CONSTRAINTS
    # --------------------------------------------------

    def test_foreign_key_constraint(self):

        invalid_menu = Menu(
            caterer_id=9999,
            menu_name="Invalid Menu",
            description="Menu with invalid caterer"
        )

        db.session.add(invalid_menu)

        with self.assertRaises(IntegrityError):
            db.session.commit()

        db.session.rollback()

    # --------------------------------------------------
    # TEST 5: USER EMAIL MUST BE UNIQUE
    # --------------------------------------------------

    def test_unique_email_constraint(self):

        user1 = User(
            full_name="First User",
            email="same@example.com",
            password_hash="hashed_password",
            role="customer"
        )

        user2 = User(
            full_name="Second User",
            email="same@example.com",
            password_hash="hashed_password",
            role="customer"
        )

        db.session.add(user1)
        db.session.commit()

        db.session.add(user2)

        with self.assertRaises(IntegrityError):
            db.session.commit()

        db.session.rollback()

    # --------------------------------------------------
    # TEST 6: ONE CATERER PROFILE PER USER
    # --------------------------------------------------

    def test_one_caterer_per_user(self):

        user, caterer = self.create_sample_caterer()

        second_caterer = CatererProfile(
            user_id=user.id,
            business_name="Another Catering Business",
            location="Nairobi",
            contact_number="0700000000",
            verification_status="pending"
        )

        db.session.add(second_caterer)

        with self.assertRaises(IntegrityError):
            db.session.commit()

        db.session.rollback()

    # --------------------------------------------------
    # TEST 7: INVALID USER ROLE IS REJECTED
    # --------------------------------------------------

    def test_invalid_user_role_rejected(self):

        user = User(
            full_name="Invalid User",
            email="invalid@example.com",
            password_hash="hashed_password",
            role="invalid_role"
        )

        db.session.add(user)

        with self.assertRaises(IntegrityError):
            db.session.commit()

        db.session.rollback()

    # --------------------------------------------------
    # TEST 8: NEGATIVE MENU ITEM PRICE IS REJECTED
    # --------------------------------------------------

    def test_negative_menu_item_price_rejected(self):

        user, caterer = self.create_sample_caterer()

        menu = Menu(
            caterer_id=caterer.id,
            menu_name="Lunch Menu"
        )

        db.session.add(menu)
        db.session.flush()

        menu_item = MenuItem(
            menu_id=menu.id,
            item_name="Invalid Food",
            price=Decimal("-100.00")
        )

        db.session.add(menu_item)

        with self.assertRaises(IntegrityError):
            db.session.commit()

        db.session.rollback()

    # --------------------------------------------------
    # TEST 9: NEGATIVE PACKAGE PRICE IS REJECTED
    # --------------------------------------------------

    def test_negative_package_price_rejected(self):

        user, caterer = self.create_sample_caterer()

        package = Package(
            caterer_id=caterer.id,
            package_name="Invalid Package",
            price_per_guest=Decimal("-100.00"),
            minimum_guests=10
        )

        db.session.add(package)

        with self.assertRaises(IntegrityError):
            db.session.commit()

        db.session.rollback()

    # --------------------------------------------------
    # TEST 10: PACKAGE MINIMUM GUEST COUNT MUST BE POSITIVE
    # --------------------------------------------------

    def test_invalid_package_minimum_guests_rejected(self):

        user, caterer = self.create_sample_caterer()

        package = Package(
            caterer_id=caterer.id,
            package_name="Invalid Package",
            price_per_guest=Decimal("1000.00"),
            minimum_guests=0
        )

        db.session.add(package)

        with self.assertRaises(IntegrityError):
            db.session.commit()

        db.session.rollback()

    # --------------------------------------------------
    # TEST 11: MAXIMUM GUESTS CANNOT BE LESS THAN MINIMUM
    # --------------------------------------------------

    def test_invalid_package_guest_range_rejected(self):

        user, caterer = self.create_sample_caterer()

        package = Package(
            caterer_id=caterer.id,
            package_name="Invalid Guest Range",
            price_per_guest=Decimal("1000.00"),
            minimum_guests=100,
            maximum_guests=50
        )

        db.session.add(package)

        with self.assertRaises(IntegrityError):
            db.session.commit()

        db.session.rollback()

    # --------------------------------------------------
    # TEST 12: BOOKING GUEST COUNT MUST BE POSITIVE
    # --------------------------------------------------

    def test_invalid_booking_guest_count_rejected(self):

        user, caterer = self.create_sample_caterer()
        customer = self.create_sample_customer()

        booking = Booking(
            customer_id=customer.id,
            caterer_id=caterer.id,
            event_date=date(2027, 6, 10),
            event_type="Birthday",
            event_location="Nairobi",
            guest_count=0,
            estimated_total=Decimal("0.00"),
            status="pending"
        )

        db.session.add(booking)

        with self.assertRaises(IntegrityError):
            db.session.commit()

        db.session.rollback()

    # --------------------------------------------------
    # TEST 13: BOOKING ITEM QUANTITY MUST BE POSITIVE
    # --------------------------------------------------

    def test_invalid_booking_item_quantity_rejected(self):

        user, caterer = self.create_sample_caterer()
        customer = self.create_sample_customer()

        package = self.create_sample_package(caterer)
        booking = self.create_sample_booking(customer, caterer)

        booking_item = BookingItem(
            booking_id=booking.id,
            package_id=package.id,
            addon_id=None,
            quantity=0,
            unit_price=Decimal("1500.00")
        )

        db.session.add(booking_item)

        with self.assertRaises(IntegrityError):
            db.session.commit()

        db.session.rollback()

    # --------------------------------------------------
    # TEST 14: BOOKING ITEM MUST HAVE PACKAGE OR ADD-ON
    # --------------------------------------------------

    def test_booking_item_requires_package_or_addon(self):

        user, caterer = self.create_sample_caterer()
        customer = self.create_sample_customer()

        booking = self.create_sample_booking(customer, caterer)

        booking_item = BookingItem(
            booking_id=booking.id,
            package_id=None,
            addon_id=None,
            quantity=1,
            unit_price=Decimal("500.00")
        )

        db.session.add(booking_item)

        with self.assertRaises(IntegrityError):
            db.session.commit()

        db.session.rollback()

    # --------------------------------------------------
    # TEST 15: AVAILABILITY STATUS MUST BE VALID
    # --------------------------------------------------

    def test_invalid_availability_status_rejected(self):

        user, caterer = self.create_sample_caterer()

        availability = Availability(
            caterer_id=caterer.id,
            available_date=date(2027, 5, 20),
            status="invalid"
        )

        db.session.add(availability)

        with self.assertRaises(IntegrityError):
            db.session.commit()

        db.session.rollback()

    # --------------------------------------------------
    # TEST 16: CATERER CANNOT HAVE DUPLICATE AVAILABILITY DATE
    # --------------------------------------------------

    def test_unique_caterer_availability_date(self):

        user, caterer = self.create_sample_caterer()

        first = Availability(
            caterer_id=caterer.id,
            available_date=date(2027, 5, 20),
            status="available"
        )

        second = Availability(
            caterer_id=caterer.id,
            available_date=date(2027, 5, 20),
            status="unavailable"
        )

        db.session.add(first)
        db.session.commit()

        db.session.add(second)

        with self.assertRaises(IntegrityError):
            db.session.commit()

        db.session.rollback()

    # --------------------------------------------------
    # TEST 17: PAYMENT AMOUNT CANNOT BE NEGATIVE
    # --------------------------------------------------

    def test_negative_payment_amount_rejected(self):

        user, caterer = self.create_sample_caterer()
        customer = self.create_sample_customer()

        booking = self.create_sample_booking(customer, caterer)

        payment = Payment(
            booking_id=booking.id,
            amount=Decimal("-100.00"),
            payment_method="M-Pesa",
            payment_status="pending"
        )

        db.session.add(payment)

        with self.assertRaises(IntegrityError):
            db.session.commit()

        db.session.rollback()

    # --------------------------------------------------
    # TEST 18: REVIEW RATING MUST BE BETWEEN 1 AND 5
    # --------------------------------------------------

    def test_invalid_review_rating_rejected(self):

        user, caterer = self.create_sample_caterer()
        customer = self.create_sample_customer()

        booking = self.create_sample_booking(customer, caterer)

        review = Review(
            customer_id=customer.id,
            caterer_id=caterer.id,
            booking_id=booking.id,
            rating=6,
            comment="Invalid rating"
        )

        db.session.add(review)

        with self.assertRaises(IntegrityError):
            db.session.commit()

        db.session.rollback()

    # --------------------------------------------------
    # TEST 19: REVIEW BOOKING ID MUST BE UNIQUE
    # --------------------------------------------------

    def test_one_review_per_booking(self):

        user, caterer = self.create_sample_caterer()
        customer = self.create_sample_customer()

        booking = self.create_sample_booking(customer, caterer)

        review1 = Review(
            customer_id=customer.id,
            caterer_id=caterer.id,
            booking_id=booking.id,
            rating=5,
            comment="Excellent service"
        )

        db.session.add(review1)
        db.session.commit()

        review2 = Review(
            customer_id=customer.id,
            caterer_id=caterer.id,
            booking_id=booking.id,
            rating=4,
            comment="Another review"
        )

        db.session.add(review2)

        with self.assertRaises(IntegrityError):
            db.session.commit()

        db.session.rollback()


if __name__ == "__main__":
    unittest.main(verbosity=2)
