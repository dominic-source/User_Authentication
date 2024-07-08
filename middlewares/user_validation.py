from functools import wraps
from flask import jsonify, request, session
import jwt
import os
from models import User, Organization
from app import db

def protected_route(func: callable) -> callable:
    """This will protect every route that this decorator is applied to."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        authorization = request.headers.get('Authorization')
        if authorization is None:
            return jsonify(
                {
                    "errors": [
                        {
                            "message": "Authorization header is required"
                        }
                    ]
                }
            ), 401
        if not authorization.startswith('Bearer '):
            return jsonify(
                {
                    "errors": [
                        {
                            "message": "Invalid authorization header"
                        }
                    ]
                }
            ), 401
        token = authorization.split(' ')[1]
        if token == "":
            return jsonify(
                {
                    "errors": [
                        {
                            "message": "Token is required"
                        }
                    ]
                }
            ), 401
        try:
            payload = jwt.decode(token, os.environ.get('SECRET_KEY'), algorithms=['HS256'])
            session['user_id'] = payload['userId']
        except jwt.ExpiredSignatureError:
            return jsonify(
                {
                    "errors": [
                        {
                            "message": "Invalid token"
                        }
                    ]
                }
            ), 401
        except jwt.InvalidTokenError:
            return jsonify(
                {
                    "errors": [
                        {
                            "message": "Invalid token"
                        }
                    ]
                }
            ), 401
        return func(*args, **kwargs)
    return wrapper


def validate_user(func: callable) -> callable:
    """
    This is a decorator function that validates the userId in the request.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        register_args = request.get_json()
        errors = { "errors": [] }
        obj = {
            "firstName": register_args.get('firstName'),
            "lastName": register_args.get('lastName'),
            "email": register_args.get('email'),
            "password": register_args.get('password'),
        }
        user = User.query.filter_by(email=obj['email']).first()
        if user is not None:
            errors["errors"].append(
                {
                    "field": "email",
                    "message": "Email already exists"
                }
            )
        phone = register_args.get('phone')
        for key, value in obj.items():
            if value is None or value == "" or not isinstance(value, str):
                errors["errors"].append(
                    {
                        "field": key,
                        "message": "This field is required and must be a string"
                    }
                )
 
        if phone is not None and not isinstance(phone, str):
            errors["errors"].append(
                {
                    "field": "phone",
                    "message": "This field must be a string"
                }
            )
        if errors["errors"]:
            return jsonify(errors), 422
        return func(*args, **kwargs)
    return wrapper
