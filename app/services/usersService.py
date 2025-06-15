from flask import abort
from app.repositories.usersRepository import get_user_by_username
from app.models.userModel import User
from flask_bcrypt import Bcrypt
from app import db


# Initializing an object to hash passwords in the database
bcrypt = Bcrypt()

# Method to register a user. Checks if a user with the same name exists; if not, registration should complete successfully
def register(username, password):
    user = get_user_by_username(username=username)
    
    if (user is None):
        new_user = User(username=username,
                         password=bcrypt.generate_password_hash(password).decode('utf-8'),
                         auth_provider='local')
        
        db.session.add(new_user)
        db.session.commit()
        return {"message": "Successfully added user."}
    else:
        abort(401, "Username already exists. Register with a different username.")

# Method to login. If credentials match, method should return something (TO BE DECIDED)
def login(username, password):
    user = get_user_by_username(username=username)
        
    # Note that order matters for bcrypt.check_password_hash (comparing hashed password to unhashed argument)
    if (user is not None and bcrypt.check_password_hash(user.password, password)):
        return {"message": "Login Successful", "user": user.to_dict()}
    else:
        abort(401, "Wrong username or password was entered")

# Method to handle Google authentication
def handle_google_auth(email):
    try:
        user = get_user_by_username(username=email)
        
        if (user is None):
            new_user = User(username=email,
                           auth_provider='google')  # No password for Google users
            db.session.add(new_user)
            db.session.commit()
            return new_user
        return user
    except Exception as e:
        db.session.rollback()
        abort(500, f"Error during Google authentication: {str(e)}")