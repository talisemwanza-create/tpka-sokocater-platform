
from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
    get_jwt
)
from sqlalchemy.exc import IntegrityError
from marshmallow import ValidationError

from extensions import db
from models import Package, Caterer
from schemas.package_schema import PackageSchema


package_bp = Blueprint("packages", __name__)

package_schema = PackageSchema()
packages_schema = PackageSchema(many=True)


# ==================================================
# HELPER FUNCTION
# ==================================================

def get_current_caterer():
    """
    Get the caterer profile belonging to the logged-in user.
    Only users with the caterer role can manage packages.
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
# GET ALL PACKAGES - PUBLIC
# ==================================================

@package_bp.route("/api/packages", methods=["GET"])
def get_packages():

    packages = Package.query.all()

    return jsonify({
        "message": "Packages retrieved successfully",
        "data": packages_schema.dump(packages)
    }), 200


# ==================================================
# GET SINGLE PACKAGE - PUBLIC
# ==================================================

@package_bp.route("/api/packages/<int:package_id>", methods=["GET"])
def get_package(package_id):

    package = db.session.get(Package, package_id)

    if not package:
        return jsonify({
            "error": "Package not found"
        }), 404

    return jsonify({
        "data": package_schema.dump(package)
    }), 200


# ==================================================
# CREATE PACKAGE - CATERER ONLY
# ==================================================

@package_bp.route("/api/packages", methods=["POST"])
@jwt_required()
def create_package():

    current_caterer = get_current_caterer()

    if not current_caterer:
        return jsonify({
            "error": "Only registered caterers can create packages"
        }), 403

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Invalid JSON body"
        }), 400

    try:
        validated_data = package_schema.load(data)

        # Caterers can only create packages for their own profiles.
        if validated_data["caterer_id"] != current_caterer.id:
            return jsonify({
                "error": "You can only create packages for your own profile"
            }), 403

        package = Package(**validated_data)

        db.session.add(package)
        db.session.commit()

        return jsonify({
            "message": "Package created successfully",
            "data": package_schema.dump(package)
        }), 201

    except ValidationError as error:
        return jsonify({
            "error": error.messages
        }), 400

    except IntegrityError:
        db.session.rollback()

        return jsonify({
            "error": "Unable to create package"
        }), 409


# ==================================================
# UPDATE PACKAGE - OWNER ONLY
# ==================================================

@package_bp.route("/api/packages/<int:package_id>", methods=["PUT"])
@jwt_required()
def update_package(package_id):

    current_caterer = get_current_caterer()

    if not current_caterer:
        return jsonify({
            "error": "Only registered caterers can update packages"
        }), 403

    package = db.session.get(Package, package_id)

    if not package:
        return jsonify({
            "error": "Package not found"
        }), 404

    # Verify that the package belongs to the logged-in caterer.
    if package.caterer_id != current_caterer.id:
        return jsonify({
            "error": "You can only update your own packages"
        }), 403

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Invalid JSON body"
        }), 400

    try:
        validated_data = package_schema.load(
            data,
            partial=True
        )

        # Prevent transferring a package to another caterer.
        if (
            "caterer_id" in validated_data
            and validated_data["caterer_id"] != current_caterer.id
        ):
            return jsonify({
                "error": "You cannot transfer a package to another caterer"
            }), 403

        for field, value in validated_data.items():
            setattr(package, field, value)

        db.session.commit()

        return jsonify({
            "message": "Package updated successfully",
            "data": package_schema.dump(package)
        }), 200

    except ValidationError as error:
        return jsonify({
            "error": error.messages
        }), 400

    except IntegrityError:
        db.session.rollback()

        return jsonify({
            "error": "Unable to update package"
        }), 409


# ==================================================
# DELETE PACKAGE - OWNER ONLY
# ==================================================

@package_bp.route("/api/packages/<int:package_id>", methods=["DELETE"])
@jwt_required()
def delete_package(package_id):

    current_caterer = get_current_caterer()

    if not current_caterer:
        return jsonify({
            "error": "Only registered caterers can delete packages"
        }), 403

    package = db.session.get(Package, package_id)

    if not package:
        return jsonify({
            "error": "Package not found"
        }), 404

    # Verify package ownership.
    if package.caterer_id != current_caterer.id:
        return jsonify({
            "error": "You can only delete your own packages"
        }), 403

    try:
        db.session.delete(package)
        db.session.commit()

        return jsonify({
            "message": "Package deleted successfully"
        }), 200

    except IntegrityError:
        db.session.rollback()

        return jsonify({
            "error": "Cannot delete package because related records exist"
        }), 409
