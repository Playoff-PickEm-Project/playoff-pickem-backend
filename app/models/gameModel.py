from flask_sqlalchemy import SQLAlchemy
from app import db

class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    team_one = db.Column(db.String(128), unique=False, nullable=False)
    team_two = db.Column(db.String(128), unique=False, nullable=False)
    
    # To pass from frontend, use Date object and .toISOString
    start_time = db.Column(db.DateTime, nullable=False)
    
    # One-to-Many relationship; each game has multiple props, each prop belongs to a single game
    props = db.relationship('Prop', back_populates='game')