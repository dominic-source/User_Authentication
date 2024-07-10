import uuid
from middlewares.user_validation import protected_route, validate_user
from views import app_views
from flask import request, jsonify, session
from models import User, Organization
from database import db
import jwt
import bcrypt
from datetime import datetime, timedelta
import os

@app_views.route("/", methods=["GET"])
def helloworld():
    return "Hello, World!"


@app_views.route("/api/users/<id>", methods=["GET"])
@protected_route
def user(id=None):
    """This is the user function"""
    user_id = session.get('user_id')
    if id is not None and id != user_id:
        return jsonify({
            "status": "Bad request",
            "message": "Unauthorized",
            "statusCode": 401
        }), 401
    user = User.query.filter_by(userId=user_id).first()
    
    if user is None:
        return jsonify({
            "status": "Bad request",
            "message": "User not found",
            "statusCode": 404
        }), 404
    return jsonify({
        "status": "success",
        "message": "User found",
        "data": {
            "userId": user.userId,
            "firstName": user.firstName,
            "lastName": user.lastName,
            "email": user.email,
            "phone": user.phone
        }
    }), 200


@app_views.route("/auth/login", methods=["POST"])
def login():
    """This is the login function"""
    request_data = request.get_json()
    email = request_data.get('email')
    password = request_data.get('password')
    user = User.query.filter_by(email=email).first()
    if user is None:
        return jsonify({
            "status": "Bad request",
            "message": "Authentication failed",
            "statusCode": 401
        }), 401
    if bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
        expiration_time = datetime.now() + timedelta(hours=24)
        payload = { "userId": user.userId, "exp": expiration_time }
        accessToken = jwt.encode(payload, os.environ.get('SECRET_KEY'), algorithm='HS256')
        return jsonify({
            "status": "success",
            "message": "Login successful",
            "data": {
                "accessToken": accessToken,
                "user": {
                    "userId": user.userId,
                    "firstName": user.firstName,
                    "lastName": user.lastName,
                    "email": user.email,
                    "phone": user.phone
                }
            }
        }), 200
    else:
        return jsonify({
            "status": "Bad request",
            "message": "Authentication failed",
            "statusCode": 401
        }), 401


@app_views.route("/auth/register", methods=["POST"])
# @validate_user
def register():
    """This is the register function"""
    register_data = request.get_json()
    password = register_data.get('password')
    firstName = register_data.get('firstName')
    lastName = register_data.get('lastName')
    email = register_data.get('email')
    phone = register_data.get('phone')
    # generate userId
    userId = str(uuid.uuid4())
    
    # hash password
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # jwt token
    expiration_time = datetime.now() + timedelta(hours=24)
    payload = { "userId": userId, "exp": expiration_time }
    accessToken = jwt.encode(payload, os.environ.get('SECRET_KEY'), algorithm='HS256')
    try:
        user = User(userId=userId, firstName=firstName, lastName=lastName, email=email, password=hashed_password, phone=phone)
        orgId = str(uuid.uuid4())
        organization = Organization(name=f"{firstName}'s Organisation", orgId=orgId)
        organization.users.append(user)
        db.session.add(user)
        db.session.add(organization)
        db.session.commit()
        return jsonify({
            "status": "success",
            "message": "Registration successful",
            "data": {
                "accessToken": accessToken,
                "user": {
                    "userId": userId,
                    "firstName": firstName,
                    "lastName": lastName,
                    "email": email,
                    "phone": phone,
                }
            }
        }), 201
    except Exception as e:
        print(e)
        return jsonify({
            "status": "Bad request",
            "message": "Registration unsuccessful",
            "statusCode": 400
        }), 400
