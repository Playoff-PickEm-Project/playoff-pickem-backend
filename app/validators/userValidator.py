from flask import abort

def validate_username(username):
    """Validate username is not None or empty string."""
    if not username or (isinstance(username, str) and username.strip() == ""):
        abort(400, "Username is required and cannot be empty")
    return username.strip() if isinstance(username, str) else username

def validate_password(password):
    """Validate password is not None or empty string."""
    if not password or (isinstance(password, str) and password.strip() == ""):
        abort(400, "Password is required and cannot be empty")
    return password

def validate_user_exists(user, custom_message=None):
    """Validate that a user object is not None."""
    if user is None:
        message = custom_message or "User not found"
        abort(404, message)
    return user
