# This model represents a league - for groups of people to compete and see who can score the most points (by getting the most props right based on point values).
from flask_sqlalchemy import SQLAlchemy
from app import db
from app.models.gameModel import Game
from app.models.playerModel import Player

class League(db.Model):
    # Each league has a unique id
    id = db.Column(db.Integer, primary_key=True)
    
    # League name field
    league_name = db.Column(db.String(128), unique=True)
    
    # Field for the join code to allow for other people to join the league. Ends up being a randomly generated string.
    join_code = db.Column(db.String(30), unique=True)
    
    # Each league has a user that is the commissioner of the league (note the one-to-one relationship).
    # I don't remember why I put both the entity itself and the id. Traditional practice I believe is to keep it to id, but either works.
    # Watch for infinite recursion if doing the relationship with the entity itself. 
    commissioner_id = db.Column(db.Integer, db.ForeignKey('player.id'))
    commissioner = db.relationship('Player', foreign_keys=[commissioner_id])
    
    
    ### For the following two fields, note how we use db.relationship. Using db.relationship on the "one" side signifies that the many side is
    ### on the other side of the relationship (which will use foreignKey to identify this model).
    # All of the players in the league. Note the one-to-many relationship (a league can have multiple players, 
    # but a player is unique for each league).
    league_players = db.relationship('Player', foreign_keys=[Player.league_id])
    
    # Note the one to many relationship. Each league has many games. 
    league_games = db.relationship('Game', foreign_keys=[Game.league_id])
    
    def __repr__(self):
        return f"<League(id={self.id}, league_name={self.league_name}, join_code={self.join_code}, commissioner_id={self.commissioner_id})>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'league_name': self.league_name,
            'join_code': self.join_code,
            'commissioner_id': self.commissioner_id,
            'commissioner': self.commissioner.to_dict() if self.commissioner else None,  # Assuming the Player class has a to_dict method
            'league_players': [player.to_dict() for player in self.league_players],  # Assuming Player class also has a to_dict method
        }
