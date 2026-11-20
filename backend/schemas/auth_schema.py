
from marshmallow import Schema, fields, validate


class RegisterSchema(Schema):
    full_name = fields.String(
        required=True,
        validate=validate.Length(min=2, max=100)
    )

    email = fields.Email(required=True)

    password = fields.String(
        required=True,
        load_only=True,
        validate=validate.Length(min=8)
    )

    phone_number = fields.String(
        required=False,
        allow_none=True
    )

    role = fields.String(
        required=True,
        validate=validate.OneOf(["customer", "caterer"])
    )


class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True, load_only=True)
