from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv
# from .controllers import usersController

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
    from app.models.userModel import Users
    
    # Initialize the app with SQLAlchemy and Migrate
    db.init_app(app)
    migrate = Migrate(app, db)

    #app.register_blueprint(usersController)

    return app