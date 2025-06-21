# This model/entity is for an NFL Football game. The associated fields relate to that of an NFL Football Game. 

from flask_sqlalchemy import SQLAlchemy
from app import db
from app.models.props.overUnderProp import OverUnderProp
from app.models.props.variableOptionProp import VariableOptionProp
from app.models.props.winnerLoserProp import WinnerLoserProp

class Game(db.Model):
  	# This is the id for the league. Defined as an integer, and primary_key being true represents that each instance is unique.
    id = db.Column(db.Integer, primary_key=True)
    
    # While each game represents an NFL football game, we know the props for different people will be different. Therefore, we 
    # allow the game model to have a relationship with the league model. Each game is going to be associated with the league it is in, and can be
    # referenced by the id in the league. Note that there is a many to one relationship between games and leagues (many games can be a part of one league).
    league_id = db.Column(db.Integer, db.ForeignKey('league.id'))
    
    ## Will leave the team_one and team_two commented out in case we ever decide to go back to that. 
    ## This field is simply the name of the game (Example: Ravens vs Chiefs). In the frontend, we let the user decide this, but it
    ## is intended to be for the two teams that are playing against each other.
    
    # team_one = db.Column(db.String(128), unique=False, nullable=False)
    # team_two = db.Column(db.String(128), unique=False, nullable=False)
    game_name = db.Column(db.String(200))
    
    ## This is for the time the game will start. This field will help us lock answers once the game starts. Note that we are using
    ## the DateTime data type.
    # Note: To pass from frontend, use Date object and .toISOString
    start_time = db.Column(db.DateTime, nullable=False)
    
    # Each league has an array of all the types of prop questions. For now, will only support winner/loser, over/under, and 
    # props with an unknown number of options.
    # Note: This can be cleaned up. Winner loser, over under could fall into variable option. Something to look into in the future.
    winner_loser_props = db.relationship('WinnerLoserProp', foreign_keys=[WinnerLoserProp.game_id])
    over_under_props = db.relationship('OverUnderProp', foreign_keys=[OverUnderProp.game_id])
    variable_option_props = db.relationship('VariableOptionProp', foreign_keys=[VariableOptionProp.game_id])
    
    # Field intended to check if the game is graded or not. 0 represents not graded, non-zero represents graded.
    graded = db.Column(db.Integer)
    
    def to_dict(self):
        return {
            'id': self.id,
            'game_name': self.game_name,
            'start_time': self.start_time,
            'winner_loser_props': [prop.to_dict() for prop in self.winner_loser_props],
            'over_under_props': [prop.to_dict() for prop in self.over_under_props],
            'variable_option_props': [prop.to_dict() for prop in self.variable_option_props],
        }