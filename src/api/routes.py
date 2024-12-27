"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
from flask import Flask, request, jsonify, url_for, Blueprint
from api.models import db, User
from api.utils import generate_sitemap, APIException
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import os
from base64 import b64encode

api = Blueprint('api', __name__)

# Allow CORS requests to this API
CORS(api)


@api.route("/register", methods=["POST"])
def add_user():
    body = request.json

    name = body.get("name", None)
    email = body.get("email", None)
    password = body.get("password", None)
    avatar = body.get("avatar", None)

    if email is None or password is None or name is None:
        return jsonify({"message":"Los campos name, email y password son requeridos"}), 400
    
    else:
        user = User()
        user_exist = User.query.filter_by(email=email).one_or_none()
        
        if user_exist is not None:
            return jsonify({"message": "El usuario ya esta registrado"}), 400
        
        salt = b64encode(os.urandom(32)).decode("utf-8")
        password = generate_password_hash(f"{password}{salt}") # 123456789sṕjṕogjpsdiopojdpofjpdojpsojpfojspodjfpsjodfpj

        user.name = name
        user.email = email
        user.password = password
        user.salt = salt
        db.session.add(user) # preparandonos para la transacción

        try:
            db.session.commit()
            return jsonify({"message":"Usuario registrado exitosamente"}), 201
        except Exception as err:
            db.session.rollback()
            return jsonify({"message":f"Error:{err.args}"}), 500


@api.route("/login", methods=["POST"])
def login():
    body = request.get_json()
    email = body.get("email", None)
    password = body.get("password", None)

    required_fields = {"email", "password"}
    missing_field = {field for field in required_fields if not body.get(field)}

    if missing_field:
        return jsonify({"message": f"Estos campos son requeridos {', '.join(missing_field)}"}), 400

    else:
        user = User.query.filter_by(email=email).one_or_none()
        if user is None:
            return jsonify({"message": "Malas credenciales"}), 400
        else:
            if check_password_hash(user.password, f"{password}{user.salt}"):
                token = "hashahahah" # genetrar token
                return jsonify({"token":token}), 200
            else:
                return jsonify({"message": "Malas credenciales"}), 400
