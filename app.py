from flask import Flask, jsonify, request
import sqlalchemy as db
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from config import Config
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec import APISpec
from flask_apispec.extension import FlaskApiSpec
from schemas import LaptopSchema, UserSchema, AuthSchema
from flask_apispec import use_kwargs, marshal_with

app = Flask(__name__)
app.config.from_object(Config)

client = app.test_client()

engine = create_engine('sqlite:///db.sqlite')

session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

Base = declarative_base()
Base.query = session.query_property()

jwt = JWTManager(app)

docs = FlaskApiSpec()

docs.init_app(app)

app.config.update({
    'APISPEC_SPEC': APISpec(
        title='laptops',
        version='v1',
        openapi_version='2.0',
        plugins=[MarshmallowPlugin()],
    ),
    'APISPEC_SWAGGER_URL': '/swagger/'
})

from models import *

Base.metadata.create_all(bind=engine)


@app.route('/laptops', methods=['GET'])
@jwt_required()
@marshal_with(LaptopSchema(many=True))
def get_laptops():
    user_id = get_jwt_identity()
    laptops = Laptop.query.filter(Laptop.user_id == user_id).all()
    return laptops


@app.route('/laptops', methods=['POST'])
@jwt_required()
@use_kwargs(LaptopSchema)
@marshal_with(LaptopSchema)
def add_laptop(**kwargs):
    user_id = get_jwt_identity()
    new = Laptop(user_id=user_id, **kwargs)
    session.add(new)
    session.commit()
    return new


@app.route('/laptops/<int:laptop_id>', methods=['PUT'])
@jwt_required()
@use_kwargs(LaptopSchema)
@marshal_with(LaptopSchema)
def edit_laptop(laptop_id, **kwargs):
    user_id = get_jwt_identity()
    item = Laptop.query.filter(Laptop.id == laptop_id, Laptop.user_id == user_id).first()
    if not item:
        return {'message': 'No laptops with this id'}, 400
    for key, value in kwargs.items():
        setattr(item, key, value)
    session.commit()
    return item


@app.route('/laptops/<int:laptop_id>', methods=['DELETE'])
@jwt_required()
@marshal_with(LaptopSchema)
def delete_laptop(laptop_id):
    user_id = get_jwt_identity()
    item = Laptop.query.filter(Laptop.id == laptop_id, Laptop.user_id == user_id).first()
    if not item:
        return {'message': 'No laptops with this id'}, 400
    session.delete(item)
    session.commit()
    return '', 204


@app.route('/register', methods=['POST'])
@use_kwargs(UserSchema)
@marshal_with(AuthSchema)
def register(**kwargs):
    user = User(**kwargs)
    session.add(user)
    session.commit()
    token = user.get_token()
    return {'access_token': token}


@app.route('/login', methods=['POST'])
@use_kwargs(UserSchema(only=('email', 'password')))
@marshal_with(AuthSchema)
def login(**kwargs):
    user = User.authenticate(**kwargs)
    token = user.get_token()
    return {'access_token': token}


@app.teardown_appcontext
def shutdown_session(exception=None):
    session.remove()


docs.register(get_laptops)
docs.register(add_laptop)
docs.register(edit_laptop)
docs.register(delete_laptop)
docs.register(register)
docs.register(login)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port='5000')

