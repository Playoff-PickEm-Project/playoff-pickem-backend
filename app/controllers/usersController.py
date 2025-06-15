from flask import Blueprint, request, jsonify, url_for, session, redirect, current_app
from app.services.usersService import register, login, handle_google_auth
from app.repositories.usersRepository import get_user_by_username
from app.models.userModel import User
from app import db
from flask_bcrypt import Bcrypt
import logging
import traceback
import os

bcrypt = Bcrypt()

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

# New endpoint to check session status
@usersController.route('/session-info', methods=['GET'])
def session_info():
    logging.info(f"Session info check - Session contents: {dict(session)}")
    if 'username' in session:
        logging.info(f"User {session['username']} is logged in")
        return jsonify({
            'username': session['username'],
            'auth_provider': session.get('auth_provider', 'local')
        })
    logging.info("No user found in session")
    return jsonify({'error': 'Not logged in'}), 401

# Google OAuth Login Route
# This route initiates the Google OAuth flow by redirecting to Google's login page
@usersController.route('/login/google', methods=['GET'])
def login_google():
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
    
# Google OAuth Authorization Callback Route
# This route handles the callback from Google after successful authentication
@usersController.route('/authorize/google')
def authorize_google():
    try:
        # Exchange the authorization code for an access token
        token = current_app.google.authorize_access_token()
        
        # Fetch user information from Google's userinfo endpoint
        resp = current_app.google.get('https://www.googleapis.com/oauth2/v3/userinfo')
        user_info = resp.json()
        email = user_info['email']
        
        # Create or update user in our database
        user = handle_google_auth(email)
        
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
    
