
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

from werkzeug.security import generate_password_hash

from app import create_app
from extensions import db

from models import User, Caterer, Menu, Package, Booking, Order


# ============================================================
# HELPER FUNCTION
# ============================================================

def get_or_create(model, lookup, defaults=None):
    """
    Find an existing record or create a new one.
    Prevents duplicate sample records when the script is rerun.
    """

    record = db.session.query(model).filter_by(**lookup).first()

    if record:
        return record

    values = dict(lookup)

    if defaults:
        values.update(defaults)

    record = model(**values)

    db.session.add(record)
    db.session.flush()

    return record


# ============================================================
# SEED USERS
# ============================================================

def seed_users():

    print("Seeding users...")

    sample_password = generate_password_hash("SokoCater123!")

    admin = get_or_create(
        User,
        {"email": "admin@sokocater.com"},
        {
            "full_name": "SokoCater Admin",
            "password_hash": sample_password,
            "role": "admin",
            "phone": "0711000001"
        }
    )

    customer_one = get_or_create(
        User,
        {"email": "customer1@example.com"},
        {
            "full_name": "Jane Wanjiku",
            "password_hash": sample_password,
            "role": "customer",
            "phone": "0711000002"
        }
    )

    customer_two = get_or_create(
        User,
        {"email": "customer2@example.com"},
        {
            "full_name": "Brian Otieno",
            "password_hash": sample_password,
            "role": "customer",
            "phone": "0711000003"
        }
    )

    caterer_user_one = get_or_create(
        User,
        {"email": "greenplate@example.com"},
        {
            "full_name": "Mary Njeri",
            "password_hash": sample_password,
            "role": "caterer",
            "phone": "0711000004"
        }
    )

    caterer_user_two = get_or_create(
        User,
        {"email": "tastehub@example.com"},
        {
            "full_name": "David Mwangi",
            "password_hash": sample_password,
            "role": "caterer",
            "phone": "0711000005"
        }
    )

    return {
        "admin": admin,
        "customer_one": customer_one,
        "customer_two": customer_two,
        "caterer_user_one": caterer_user_one,
        "caterer_user_two": caterer_user_two
    }


# ============================================================
# SEED CATERERS
# ============================================================

def seed_caterers(users):

    print("Seeding caterers...")

    caterer_one = get_or_create(
        Caterer,
        {"user_id": users["caterer_user_one"].id},
        {
            "business_name": "Green Plate Catering",
            "description": "Fresh and delicious catering for weddings and events.",
            "location": "Nairobi",
            "contact_number": "0711222333"
        }
    )

    caterer_two = get_or_create(
        Caterer,
        {"user_id": users["caterer_user_two"].id},
        {
            "business_name": "Taste Hub Events",
            "description": "Professional catering for corporate and private events.",
            "location": "Kiambu",
            "contact_number": "0722333444"
        }
    )

    return {
        "caterer_one": caterer_one,
        "caterer_two": caterer_two
    }


# ============================================================
# SEED MENUS
# ============================================================

def seed_menus(caterers):

    print("Seeding menus...")

    menu_one = get_or_create(
        Menu,
        {
            "caterer_id": caterers["caterer_one"].id,
            "name": "Wedding Menu"
        },
        {
            "description": "A selection of meals suitable for weddings.",
            "price": Decimal("1500.00")
        }
    )

    menu_two = get_or_create(
        Menu,
        {
            "caterer_id": caterers["caterer_two"].id,
            "name": "Corporate Menu"
        },
        {
            "description": "Professional catering options for corporate events.",
            "price": Decimal("1200.00")
        }
    )

    return {
        "menu_one": menu_one,
        "menu_two": menu_two
    }


# ============================================================
# SEED PACKAGES
# ============================================================

def seed_packages(caterers):

    print("Seeding packages...")

    package_one = get_or_create(
        Package,
        {
            "caterer_id": caterers["caterer_one"].id,
            "name": "Classic Wedding Package"
        },
        {
            "category": "Wedding Catering",
            "description": "A complete wedding catering package."
        }
    )

    package_two = get_or_create(
        Package,
        {
            "caterer_id": caterers["caterer_two"].id,
            "name": "Corporate Lunch Package"
        },
        {
            "category": "Corporate Events",
            "description": "A convenient package for corporate events."
        }
    )

    return {
        "package_one": package_one,
        "package_two": package_two
    }


# ============================================================
# SEED BOOKINGS
# ============================================================

def seed_bookings(users, caterers, packages):

    print("Seeding bookings...")

    booking_one = get_or_create(
        Booking,
        {
            "user_id": users["customer_one"].id,
            "caterer_id": caterers["caterer_one"].id,
            "package_id": packages["package_one"].id,
            "event_date": date.today() + timedelta(days=30),
            "event_type": "Wedding"
        },
        {
            "event_location": "Nairobi",
            "guest_count": 80,
            "price_per_person": Decimal("1500.00"),
            "estimated_total": Decimal("120000.00"),
            "status": "pending"
        }
    )

    booking_two = get_or_create(
        Booking,
        {
            "user_id": users["customer_two"].id,
            "caterer_id": caterers["caterer_two"].id,
            "package_id": packages["package_two"].id,
            "event_date": date.today() + timedelta(days=60),
            "event_type": "Corporate Event"
        },
        {
            "event_location": "Kiambu",
            "guest_count": 50,
            "price_per_person": Decimal("1200.00"),
            "estimated_total": Decimal("60000.00"),
            "status": "confirmed"
        }
    )

    return {
        "booking_one": booking_one,
        "booking_two": booking_two
    }


# ============================================================
# SEED ORDERS
# ============================================================

def seed_orders(users, caterers, menus):

    print("Seeding orders...")

    order_one = get_or_create(
        Order,
        {
            "user_id": users["customer_one"].id,
            "caterer_id": caterers["caterer_one"].id,
            "menu_id": menus["menu_one"].id
        },
        {
            "quantity": 2,
            "unit_price": Decimal("1500.00"),
            "total_amount": Decimal("3000.00"),
            "status": "pending",
            "order_date": datetime.now(UTC)
        }
    )

    order_two = get_or_create(
        Order,
        {
            "user_id": users["customer_two"].id,
            "caterer_id": caterers["caterer_two"].id,
            "menu_id": menus["menu_two"].id
        },
        {
            "quantity": 3,
            "unit_price": Decimal("1200.00"),
            "total_amount": Decimal("3600.00"),
            "status": "pending",
            "order_date": datetime.now(UTC)
        }
    )

    return {
        "order_one": order_one,
        "order_two": order_two
    }


# ============================================================
# MAIN SEED FUNCTION
# ============================================================

def seed_database():

    print("\nStarting SokoCater database seeding...\n")

    try:
        # Seed records in foreign-key dependency order.
        # Database tables must already exist and match the models.

        users = seed_users()

        caterers = seed_caterers(users)

        menus = seed_menus(caterers)

        packages = seed_packages(caterers)

        bookings = seed_bookings(users, caterers, packages)

        orders = seed_orders(users, caterers, menus)

        # Save all changes.
        db.session.commit()

        print("\n========================================")
        print("SokoCater database seeded successfully!")
        print("========================================")

        print("\nSample login accounts:")
        print("Admin:     admin@sokocater.com")
        print("Customer:  customer1@example.com")
        print("Caterer:   greenplate@example.com")
        print("Password:  SokoCater123!")

        print("\n========================================\n")

    except Exception as error:

        db.session.rollback()

        print("\nDatabase seeding failed!")
        print(f"Error: {error}")

        raise


# ============================================================
# SCRIPT ENTRY POINT
# ============================================================

if __name__ == "__main__":

    app = create_app()

    with app.app_context():
        seed_database()
