from app.repositories.usersRepository import get_user_by_username
from app.models.userModel import Users
from flask_bcrypt import Bcrypt
from app import db

# Initializing an object to hash passwords in the database
bcrypt = Bcrypt()

# Method to register a user. Checks if a user with the same name exists; if not, registration should complete successfully
def register(username, password):
    user = get_user_by_username(username=username)
    
    if (user is None):
        new_user = Users(username=username,
                         password=bcrypt.generate_password_hash(password))
        
        db.session.add(new_user)
        db.session.commit()
        return {"message": "Successfully added user."}
    else:
        return {"error": f"Username {username} already exists."}

# Method to login. If credentials match, method should return something (TO BE DECIDED)
def login(username, password):
    user = get_user_by_username(username=username)
    
    # Note that order matters for bcrypt.check_password_hash (comparing hashed password to unhashed argument)
    if (user is not None and bcrypt.check_password_hash(user.password, password)):
        return {"message": "Login Successful"}
    else:
        return {"error": "Login Unsuccessful. Username or Password is incorrect."}