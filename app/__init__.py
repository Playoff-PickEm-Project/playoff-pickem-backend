from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from app.auth import init_oauth
import os
from dotenv import load_dotenv

# load .env variables
load_dotenv()

# For initializing the sqlalchemy object
db = SQLAlchemy()
migrate = Migrate()

POSTGRESQL_PASSWORD = os.getenv('POSTGRESQL_PASSWORD')

def create_app():
    app = Flask(__name__)
    
    # Set secret key for session management
    app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key')  # Make sure to set SECRET_KEY in your .env file
    
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize OAuth with the app instance
    oauth, google = init_oauth(app)
    app.oauth = oauth
    app.google = google
    
    # Need to import the model before doing db.init in order for the changes to models to be detected
    from app.models.userModel import User
    from app.models.leagueModel import League
    from app.models.gameModel import Game
    from app.models.props.winnerLoserProp import WinnerLoserProp
    from app.models.props.overUnderProp import OverUnderProp
    from app.models.propAnswers.overUnderAnswer import OverUnderAnswer 
    from app.models.propAnswers.winnerLoserAnswer import WinnerLoserAnswer
    from app.models.props.variableOptionProp import VariableOptionProp
    from app.models.props.hashMapAnswers import HashMapAnswers
    from app.models.propAnswers.variableOptionAnswer import VariableOptionAnswer
    # from app.models.allModels import User, League, Player
    
    # Initialize the app with SQLAlchemy and Migrate
    db.init_app(app)
    migrate.init_app(app, db)
    
    return app