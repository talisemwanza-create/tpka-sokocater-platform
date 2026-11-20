
from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
    get_jwt
)
from sqlalchemy.exc import IntegrityError
from marshmallow import ValidationError

from extensions import db
from models import Menu, Caterer
from schemas.menu_schema import MenuSchema


menu_bp = Blueprint("menus", __name__)

menu_schema = MenuSchema()
menus_schema = MenuSchema(many=True)


# ==================================================
# HELPER FUNCTION
# ==================================================

def get_current_caterer():
    """
    Get the caterer profile belonging to the logged-in user.

    Only users with the caterer role can access
    protected menu operations.
    """

    claims = get_jwt()

    if claims.get("role") != "caterer":
        return None

    try:
        user_id = int(get_jwt_identity())
    except (TypeError, ValueError):
        return None

    return Caterer.query.filter_by(
        user_id=user_id
    ).first()


# ==================================================
# GET ALL MENUS - PUBLIC
# ==================================================

@menu_bp.route("/api/menus", methods=["GET"])
def get_menus():

    menus = Menu.query.all()

    return jsonify({
        "message": "Menus retrieved successfully",
        "data": menus_schema.dump(menus)
    }), 200


# ==================================================
# GET SINGLE MENU - PUBLIC
# ==================================================

@menu_bp.route("/api/menus/<int:menu_id>", methods=["GET"])
def get_menu(menu_id):

    menu = db.session.get(Menu, menu_id)

    if not menu:
        return jsonify({
            "error": "Menu not found"
        }), 404

    return jsonify({
        "data": menu_schema.dump(menu)
    }), 200


# ==================================================
# CREATE MENU - CATERER ONLY
# ==================================================

@menu_bp.route("/api/menus", methods=["POST"])
@jwt_required()
def create_menu():

    current_caterer = get_current_caterer()

    if not current_caterer:
        return jsonify({
            "error": "Only registered caterers can create menus"
        }), 403

    # silent=True prevents Flask from returning 415
    # when the request does not contain JSON.
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Invalid JSON body"
        }), 400

    try:
        validated_data = menu_schema.load(data)

        # A caterer can only create menus for their own profile.
        if validated_data["caterer_id"] != current_caterer.id:
            return jsonify({
                "error": "You can only create menus for your own profile"
            }), 403

        menu = Menu(**validated_data)

        db.session.add(menu)
        db.session.commit()

        return jsonify({
            "message": "Menu created successfully",
            "data": menu_schema.dump(menu)
        }), 201

    except ValidationError as error:
        return jsonify({
            "error": error.messages
        }), 400

    except IntegrityError:
        db.session.rollback()

        return jsonify({
            "error": "Unable to create menu"
        }), 409


# ==================================================
# UPDATE MENU - OWNER ONLY
# ==================================================

@menu_bp.route("/api/menus/<int:menu_id>", methods=["PUT"])
@jwt_required()
def update_menu(menu_id):

    current_caterer = get_current_caterer()

    if not current_caterer:
        return jsonify({
            "error": "Only registered caterers can update menus"
        }), 403

    menu = db.session.get(Menu, menu_id)

    if not menu:
        return jsonify({
            "error": "Menu not found"
        }), 404

    # Verify menu ownership.
    if menu.caterer_id != current_caterer.id:
        return jsonify({
            "error": "You can only update your own menus"
        }), 403

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Invalid JSON body"
        }), 400

    try:
        validated_data = menu_schema.load(
            data,
            partial=True
        )

        # Prevent transferring ownership to another caterer.
        if (
            "caterer_id" in validated_data
            and validated_data["caterer_id"] != current_caterer.id
        ):
            return jsonify({
                "error": "You cannot transfer a menu to another caterer"
            }), 403

        for field, value in validated_data.items():
            setattr(menu, field, value)

        db.session.commit()

        return jsonify({
            "message": "Menu updated successfully",
            "data": menu_schema.dump(menu)
        }), 200

    except ValidationError as error:
        return jsonify({
            "error": error.messages
        }), 400

    except IntegrityError:
        db.session.rollback()

        return jsonify({
            "error": "Unable to update menu"
        }), 409


# ==================================================
# DELETE MENU - OWNER ONLY
# ==================================================

@menu_bp.route("/api/menus/<int:menu_id>", methods=["DELETE"])
@jwt_required()
def delete_menu(menu_id):

    current_caterer = get_current_caterer()

    if not current_caterer:
        return jsonify({
            "error": "Only registered caterers can delete menus"
        }), 403

    menu = db.session.get(Menu, menu_id)

    if not menu:
        return jsonify({
            "error": "Menu not found"
        }), 404

    # Verify menu ownership.
    if menu.caterer_id != current_caterer.id:
        return jsonify({
            "error": "You can only delete your own menus"
        }), 403

    try:
        db.session.delete(menu)
        db.session.commit()

        return jsonify({
            "message": "Menu deleted successfully"
        }), 200

    except IntegrityError:
        db.session.rollback()

        return jsonify({
            "error": "Cannot delete menu because related records exist"
        }), 409
