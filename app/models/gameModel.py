from flask_sqlalchemy import SQLAlchemy
from app import db
from app.models.props.overUnderProp import OverUnderProp
from app.models.props.variableOptionProp import VariableOptionProp
from app.models.props.winnerLoserProp import WinnerLoserProp

class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    league_id = db.Column(db.Integer, db.ForeignKey('league.id'))
    
    # team_one = db.Column(db.String(128), unique=False, nullable=False)
    # team_two = db.Column(db.String(128), unique=False, nullable=False)
    game_name = db.Column(db.String(200))
    
    # To pass from frontend, use Date object and .toISOString
    start_time = db.Column(db.DateTime, nullable=False)
    
    # Each league has an array of all the types of prop questions. For now, will only support winner/loser and over/under.
    winner_loser_props = db.relationship('WinnerLoserProp', foreign_keys=[WinnerLoserProp.game_id])
    over_under_props = db.relationship('OverUnderProp', foreign_keys=[OverUnderProp.game_id])
    variable_option_props = db.relationship('VariableOptionProp', foreign_keys=[VariableOptionProp.game_id])
    
    # Field to check if the game is graded or not. 0 represents not graded, non-zero represents graded.
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