from authlib.integrations.flask_client import OAuth
from api_key import *

# Global variables to store oauth and google objects
oauth = None
google = None

def init_oauth(app):
    global oauth, google
    # Initializing the OAuth object with the Flask app
    oauth = OAuth(app)

    # Registering the Google OAuth client with the client ID and secret
    google = oauth.register(
        name='google',
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={
            'scope': 'openid email profile',
            'redirect_uri': 'http://localhost:5000/authorize/google'  # Add this for local development
        }
    )
    
    return oauth, google 