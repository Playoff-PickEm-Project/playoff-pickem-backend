from flask_sqlalchemy import SQLAlchemy
from app import db
from app.models.propAnswers.overUnderAnswer import OverUnderAnswer
from app.models.propAnswers.winnerLoserAnswer import WinnerLoserAnswer

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    name = db.Column(db.String(75), unique=False, nullable=False)
    
    # A player may be the commissioner of the league.
    #league_commissioner = db.relationship('League', uselist=False, back_populates='commissioner', foreign_keys='League.commissioner_id')
    
    # Standings (many side)
    league_id = db.Column(db.Integer, db.ForeignKey('league.id'))
    # league_standing = db.relationship('League', foreign_keys=[league_id], back_populates='player_standings')
    
    # The league that the player belongs to.
    #league = db.relationship('League', foreign_keys=[league_id], back_populates='league_players')
    
    # The user that the player belongs to.
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', foreign_keys=[user_id], back_populates='user_players')
    
    # In order to calculate the number of points a player has.
    points = db.Column(db.Numeric)
    
    player_winner_loser_answers = db.relationship('WinnerLoserAnswer', foreign_keys=[WinnerLoserAnswer.player_id])
    player_over_under_answers = db.relationship('OverUnderAnswer', foreign_keys=[OverUnderAnswer.player_id])
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'league_id': self.league_id,
            'user_id': self.user_id,
            'points': self.points,
            #'league': self.league.to_dict() if self.league else None,  # Include league details if exists
            #'user': self.user.to_dict() if self.user else None   # Include user details if exists
        }