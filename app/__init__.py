from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv

# For initializing the sqlalchemy object
db = SQLAlchemy()

load_dotenv()

POSTGRESQL_PASSWORD = os.getenv('POSTGRESQL_PASSWORD')

def create_app():
    app = Flask(__name__)
    
    app.config['SQLAlchemy_DATABASE_URI'] = f"postgres://sathvik_akhil:{POSTGRESQL_PASSWORD}@localhost:5432/playoff_pickems"
    app.config['SQLAlchemy_Track_Modifications'] = False
    
    # Initialize the app with SQLAlchemy and Migrate
    db.init_app(app)
    migrate = Migrate(app, db)

    from . import home_screen as home_screen_blueprint
    app.register_blueprint(home_screen_blueprint)

    return app