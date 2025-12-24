from flask import abort
from app.repositories.usersRepository import get_user_by_username
from app.models.userModel import User
from flask_bcrypt import Bcrypt
from app import db
from app.validators.userValidator import validate_username, validate_password


# Initializing an object to hash passwords in the database
bcrypt = Bcrypt()


class UserService:
    """
    Service class for handling user-related business logic.

    This class manages user registration, authentication (both local and Google OAuth),
    and password hashing/verification using bcrypt.
    """

    @staticmethod
    def register(username, password):
        """
        Register a new user with local authentication.

        Validates the username and password, checks if the username already exists,
        and creates a new user with a hashed password if registration is successful.

        Args:
            username (str): The desired username for the new user.
            password (str): The plain-text password for the new user.

        Returns:
            dict: A success message if registration completes successfully.

        Raises:
            400: If username or password validation fails.
            409: If a user with the same username already exists.
        """
        # Validate inputs
        username = validate_username(username)
        password = validate_password(password)

        user = get_user_by_username(username=username)

        if (user is None):
            new_user = User(username=username,
                             password=bcrypt.generate_password_hash(password).decode('utf-8'),
                             auth_provider='local')

            db.session.add(new_user)
            db.session.commit()
            return {"message": "Successfully added user."}
        else:
            abort(409, "Username already exists. Register with a different username.")

    @staticmethod
    def login(username, password):
        """
        Authenticate a user with local credentials.

        Validates the username and password, retrieves the user from the database,
        and verifies the password hash matches the provided password.

        Args:
            username (str): The username of the user attempting to log in.
            password (str): The plain-text password provided by the user.

        Returns:
            dict: A success message and user data if authentication succeeds.

        Raises:
            400: If username or password validation fails.
            401: If the username doesn't exist or password doesn't match.
        """
        # Validate inputs
        username = validate_username(username)
        password = validate_password(password)

        user = get_user_by_username(username=username)

        # Note that order matters for bcrypt.check_password_hash (comparing hashed password to unhashed argument)
        if (user is not None and bcrypt.check_password_hash(user.password, password)):
            return {"message": "Login Successful", "user": user.to_dict()}
        else:
            abort(401, "Wrong username or password was entered")

    @staticmethod
    def handle_google_auth(email):
        """
        Handle Google OAuth authentication.

        Validates the email address and either retrieves an existing user with that email
        or creates a new user with Google as the authentication provider. Google-authenticated
        users do not have passwords stored in the database.

        Args:
            email (str): The email address from the Google OAuth response.

        Returns:
            User: The existing or newly created user object.

        Raises:
            400: If email validation fails.
            500: If there's a database error during user creation or retrieval.
        """
        # Validate email
        email = validate_username(email)

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
