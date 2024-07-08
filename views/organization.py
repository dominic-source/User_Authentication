import uuid
from middlewares.user_validation import protected_route
from views import app_views
from flask import request, jsonify, session
from models import User, Organization
from app import db


@app_views.route("/api/organisations/:orgId/users", methods=["POST"])
@protected_route
def add_existing_user_to_organization(orgId=None):
    """This is the add existing user to organization function"""
    try:
        orgOwner = session.get('user_id')
        orgUser = User.query.filter_by(userId=orgOwner).first()
        if orgUser is None:
            return jsonify({
                "status": "Bad request",
                "message": "User not found",
                "statusCode": 404
            }), 404
        request_data = request.get_json()
        userId = request_data.get('userId')
        user = User.query.filter_by(userId=userId).first()
        if user is None:
            return jsonify({
                "status": "Bad request",
                "message": "The User was not found",
                "statusCode": 404
            }), 404
        org_check = Organization.query.filter_by(orgId=orgId).first()
        if org_check is None:
            return jsonify({
                "status": "Bad request",
                "message": "Organization not found",
                "statusCode": 404
            }), 404
        organization = [org for org in orgUser.organizations if org.orgId == orgId]
        if not organization:
            return jsonify({
                "status": "Bad request",
                "message": "You are not in this organization",
                "statusCode": 400
            }), 400
        
        user.organizations.append(org_check)
        db.session.commit()
        return jsonify({
            "status": "success",
            "message": "User added to organization successfully"
        }), 200
    except Exception as e:
        print(e)
        return jsonify({
            "status": "Bad request",
            "message": "Server error",
            "statusCode": 400
        }), 400


@app_views.route("/api/organisations", methods=["POST"])
@protected_route
def create_organization():
    """This is the create organization function"""
    user_id = session.get('user_id')
    user = User.query.filter_by(userId=user_id).first()
    if user is None:
        return jsonify({
            "status": "Bad request",
            "message": "User not found",
            "statusCode": 404
        }), 404
    request_data = request.get_json()
    name = request_data.get('name')
    description = request_data.get('description')

    try:
        organization = [orgName for orgName in user.organizations if orgName.name == name]
        if organization:
            return jsonify({
                "status": "Bad Request",
                "message": "Client error",
                "statusCode": 400
        }), 400

        organization = Organization(orgId=str(uuid.uuid4()), name=name, description=description)
        user.organizations.append(organization)
        db.session.add(organization)
        db.session.commit()
        return jsonify({
            "status": "success",
            "message": "Organisation created successfully",
            "data": {
                "orgId": organization.orgId,
                "name": organization.name,
                "description": organization.description
            }
        }), 201
    except Exception as e:
        return jsonify({
            "status": "Bad Request",
            "message": "Client error",
            "statusCode": 400
        }), 400


@app_views.route("/api/organisations/:orgId", methods=["GET"])
@protected_route
def organization(orgId=None):
    """This is the organization function"""
    user_id = session.get('user_id')
    user = User.query.filter_by(userId=user_id).first()
    if user is None:
        return jsonify({
            "status": "Bad request",
            "message": "User not found",
            "statusCode": 404
        }), 404
    organization = user.organizations.filter_by(orgId=orgId).first()
    if organization is None:
        return jsonify({
            "status": "Bad request",
            "message": "Organization not found",
            "statusCode": 404
        }), 404
    return jsonify({
        "status": "success",
        "message": "Organization found",
        "data": {
            "orgId": organization.orgId,
            "name": organization.name,
            "description": organization.description
        }
    }), 200


@app_views.route("/api/organisations", methods=["GET"])
@protected_route
def organizations():
    """This is the organizations function"""
    user_id = session.get('user_id')
    user = User.query.filter_by(userId=user_id).first()
    if user is None:
        return jsonify({
            "status": "Bad request",
            "message": "User not found",
            "statusCode": 404
        }), 404
    organizations = user.organizations
    return jsonify({
        "status": "success",
        "message": "Organizations found",
        "data": [
            {
                "orgId": organization.orgId,
                "name": organization.name,
                "description": organization.description
            } for organization in organizations
        ]
    }), 200
