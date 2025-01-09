from flask_sqlalchemy import SQLAlchemy
from app import db

# Defining and creating a table for all users. Plan is for each user to have a username and password
class User(db.Model):
    # Creating all the fields for this entity. Every entity needs an id
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(75), unique=True, nullable=False)
    password = db.Column(db.String(128), unique=False, nullable=False)
    
    # A user can have multiple 'player accounts' (for each league), but each player belongs to a single user. One-to-Many relationship.
    user_players = db.relationship('Player', back_populates='user')
    
    def __repr__(self):
        return f"Username: {self.username}"
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
        }