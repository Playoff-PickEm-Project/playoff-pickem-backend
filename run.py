# run.py file to run the flask application. Run with 'python3 run.py'

from app import create_app
from app.controllers.propController import propController
from app.controllers.usersController import usersController
from app.controllers.leagueController import leagueController
from app.controllers.gameController import gameController
from flask import request
from flask_cors import CORS
from datetime import timedelta
import os

app = create_app()  # Initialize the app

# Configure session
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

# Configure CORS - allow localhost:3000 to make credentialed requests
CORS(app,
     origins=["http://localhost:3000", "http://127.0.0.1:3000", "https://playoff-pickem-frontend-q31n.onrender.com"],
     supports_credentials=True)

# Register blueprints and other configurations
app.register_blueprint(usersController)
app.register_blueprint(leagueController)
app.register_blueprint(gameController)
app.register_blueprint(propController)

if __name__ == "__main__":
    app.run(debug=True)
