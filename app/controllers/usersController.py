from flask import Blueprint, request, jsonify
from app.services.usersService import register, login
from app.repositories.usersRepository import get_user_by_username

# Creating a blueprint for user routing purposes
usersController = Blueprint('usersController', __name__)

# Creates the route to register. Calls the register method from the services file.
@usersController.route('/register', methods=['POST'])
def register_user():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    result = register(username, password)
    
    return jsonify(result)

# Creates the route to login. Calls the register method from the services file.
@usersController.route('/login', methods=['POST'])
def login_user():
    print("hi")
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    result = login(username, password)
    
    return jsonify(result)

@usersController.route('/get_user_by_username', methods=['GET'])
def getUserByUsername():
    username = request.args.get('username')
    
    result = get_user_by_username(username)
    
    return jsonify(result.to_dict())
