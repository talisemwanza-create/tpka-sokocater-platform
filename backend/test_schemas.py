
import unittest

from decimal import Decimal
from datetime import date

from marshmallow import ValidationError

from schemas import (
    CatererSchema,
    MenuSchema,
    PackageSchema,
    BookingSchema
)


class TestCatererSchema(unittest.TestCase):

    def setUp(self):
        self.schema = CatererSchema()

    def valid_data(self):
        return {
            "user_id": 1,
            "business_name": "Kate Catering",
            "description": "Professional catering services",
            "location": "Nairobi",
            "contact_number": "0712345678"
        }

    def test_valid_caterer_data(self):
        result = self.schema.load(self.valid_data())

        self.assertEqual(result["user_id"], 1)
        self.assertEqual(result["business_name"], "Kate Catering")

    def test_missing_business_name(self):
        data = self.valid_data()
        del data["business_name"]

        with self.assertRaises(ValidationError):
            self.schema.load(data)

    def test_invalid_user_id(self):
        data = self.valid_data()
        data["user_id"] = 0

        with self.assertRaises(ValidationError):
            self.schema.load(data)

    def test_verification_status_cannot_be_supplied(self):
        data = self.valid_data()
        data["verification_status"] = "verified"

        with self.assertRaises(ValidationError):
            self.schema.load(data)


class TestMenuSchema(unittest.TestCase):

    def setUp(self):
        self.schema = MenuSchema()

    def valid_data(self):
        return {
            "caterer_id": 1,
            "menu_name": "Wedding Menu",
            "description": "A special wedding menu"
        }

    def test_valid_menu_data(self):
        result = self.schema.load(self.valid_data())

        self.assertEqual(result["caterer_id"], 1)
        self.assertEqual(result["menu_name"], "Wedding Menu")

    def test_missing_menu_name(self):
        data = self.valid_data()
        del data["menu_name"]

        with self.assertRaises(ValidationError):
            self.schema.load(data)

    def test_invalid_caterer_id(self):
        data = self.valid_data()
        data["caterer_id"] = 0

        with self.assertRaises(ValidationError):
            self.schema.load(data)

    def test_menu_name_too_short(self):
        data = self.valid_data()
        data["menu_name"] = "A"

        with self.assertRaises(ValidationError):
            self.schema.load(data)


class TestPackageSchema(unittest.TestCase):

    def setUp(self):
        self.schema = PackageSchema()

    def valid_data(self):
        return {
            "caterer_id": 1,
            "package_name": "Premium Package",
            "description": "A premium catering package",
            "price_per_guest": "1500.00",
            "minimum_guests": 20,
            "maximum_guests": 200
        }

    def test_valid_package_data(self):
        result = self.schema.load(self.valid_data())

        self.assertEqual(result["caterer_id"], 1)
        self.assertEqual(result["package_name"], "Premium Package")
        self.assertEqual(
            result["price_per_guest"],
            Decimal("1500.00")
        )

    def test_missing_package_name(self):
        data = self.valid_data()
        del data["package_name"]

        with self.assertRaises(ValidationError):
            self.schema.load(data)

    def test_invalid_caterer_id(self):
        data = self.valid_data()
        data["caterer_id"] = 0

        with self.assertRaises(ValidationError):
            self.schema.load(data)

    def test_negative_package_price(self):
        data = self.valid_data()
        data["price_per_guest"] = "-100.00"

        with self.assertRaises(ValidationError):
            self.schema.load(data)

    def test_invalid_minimum_guests(self):
        data = self.valid_data()
        data["minimum_guests"] = 0

        with self.assertRaises(ValidationError):
            self.schema.load(data)

    def test_maximum_guests_can_be_optional(self):
        data = self.valid_data()
        del data["maximum_guests"]

        result = self.schema.load(data)

        self.assertNotIn("maximum_guests", result)


class TestBookingSchema(unittest.TestCase):

    def setUp(self):
        self.schema = BookingSchema()

    def valid_data(self):
        return {
            "caterer_id": 2,
            "package_id": 3,
            "event_date": "2027-05-20",
            "event_type": "Wedding",
            "event_location": "Nairobi",
            "guest_count": 100
        }

    def test_valid_booking_data(self):
        result = self.schema.load(self.valid_data())

        self.assertEqual(result["caterer_id"], 2)
        self.assertEqual(result["package_id"], 3)
        self.assertEqual(result["event_type"], "Wedding")
        self.assertEqual(result["guest_count"], 100)
        self.assertEqual(result["event_date"], date(2027, 5, 20))

    def test_missing_package_id(self):
        data = self.valid_data()
        del data["package_id"]

        with self.assertRaises(ValidationError):
            self.schema.load(data)

    def test_invalid_caterer_id(self):
        data = self.valid_data()
        data["caterer_id"] = 0

        with self.assertRaises(ValidationError):
            self.schema.load(data)

    def test_invalid_package_id(self):
        data = self.valid_data()
        data["package_id"] = 0

        with self.assertRaises(ValidationError):
            self.schema.load(data)

    def test_invalid_guest_count(self):
        data = self.valid_data()
        data["guest_count"] = 0

        with self.assertRaises(ValidationError):
            self.schema.load(data)

    def test_invalid_event_date(self):
        data = self.valid_data()
        data["event_date"] = "not-a-date"

        with self.assertRaises(ValidationError):
            self.schema.load(data)

    def test_missing_event_type(self):
        data = self.valid_data()
        del data["event_type"]

        with self.assertRaises(ValidationError):
            self.schema.load(data)

    def test_customer_id_is_not_accepted_as_input(self):
        data = self.valid_data()
        data["customer_id"] = 1

        with self.assertRaises(ValidationError):
            self.schema.load(data)

    def test_status_is_not_accepted_as_input(self):
        data = self.valid_data()
        data["status"] = "completed"

        with self.assertRaises(ValidationError):
            self.schema.load(data)

    def test_estimated_total_is_not_accepted_as_input(self):
        data = self.valid_data()
        data["estimated_total"] = "150000.00"

        with self.assertRaises(ValidationError):
            self.schema.load(data)

    def test_package_id_is_not_in_dumped_output(self):
        data = {
            "id": 1,
            "customer_id": 2,
            "caterer_id": 3,
            "package_id": 4,
            "event_date": date(2027, 5, 20),
            "event_type": "Wedding",
            "event_location": "Nairobi",
            "guest_count": 100,
            "estimated_total": Decimal("150000.00"),
            "status": "pending"
        }

        result = self.schema.dump(data)

        self.assertNotIn("package_id", result)
        self.assertEqual(result["customer_id"], 2)
        self.assertEqual(result["estimated_total"], "150000.00")
        self.assertEqual(result["status"], "pending")


if __name__ == "__main__":
    unittest.main(verbosity=2)
