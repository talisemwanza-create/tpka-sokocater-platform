
from datetime import UTC, datetime

from sqlalchemy import CheckConstraint, UniqueConstraint

from extensions import db


# ============================================================
# 1. USER MODEL
# ============================================================

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    phone_number = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(UTC))

    __table_args__ = (
        CheckConstraint(
            "role IN ('customer', 'caterer', 'admin')",
            name="check_user_role"
        ),
    )

    # One user can have one caterer profile
    caterer_profile = db.relationship(
        "CatererProfile",
        back_populates="user",
        uselist=False
    )

    # One customer can make many bookings
    bookings = db.relationship(
        "Booking",
        back_populates="customer",
        foreign_keys="Booking.customer_id"
    )

    reviews = db.relationship(
        "Review",
        back_populates="customer"
    )

    notifications = db.relationship(
        "Notification",
        back_populates="user"
    )


# ============================================================
# 2. CATERER PROFILE MODEL
# ============================================================

class CatererProfile(db.Model):
    __tablename__ = "caterer_profiles"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        unique=True,
        nullable=False
    )

    business_name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    location = db.Column(db.String(150), nullable=False)
    contact_number = db.Column(db.String(20))
    business_image = db.Column(db.String(255))
    verification_status = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(UTC))

    user = db.relationship(
        "User",
        back_populates="caterer_profile"
    )

    menus = db.relationship(
        "Menu",
        back_populates="caterer"
    )

    packages = db.relationship(
        "Package",
        back_populates="caterer"
    )

    addons = db.relationship(
        "AddOn",
        back_populates="caterer"
    )

    bookings = db.relationship(
        "Booking",
        back_populates="caterer"
    )

    availability_records = db.relationship(
        "Availability",
        back_populates="caterer"
    )

    reviews = db.relationship(
        "Review",
        back_populates="caterer"
    )


# ============================================================
# 3. MENU MODEL
# ============================================================

class Menu(db.Model):
    __tablename__ = "menus"

    id = db.Column(db.Integer, primary_key=True)

    caterer_id = db.Column(
        db.Integer,
        db.ForeignKey("caterer_profiles.id"),
        nullable=False
    )

    menu_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(UTC))

    caterer = db.relationship(
        "CatererProfile",
        back_populates="menus"
    )

    menu_items = db.relationship(
        "MenuItem",
        back_populates="menu"
    )


# ============================================================
# 4. MENU ITEM MODEL
# ============================================================

class MenuItem(db.Model):
    __tablename__ = "menu_items"

    id = db.Column(db.Integer, primary_key=True)

    menu_id = db.Column(
        db.Integer,
        db.ForeignKey("menus.id"),
        nullable=False
    )

    item_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    image_url = db.Column(db.String(255))

    __table_args__ = (
        CheckConstraint("price >= 0", name="check_menu_item_price"),
    )

    menu = db.relationship(
        "Menu",
        back_populates="menu_items"
    )

    package_items = db.relationship(
        "PackageItem",
        back_populates="menu_item"
    )


# ============================================================
# 5. PACKAGE MODEL
# ============================================================

class Package(db.Model):
    __tablename__ = "packages"

    id = db.Column(db.Integer, primary_key=True)

    caterer_id = db.Column(
        db.Integer,
        db.ForeignKey("caterer_profiles.id"),
        nullable=False
    )

    package_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price_per_guest = db.Column(db.Numeric(10, 2), nullable=False)
    minimum_guests = db.Column(db.Integer, nullable=False)
    maximum_guests = db.Column(db.Integer)

    __table_args__ = (
        CheckConstraint(
            "price_per_guest >= 0",
            name="check_package_price"
        ),
        CheckConstraint(
            "minimum_guests > 0",
            name="check_package_minimum_guests"
        ),
        CheckConstraint(
            "maximum_guests IS NULL OR maximum_guests >= minimum_guests",
            name="check_package_guest_range"
        ),
    )

    caterer = db.relationship(
        "CatererProfile",
        back_populates="packages"
    )

    package_items = db.relationship(
        "PackageItem",
        back_populates="package"
    )

    booking_items = db.relationship(
        "BookingItem",
        back_populates="package"
    )


# ============================================================
# 6. PACKAGE ITEM MODEL
# ============================================================

class PackageItem(db.Model):
    __tablename__ = "package_items"

    id = db.Column(db.Integer, primary_key=True)

    package_id = db.Column(
        db.Integer,
        db.ForeignKey("packages.id"),
        nullable=False
    )

    menu_item_id = db.Column(
        db.Integer,
        db.ForeignKey("menu_items.id"),
        nullable=False
    )

    __table_args__ = (
        UniqueConstraint(
            "package_id",
            "menu_item_id",
            name="unique_package_menu_item"
        ),
    )

    package = db.relationship(
        "Package",
        back_populates="package_items"
    )

    menu_item = db.relationship(
        "MenuItem",
        back_populates="package_items"
    )


# ============================================================
# 7. ADD-ON MODEL
# ============================================================

class AddOn(db.Model):
    __tablename__ = "add_ons"

    id = db.Column(db.Integer, primary_key=True)

    caterer_id = db.Column(
        db.Integer,
        db.ForeignKey("caterer_profiles.id"),
        nullable=False
    )

    addon_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2), nullable=False)

    __table_args__ = (
        CheckConstraint("price >= 0", name="check_addon_price"),
    )

    caterer = db.relationship(
        "CatererProfile",
        back_populates="addons"
    )

    booking_items = db.relationship(
        "BookingItem",
        back_populates="addon"
    )


# ============================================================
# 8. BOOKING MODEL
# ============================================================

class Booking(db.Model):
    __tablename__ = "bookings"

    id = db.Column(db.Integer, primary_key=True)

    customer_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    caterer_id = db.Column(
        db.Integer,
        db.ForeignKey("caterer_profiles.id"),
        nullable=False
    )

    event_date = db.Column(db.Date, nullable=False)
    event_type = db.Column(db.String(100), nullable=False)
    event_location = db.Column(db.String(200), nullable=False)
    guest_count = db.Column(db.Integer, nullable=False)
    estimated_total = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="pending")
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(UTC))

    __table_args__ = (
        CheckConstraint(
            "guest_count > 0",
            name="check_booking_guest_count"
        ),
        CheckConstraint(
            "estimated_total >= 0",
            name="check_booking_total"
        ),
        CheckConstraint(
            "status IN ('pending', 'accepted', 'rejected', "
            "'confirmed', 'cancelled', 'completed')",
            name="check_booking_status"
        ),
    )

    customer = db.relationship(
        "User",
        back_populates="bookings",
        foreign_keys=[customer_id]
    )

    caterer = db.relationship(
        "CatererProfile",
        back_populates="bookings"
    )

    booking_items = db.relationship(
        "BookingItem",
        back_populates="booking"
    )

    payments = db.relationship(
        "Payment",
        back_populates="booking"
    )

    review = db.relationship(
        "Review",
        back_populates="booking",
        uselist=False
    )


# ============================================================
# 9. BOOKING ITEM MODEL
# ============================================================

class BookingItem(db.Model):
    __tablename__ = "booking_items"

    id = db.Column(db.Integer, primary_key=True)

    booking_id = db.Column(
        db.Integer,
        db.ForeignKey("bookings.id"),
        nullable=False
    )

    package_id = db.Column(
        db.Integer,
        db.ForeignKey("packages.id"),
        nullable=True
    )

    addon_id = db.Column(
        db.Integer,
        db.ForeignKey("add_ons.id"),
        nullable=True
    )

    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)

    __table_args__ = (
        CheckConstraint(
            "(package_id IS NOT NULL AND addon_id IS NULL) OR "
            "(package_id IS NULL AND addon_id IS NOT NULL)",
            name="check_booking_item_selection"
        ),
        CheckConstraint(
            "quantity > 0",
            name="check_booking_item_quantity"
        ),
        CheckConstraint(
            "unit_price >= 0",
            name="check_booking_item_price"
        ),
    )

    booking = db.relationship(
        "Booking",
        back_populates="booking_items"
    )

    package = db.relationship(
        "Package",
        back_populates="booking_items"
    )

    addon = db.relationship(
        "AddOn",
        back_populates="booking_items"
    )


# ============================================================
# 10. AVAILABILITY MODEL
# ============================================================

class Availability(db.Model):
    __tablename__ = "availability"

    id = db.Column(db.Integer, primary_key=True)

    caterer_id = db.Column(
        db.Integer,
        db.ForeignKey("caterer_profiles.id"),
        nullable=False
    )

    available_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "caterer_id",
            "available_date",
            name="unique_caterer_availability_date"
        ),
        CheckConstraint(
            "status IN ('available', 'unavailable', 'booked')",
            name="check_availability_status"
        ),
    )

    caterer = db.relationship(
        "CatererProfile",
        back_populates="availability_records"
    )


# ============================================================
# 11. PAYMENT MODEL
# ============================================================

class Payment(db.Model):
    __tablename__ = "payments"

    id = db.Column(db.Integer, primary_key=True)

    booking_id = db.Column(
        db.Integer,
        db.ForeignKey("bookings.id"),
        nullable=False
    )

    amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)

    transaction_reference = db.Column(
        db.String(100),
        unique=True
    )

    payment_status = db.Column(db.String(20), nullable=False)
    paid_at = db.Column(db.DateTime)

    __table_args__ = (
        CheckConstraint(
            "amount >= 0",
            name="check_payment_amount"
        ),
        CheckConstraint(
            "payment_status IN ('pending', 'successful', 'failed')",
            name="check_payment_status"
        ),
    )

    booking = db.relationship(
        "Booking",
        back_populates="payments"
    )


# ============================================================
# 12. REVIEW MODEL
# ============================================================

class Review(db.Model):
    __tablename__ = "reviews"

    id = db.Column(db.Integer, primary_key=True)

    customer_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    caterer_id = db.Column(
        db.Integer,
        db.ForeignKey("caterer_profiles.id"),
        nullable=False
    )

    booking_id = db.Column(
        db.Integer,
        db.ForeignKey("bookings.id"),
        unique=True,
        nullable=False
    )

    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(UTC))

    __table_args__ = (
        CheckConstraint(
            "rating >= 1 AND rating <= 5",
            name="check_review_rating"
        ),
    )

    customer = db.relationship(
        "User",
        back_populates="reviews"
    )

    caterer = db.relationship(
        "CatererProfile",
        back_populates="reviews"
    )

    booking = db.relationship(
        "Booking",
        back_populates="review"
    )


# ============================================================
# 13. NOTIFICATION MODEL
# ============================================================

class Notification(db.Model):
    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(50), nullable=False)
    is_read = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(UTC))

    user = db.relationship(
        "User",
        back_populates="notifications"
    )


# Backward-compatible name used by existing routes
Caterer = CatererProfile

