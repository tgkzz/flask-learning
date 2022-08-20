from marshmallow import Schema, validate, fields


class LaptopSchema(Schema):
    id = fields.Integer(dump_only=True)
    user_id = fields.Integer(dump_only=True)
    name = fields.String(required=True, validate=[validate.Length(max=250)])
    description = fields.String(required=True, validate=[validate.Length(max=500)])
    message = fields.String(dump_only=True)


class UserSchema(Schema):
    name = fields.String(required=True, validate=[validate.Length(max=250)])
    email = fields.String(required=True, validate=[validate.Length(max=250)])
    password = fields.String(required=True, validate=[validate.Length(max=100)], load_only=True)
    laptops = fields.Nested(LaptopSchema, many=True, dump_only=True)


class AuthSchema(Schema):
    access_token = fields.String(dump_only=True)
    message = fields.String(dump_only=True)

