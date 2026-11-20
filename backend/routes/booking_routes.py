from decimal import Decimal

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from sqlalchemy.exc import IntegrityError
from marshmallow import ValidationError

from extensions import db
from models import Booking, BookingItem, User, Caterer, Package
from schemas.booking_schema import BookingSchema


booking_bp = Blueprint("bookings", __name__)

booking_schema = BookingSchema()
bookings_schema = BookingSchema(many=True)


def get_booking_total(booking):
    """Calculate the total from all booking items."""
    total = Decimal("0.00")

    for item in booking.booking_items:
        total += Decimal(str(item.unit_price)) * item.quantity

    return total


def validate_package(package, caterer_id, guest_count):
    """Check that a package belongs to the caterer and supports the guest count."""

    if not package:
        return "Package not found"

    if package.caterer_id != caterer_id:
        return "Selected package does not belong to this caterer"

    if guest_count < package.minimum_guests:
        return (
            f"This package requires at least "
            f"{package.minimum_guests} guests"
        )

    if (
        package.maximum_guests is not None
        and guest_count > package.maximum_guests
    ):
        return (
            f"This package supports a maximum of "
            f"{package.maximum_guests} guests"
        )

    return None


# ============================================================
# GET ALL BOOKINGS
# ============================================================

@booking_bp.route("/api/bookings", methods=["GET"])
@jwt_required()
def get_bookings():

    current_user_id = int(get_jwt_identity())
    current_role = get_jwt().get("role")

    if current_role == "customer":

        bookings = Booking.query.filter_by(
            customer_id=current_user_id
        ).all()

    elif current_role == "caterer":

        caterer = Caterer.query.filter_by(
            user_id=current_user_id
        ).first()

        if not caterer:
            return jsonify({
                "error": "Caterer profile not found"
            }), 404

        bookings = Booking.query.filter_by(
            caterer_id=caterer.id
        ).all()

    else:
        return jsonify({
            "error": "Access forbidden"
        }), 403

    return jsonify({
        "message": "Bookings retrieved successfully",
        "data": bookings_schema.dump(bookings)
    }), 200


# ============================================================
# GET ONE BOOKING
# ============================================================

@booking_bp.route("/api/bookings/<int:booking_id>", methods=["GET"])
@jwt_required()
def get_booking(booking_id):

    current_user_id = int(get_jwt_identity())
    current_role = get_jwt().get("role")

    booking = db.session.get(Booking, booking_id)

    if not booking:
        return jsonify({
            "error": "Booking not found"
        }), 404

    if current_role == "customer":

        if booking.customer_id != current_user_id:
            return jsonify({
                "error": "You are not authorized to view this booking"
            }), 403

    elif current_role == "caterer":

        caterer = Caterer.query.filter_by(
            user_id=current_user_id
        ).first()

        if not caterer or booking.caterer_id != caterer.id:
            return jsonify({
                "error": "You are not authorized to view this booking"
            }), 403

    else:
        return jsonify({
            "error": "Access forbidden"
        }), 403

    return jsonify({
        "data": booking_schema.dump(booking)
    }), 200


# ============================================================
# CREATE BOOKING
# CUSTOMER ONLY
# ============================================================

@booking_bp.route("/api/bookings", methods=["POST"])
@jwt_required()
def create_booking():

    current_user_id = int(get_jwt_identity())
    current_role = get_jwt().get("role")

    if current_role != "customer":
        return jsonify({
            "error": "Only customers can create bookings"
        }), 403

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Invalid JSON body"
        }), 400

    try:
        validated_data = booking_schema.load(data)

        user = db.session.get(User, current_user_id)

        if not user:
            return jsonify({
                "error": "Customer not found"
            }), 404

        caterer = db.session.get(
            Caterer,
            validated_data["caterer_id"]
        )

        if not caterer:
            return jsonify({
                "error": "Caterer not found"
            }), 404

        package = db.session.get(
            Package,
            validated_data["package_id"]
        )

        package_error = validate_package(
            package,
            caterer.id,
            validated_data["guest_count"]
        )

        if package_error:
            return jsonify({
                "error": package_error
            }), 400

        guest_count = validated_data["guest_count"]

        estimated_total = (
            Decimal(str(package.price_per_guest)) * guest_count
        )

        booking = Booking(
            customer_id=current_user_id,
            caterer_id=caterer.id,
            event_date=validated_data["event_date"],
            event_type=validated_data["event_type"],
            event_location=validated_data["event_location"],
            guest_count=guest_count,
            estimated_total=estimated_total
        )

        db.session.add(booking)
        db.session.flush()

        booking_item = BookingItem(
            booking_id=booking.id,
            package_id=package.id,
            addon_id=None,
            quantity=guest_count,
            unit_price=package.price_per_guest
        )

        db.session.add(booking_item)
        db.session.commit()

        return jsonify({
            "message": "Booking created successfully",
            "data": booking_schema.dump(booking)
        }), 201

    except ValidationError as error:
        db.session.rollback()

        return jsonify({
            "error": error.messages
        }), 400

    except IntegrityError:
        db.session.rollback()

        return jsonify({
            "error": "Unable to create booking"
        }), 409


# ============================================================
# UPDATE BOOKING
# CUSTOMER: UPDATE OWN BOOKING DETAILS
# CATERER: UPDATE BOOKING STATUS
# ============================================================

@booking_bp.route("/api/bookings/<int:booking_id>", methods=["PUT"])
@jwt_required()
def update_booking(booking_id):

    current_user_id = int(get_jwt_identity())
    current_role = get_jwt().get("role")

    booking = db.session.get(Booking, booking_id)

    if not booking:
        return jsonify({
            "error": "Booking not found"
        }), 404

    if current_role == "customer":

        if booking.customer_id != current_user_id:
            return jsonify({
                "error": "You are not authorized to update this booking"
            }), 403

    elif current_role == "caterer":

        caterer = Caterer.query.filter_by(
            user_id=current_user_id
        ).first()

        if not caterer or booking.caterer_id != caterer.id:
            return jsonify({
                "error": "You are not authorized to update this booking"
            }), 403

    else:
        return jsonify({
            "error": "Access forbidden"
        }), 403

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Invalid JSON body"
        }), 400

    try:

        # Caterers can update booking status only.
        if current_role == "caterer":

            allowed_statuses = [
                "pending",
                "accepted",
                "rejected",
                "confirmed",
                "cancelled",
                "completed"
            ]

            if set(data.keys()) != {"status"}:
                return jsonify({
                    "error": "Caterers can only update booking status"
                }), 400

            if data["status"] not in allowed_statuses:
                return jsonify({
                    "error": "Invalid booking status"
                }), 400

            booking.status = data["status"]

        # Customers can update their own booking details.
        elif current_role == "customer":

            allowed_fields = {
                "caterer_id",
                "package_id",
                "event_date",
                "event_type",
                "event_location",
                "guest_count"
            }

            if not data:
                return jsonify({
                    "error": "No update data provided"
                }), 400

            if not set(data.keys()).issubset(allowed_fields):
                return jsonify({
                    "error": "You cannot update the supplied fields"
                }), 403

            validated_data = booking_schema.load(
                data,
                partial=True
            )

            new_caterer_id = validated_data.get(
                "caterer_id",
                booking.caterer_id
            )

            new_guest_count = validated_data.get(
                "guest_count",
                booking.guest_count
            )

            # Find the existing package booking item.
            package_item = next(
                (
                    item for item in booking.booking_items
                    if item.package_id is not None
                ),
                None
            )

            if "package_id" in validated_data:

                new_package = db.session.get(
                    Package,
                    validated_data["package_id"]
                )

            elif package_item:

                new_package = db.session.get(
                    Package,
                    package_item.package_id
                )

            else:
                return jsonify({
                    "error": "The booking has no package item"
                }), 400

            caterer = db.session.get(
                Caterer,
                new_caterer_id
            )

            if not caterer:
                return jsonify({
                    "error": "Caterer not found"
                }), 404

            package_error = validate_package(
                new_package,
                caterer.id,
                new_guest_count
            )

            if package_error:
                return jsonify({
                    "error": package_error
                }), 400

            booking.caterer_id = caterer.id

            for field in [
                "event_date",
                "event_type",
                "event_location"
            ]:
                if field in validated_data:
                    setattr(
                        booking,
                        field,
                        validated_data[field]
                    )

            booking.guest_count = new_guest_count

            # Update or create the package booking item.
            if package_item:

                package_item.package_id = new_package.id
                package_item.quantity = new_guest_count
                package_item.unit_price = new_package.price_per_guest

            else:

                package_item = BookingItem(
                    booking_id=booking.id,
                    package_id=new_package.id,
                    addon_id=None,
                    quantity=new_guest_count,
                    unit_price=new_package.price_per_guest
                )

                db.session.add(package_item)

            # Recalculate the total, including any existing add-ons.
            db.session.flush()
            booking.estimated_total = get_booking_total(booking)

        db.session.commit()

        return jsonify({
            "message": "Booking updated successfully",
            "data": booking_schema.dump(booking)
        }), 200

    except ValidationError as error:
        db.session.rollback()

        return jsonify({
            "error": error.messages
        }), 400

    except IntegrityError:
        db.session.rollback()

        return jsonify({
            "error": "Unable to update booking"
        }), 409


# ============================================================
# DELETE BOOKING
# CUSTOMER ONLY - OWN BOOKING
# ============================================================

@booking_bp.route("/api/bookings/<int:booking_id>", methods=["DELETE"])
@jwt_required()
def delete_booking(booking_id):

    current_user_id = int(get_jwt_identity())
    current_role = get_jwt().get("role")

    if current_role != "customer":
        return jsonify({
            "error": "Only customers can delete bookings"
        }), 403

    booking = db.session.get(Booking, booking_id)

    if not booking:
        return jsonify({
            "error": "Booking not found"
        }), 404

    if booking.customer_id != current_user_id:
        return jsonify({
            "error": "You are not authorized to delete this booking"
        }), 403

    try:
        # Delete booking items first because their foreign key
        # references the booking.
        BookingItem.query.filter_by(
            booking_id=booking.id
        ).delete(synchronize_session=False)

        db.session.delete(booking)
        db.session.commit()

        return jsonify({
            "message": "Booking deleted successfully"
        }), 200

    except IntegrityError:
        db.session.rollback()

        return jsonify({
            "error": (
                "Cannot delete booking because related payments "
                "or reviews exist"
            )
        }), 409
