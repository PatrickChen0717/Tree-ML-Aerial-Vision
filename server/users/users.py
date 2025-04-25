from flask import request, jsonify, make_response
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
import datetime
from database import UserDatabase

db = UserDatabase()

def create_account(username, password):
    if db.is_new_user(username):
        success = db.add_new_user(username, password)
        return {"message": "User Created" if success else "Failed to Create User", "allow_create": success}
    return {"message": "This Username Already Exists", "allow_create": False}

def login(username, password):
    if db.is_new_user(username):
        return {"message": "User Not Found", "allow_login": False}

    if not db.check_password(username, password):
        return {"message": "Incorrect Password", "allow_login": False}
    
    access_token = create_access_token(identity=username, expires_delta=datetime.timedelta(days=365))

    return {"message": "Login Successful", "allow_login": True, "token": access_token}

def logout():
    response = make_response(jsonify({"message": "Logged Out"}))
    response.set_cookie("korotuTL88_cookie", "", expires=0)
    return response
