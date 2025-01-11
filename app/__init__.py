from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv

# load .env variables
load_dotenv()

# For initializing the sqlalchemy object
db = SQLAlchemy()

POSTGRESQL_PASSWORD = os.getenv('POSTGRESQL_PASSWORD')

def create_app():
    app = Flask(__name__)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Need to import the model before doing db.init in order for the changes to models to be detected
    from app.models.userModel import User
    from app.models.playerModel import Player
    from app.models.leagueModel import League
    from app.models.gameModel import Game
    from app.models.props.winnerLoserProp import WinnerLoserProp
    from app.models.props.overUnderProp import OverUnderProp
    from app.models.propAnswers.overUnderAnswer import OverUnderAnswer 
    from app.models.propAnswers.winnerLoserAnswer import WinnerLoserAnswer
    # from app.models.allModels import User, League, Player
    
    # Initialize the app with SQLAlchemy and Migrate
    db.init_app(app)
    Migrate(app, db)

    return app