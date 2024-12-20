from flask import Blueprint, request, jsonify
from app.services.usersService import register, login

# Creating a blueprint for user routing purposes
usersController = Blueprint('usersController', __name__)

@usersController.route('/register', methods=['POST'])
def register_user():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    result = register(username, password)
    
    return jsonify(result)

@usersController.route('/login', methods=['POST'])
def login_user():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    result = login(username, password)
    
    return jsonify(result)