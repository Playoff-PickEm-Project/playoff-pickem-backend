from flask_sqlalchemy import SQLAlchemy
from app import db

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    name = db.Column(db.String(75), unique=False, nullable=False)
    
    # A player may be the commissioner of the league.
    league_commissioner = db.relationship('League', uselist=False, back_populates='commissioner', foreign_keys='League.commissioner_id')
    
    # Standings (many side)
    league_id = db.Column(db.Integer, db.ForeignKey('league.id'))
    # league_standing = db.relationship('League', foreign_keys=[league_id], back_populates='player_standings')
    
    # The league that the player belongs to.
    league = db.relationship('League', foreign_keys=[league_id], back_populates='league_players')
    
    # The user that the player belongs to.
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', foreign_keys=[user_id], back_populates='user_players')