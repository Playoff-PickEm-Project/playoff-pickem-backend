# run.py file to run the flask application. Run with 'python3 run.py'

from app import create_app
from app.controllers.propController import propController
from app.controllers.usersController import usersController
from app.controllers.leagueController import leagueController
from app.controllers.gameController import gameController
from flask_cors import CORS
from datetime import timedelta
import os

app = create_app()  # Initialize the app

# Configure session
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

# Configure CORS with credentials support
CORS(app,
     resources={r"/*": {
         "origins": [
             "https://playoff-pickem-frontend-q31n.onrender.com",
             "http://localhost:3000",
             "http://127.0.0.1:3000"
         ],
         "supports_credentials": True,
         "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         "allow_headers": ["Content-Type", "Authorization"],
         "expose_headers": ["Content-Type", "Authorization"],
         "max_age": 3600
     }},
     supports_credentials=True)

@app.after_request
def add_cache_headers(response):
    # This will ensure no caching
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, proxy-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

# Register blueprints and other configurations
app.register_blueprint(usersController)
app.register_blueprint(leagueController)
app.register_blueprint(gameController)
app.register_blueprint(propController)

if __name__ == "__main__":
    app.run(debug=True)
