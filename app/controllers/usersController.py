from flask import Blueprint, request, jsonify, url_for, session, redirect, current_app
from app.services.usersService import UserService
from app.repositories.usersRepository import get_user_by_username
from app.models.userModel import User
from app import db
from flask_bcrypt import Bcrypt
import logging
import traceback
import os

bcrypt = Bcrypt()

"""
User Controller

Handles all user-related HTTP endpoints including registration, login,
session management, and Google OAuth authentication.
"""

usersController = Blueprint('usersController', __name__)

@usersController.route('/register', methods=['POST'])
def register_user():
    """
    Register a new user with local authentication.

    Expects JSON body with:
        - username (str): The desired username
        - password (str): The plain-text password

    Returns:
        JSON: Success message if registration completes
    """
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    result = UserService.register(username, password)

    return jsonify(result)

@usersController.route('/login', methods=['POST'])
def login_user():
    """
    Authenticate a user with local credentials.

    Expects JSON body with:
        - username (str): The username
        - password (str): The plain-text password

    Returns:
        JSON: Success message and user data if authentication succeeds
    """
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    result = UserService.login(username, password)

    return jsonify(result)

@usersController.route('/get_user_by_username', methods=['GET'])
def getUserByUsername():
    """
    Retrieve a user by their username.

    Query Parameters:
        - username (str): The username to look up

    Returns:
        JSON: User object as dictionary
    """
    username = request.args.get('username')

    result = get_user_by_username(username)

    return jsonify(result.to_dict())

@usersController.route('/session-info', methods=['GET'])
def session_info():
    """
    Check the current session status and retrieve session information.

    Returns:
        JSON: Username and auth provider if logged in, or error if not logged in
    """
    logging.info(f"Session info check - Session contents: {dict(session)}")
    if 'username' in session:
        logging.info(f"User {session['username']} is logged in")
        return jsonify({
            'username': session['username'],
            'auth_provider': session.get('auth_provider', 'local')
        })
    logging.info("No user found in session")
    return jsonify({'error': 'Not logged in'}), 401

@usersController.route('/logout', methods=['POST'])
def logout():
    """
    Log out the current user by clearing their session.

    Returns:
        JSON: Success message
    """
    username = session.get('username', 'Unknown')
    session.clear()
    logging.info(f"User {username} logged out successfully")
    return jsonify({'message': 'Logged out successfully'}), 200

@usersController.route('/login/google', methods=['GET'])
def login_google():
    """
    Initiate Google OAuth authentication flow.

    Redirects the user to Google's login page for OAuth authentication.

    Returns:
        Redirect: Redirect to Google's OAuth authorization page
    """
    try:
        # Generate the redirect URI for Google OAuth callback
        # _external=True ensures we get a full URL including the domain
        redirect_uri = url_for('usersController.authorize_google', _external=True)
        logging.info(f"Starting Google login - Redirect URI: {redirect_uri}")
        # Redirect to Google's OAuth page
        return current_app.google.authorize_redirect(redirect_uri)
    except Exception as e:
        logging.error(f"Error during Google login: {str(e)}")
        logging.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({"error": f"An error occurred during Google login: {str(e)}"}), 500
    
@usersController.route('/authorize/google')
def authorize_google():
    """
    Handle Google OAuth callback after user authentication.

    Exchanges the authorization code for an access token, retrieves user info
    from Google, creates or retrieves the user in the database, stores session
    information, and returns HTML that communicates with the popup opener window.

    Returns:
        HTML: JavaScript that sends user data to opener window and closes popup
    """
    try:
        # Exchange the authorization code for an access token
        token = current_app.google.authorize_access_token()

        # Fetch user information from Google's userinfo endpoint
        resp = current_app.google.get('https://www.googleapis.com/oauth2/v3/userinfo')
        user_info = resp.json()
        email = user_info['email']

        # Create or update user in our database
        user = UserService.handle_google_auth(email)

        # Store user information in session
        session['username'] = email
        session['auth_provider'] = 'google'

        # Return HTML that sends the response back to the opener window
        # This is used when the login is initiated from a popup window
        return f"""
        <html>
            <body>
                <script>
                    // Send the user data back to the main window
                    window.opener.postMessage({{
                        success: true,
                        username: '{email}',
                        auth_provider: 'google'
                    }}, '{os.getenv('FRONTEND_URL', 'http://localhost:3000')}');
                    // Close the popup window
                    window.close();
                </script>
            </body>
        </html>
        """
    except Exception as e:
        logging.error(f"Error during Google authorization: {str(e)}")
        logging.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({"error": f"An error occurred during Google authorization: {str(e)}"}), 500
    
