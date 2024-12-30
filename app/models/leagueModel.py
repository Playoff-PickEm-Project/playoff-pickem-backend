from flask_sqlalchemy import SQLAlchemy
from app import db
from app.models.playerModel import Player

# Model for the league entity
class League(db.Model):
    # Each league has a unique id
    id = db.Column(db.Integer, primary_key=True)
    
    # League name field
    league_name = db.Column(db.String(128), unique=True)
    
    # Join code to allow for other people to join the league.
    join_code = db.Column(db.String(30), unique=True)
    
    # Has a user that is the commissioner of the league (note the one-to-one relationship)
    commissioner_id = db.Column(db.Integer, db.ForeignKey('player.id'))
    commissioner = db.relationship('Player', foreign_keys=[commissioner_id], back_populates='league_commissioner')
    
    # All of the players in the league. Note the one-to-many relationship (a league can have multiple players, 
    # but a player is unique for each league).
    league_players = db.relationship('Player', foreign_keys=[Player.league_id], back_populates='league')
    
    # Leaderboard - one-to-many relationship?
    # player_standings = db.relationship("Player", back_populates='league_standing')
    
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

    
    