from flask import Blueprint, jsonify
from laptop import logger, docs
from laptop.schemas import LaptopSchema
from flask_apispec import use_kwargs, marshal_with
from laptop.models import Laptop
from flask_jwt_extended import jwt_required, get_jwt_identity

laptops = Blueprint('laptops', __name__)


@laptops.route('/laptops', methods=['GET'])
@jwt_required()
@marshal_with(LaptopSchema(many=True))
def get_laptops():
    try:
        user_id = get_jwt_identity()
        laptops = Laptop.query.filter(Laptop.user_id == user_id).all()
    except Exception as e:
        logger.warning(f'user:{user_id} video - read action failed with errors: {e}')
        return {'message': str(e)}, 400
    return laptops


@laptops.route('/laptops', methods=['POST'])
@jwt_required()
@use_kwargs(LaptopSchema)
@marshal_with(LaptopSchema)
def add_laptop(**kwargs):
    try:
        user_id = get_jwt_identity()
        new = Laptop(user_id=user_id, **kwargs)
        new.save()
    except Exception as e:
        logger.warning(f'user:{user_id} video - create action failed with errors: {e}')
        return {'message': str(e)}, 400
    return new


@laptops.route('/laptops/<int:laptop_id>', methods=['PUT'])
@jwt_required()
@use_kwargs(LaptopSchema)
@marshal_with(LaptopSchema)
def edit_laptop(laptop_id, **kwargs):
    try:
        user_id = get_jwt_identity()
        item = Laptop.get(laptop_id, user_id)
        item.update(**kwargs)
    except Exception as e:
        logger.warning(f'user:{user_id} video - edit action failed with errors: {e}')
        return {'message': str(e)}, 400
    return item


@laptops.route('/laptops/<int:laptop_id>', methods=['DELETE'])
@jwt_required()
@marshal_with(LaptopSchema)
def delete_laptop(laptop_id):
    try:
        user_id = get_jwt_identity()
        item = Laptop.get(laptop_id, user_id)
        item.delete()
    except Exception as e:
        logger.warning(f'user:{user_id} video - delete action failed with errors: {e}')
        return {'message': str(e)}, 400
    return '', 204


@laptops.errorhandler(422)
def handle_error(err):
    headers = err.data.get('headers', None)
    messages = err.data.get('messages', ['Invalid Request.'])
    logger.warning(f'Invalid input params: {messages}')
    if headers:
        return jsonify({'message': messages}), 400, headers
    else:
        return jsonify({'message': messages}), 400


docs.register(get_laptops, blueprint='laptops')
docs.register(add_laptop, blueprint='laptops')
docs.register(edit_laptop, blueprint='laptops')
docs.register(delete_laptop, blueprint='laptops')
