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
    
    app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://sathvik_akhil:{POSTGRESQL_PASSWORD}@localhost:5432/playoff_pickems"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Need to import the model before doing db.init in order for the changes to models to be detected
    from app.models.userModel import User
    from app.models.playerModel import Player
    from app.models.leagueModel import League
    from app.models.gameModel import Game
    # from app.models.allModels import User, League, Player
    
    # Initialize the app with SQLAlchemy and Migrate
    db.init_app(app)
    Migrate(app, db)

    return app