
from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token
from marshmallow import ValidationError
from werkzeug.security import generate_password_hash, check_password_hash

from extensions import db
from models import User
from schemas.auth_schema import RegisterSchema, LoginSchema


auth_bp = Blueprint("auth", __name__)

register_schema = RegisterSchema()
login_schema = LoginSchema()


@auth_bp.route("/api/auth/register", methods=["POST"])
def register():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Invalid JSON body"}), 400

    try:
        validated_data = register_schema.load(data)

        email = validated_data["email"].lower()

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            return jsonify({"error": "Email already registered"}), 409

        user = User(
            full_name=validated_data["full_name"],
            email=email,
            password_hash=generate_password_hash(validated_data["password"]),
            phone_number=validated_data.get("phone_number"),
            role=validated_data["role"]
        )

        db.session.add(user)
        db.session.commit()

        return jsonify({
            "message": "User registered successfully",
            "user": {
                "id": user.id,
                "full_name": user.full_name,
                "email": user.email,
                "phone_number": user.phone_number,
                "role": user.role
            }
        }), 201

    except ValidationError as error:
        return jsonify({"error": error.messages}), 400


@auth_bp.route("/api/auth/login", methods=["POST"])
def login():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Invalid JSON body"}), 400

    try:
        validated_data = login_schema.load(data)

        email = validated_data["email"].lower()
        password = validated_data["password"]

        user = User.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password_hash, password):
            return jsonify({"error": "Invalid email or password"}), 401

        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={"role": user.role}
        )

        return jsonify({
            "message": "Login successful",
            "access_token": access_token,
            "user": {
                "id": user.id,
                "full_name": user.full_name,
                "email": user.email,
                "phone_number": user.phone_number,
                "role": user.role
            }
        }), 200

    except ValidationError as error:
        return jsonify({"error": error.messages}), 400
