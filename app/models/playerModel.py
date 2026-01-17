# The player model is associated with a league. Each user can have multiple players, and leagues are expected to have multiple players.

from flask_sqlalchemy import SQLAlchemy
from app import db
from app.models.propAnswers.overUnderAnswer import OverUnderAnswer
from app.models.propAnswers.variableOptionAnswer import VariableOptionAnswer
from app.models.propAnswers.winnerLoserAnswer import WinnerLoserAnswer

class Player(db.Model):
		# Unique id of the player.
    id = db.Column(db.Integer, primary_key=True)
    
    # Name for the player.
    name = db.Column(db.String(75), unique=False, nullable=False)
    
    # A player may be the commissioner of the league.
    #league_commissioner = db.relationship('League', uselist=False, back_populates='commissioner', foreign_keys='League.commissioner_id')
    
    # Id of the league this player is a part of.
    league_id = db.Column(db.Integer, db.ForeignKey('league.id'))
    # league_standing = db.relationship('League', foreign_keys=[league_id], back_populates='player_standings')
    
    # The league that the player belongs to.
    #league = db.relationship('League', foreign_keys=[league_id], back_populates='league_players')
    
    # The user that the player belongs to.
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', foreign_keys=[user_id], back_populates='user_players')
    
    # Number of points the player has.
    points = db.Column(db.Numeric)
    
    # These three fields represent the answers this player holds for the three types of questions. Note that this is the one side of a one to many
    # relationship, signified by "db.relationship".
    player_winner_loser_answers = db.relationship('WinnerLoserAnswer', foreign_keys=[WinnerLoserAnswer.player_id])
    player_over_under_answers = db.relationship('OverUnderAnswer', foreign_keys=[OverUnderAnswer.player_id])
    player_variable_option_answers = db.relationship('VariableOptionAnswer', foreign_keys=[VariableOptionAnswer.player_id])

    # Tracks which props this player has selected to answer (new feature)
    prop_selections = db.relationship('PlayerPropSelection', back_populates='player', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'league_id': self.league_id,
            'user_id': self.user_id,
            'username': self.user.username if self.user else None,  # Include username for matching
            'points': float(self.points) if self.points else 0,  # Convert Numeric to float
            #'league': self.league.to_dict() if self.league else None,  # Include league details if exists
            #'user': self.user.to_dict() if self.user else None   # Include user details if exists
        }
        
## I'm assuming right now, we identify through the league entity if the league's commissioner == the current comissioner. Consider adding a flag field for 
## if the player is a comissioner or not, since players should not be able to be duplicated. is_comissioner