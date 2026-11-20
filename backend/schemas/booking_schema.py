from marshmallow import Schema, fields, validate


class BookingSchema(Schema):

    id = fields.Integer(dump_only=True)

    customer_id = fields.Integer(dump_only=True)

    caterer_id = fields.Integer(
        required=True,
        validate=validate.Range(min=1)
    )

    # Used as input to select a package.
    # The package selection will be stored in booking_items.
    package_id = fields.Integer(
        required=True,
        load_only=True,
        validate=validate.Range(min=1)
    )

    event_type = fields.String(
        required=True,
        validate=validate.Length(min=2, max=100)
    )

    event_date = fields.Date(required=True)

    event_location = fields.String(
        required=True,
        validate=validate.Length(min=2, max=200)
    )

    guest_count = fields.Integer(
        required=True,
        validate=validate.Range(min=1)
    )

    estimated_total = fields.Decimal(
        dump_only=True,
        as_string=True
    )

    status = fields.String(dump_only=True)

    created_at = fields.DateTime(dump_only=True)
