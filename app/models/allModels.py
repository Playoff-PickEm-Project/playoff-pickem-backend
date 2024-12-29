# from flask_sqlalchemy import SQLAlchemy
# from app import db

# class Player(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
    
#     name = db.Column(db.String(75), unique=False, nullable=False)
    
#     # A player may be the commissioner of the league.
#     league_commissioner = db.relationship('League', uselist=False, back_populates='commissioner', foreign_keys='League.commissioner_id')
    
#     # Standings (many side)
#     league_id = db.Column(db.Integer, db.ForeignKey('leagues.id'))
#     # league_standing = db.relationship('League', foreign_keys=[league_id], back_populates='player_standings')
    
#     # The league that the player belongs to.
#     league = db.relationship('League', foreign_keys=[league_id], back_populates='league_players')
    
#     # The user that the player belongs to.
#     user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
#     user = db.relationship('User', foreign_keys=[user_id], back_populates='user_players')

# # Model for the league entity
# class League(db.Model):
#     # Each league has a unique id
#     id = db.Column(db.Integer, primary_key=True)
    
#     # League name field
#     league_name = db.Column(db.String(128), unique=True)
    
#     # Join code to allow for other people to join the league.
#     join_code = db.Column(db.String(30), unique=True)
    
#     # Has a user that is the commissioner of the league (note the one-to-one relationship)
#     commissioner_id = db.Column(db.Integer, db.ForeignKey('players.id'))
#     commissioner = db.relationship('Player', foreign_keys=[commissioner_id], back_populates='league_commissioner')
    
#     # All of the players in the league. Note the one-to-many relationship (a league can have multiple players, 
#     # but a player is unique for each league).
#     league_players = db.relationship('Player', foreign_keys=[Player.league_id], back_populates='league')
    
#     # Leaderboard - one-to-many relationship?
#     # player_standings = db.relationship("Player", back_populates='league_standing')
    
# from flask_sqlalchemy import SQLAlchemy
# from app import db
    
# from flask_sqlalchemy import SQLAlchemy
# from app import db

# # Defining and creating a table for all users. Plan is for each user to have a username and password
# class User(db.Model):
#     # Creating all the fields for this entity. Every entity needs an id
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(75), unique=True, nullable=False)
#     password = db.Column(db.String(128), unique=False, nullable=False)
    
#     # A user can have multiple 'player accounts' (for each league), but each player belongs to a single user. One-to-Many relationship.
#     user_players = db.relationship('Player', back_populates='user', foreign_keys=['Player.user_id'])
    
#     def __repr__(self):
#         return f"Username: {self.username}"