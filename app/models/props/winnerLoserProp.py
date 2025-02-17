from flask_sqlalchemy import SQLAlchemy
from app import db
# from gameModel import Game

class WinnerLoserProp(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    # Many-to-One relationship - each prop belongs to a game
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    
    question = db.Column(db.String(200))
    
    favorite_team = db.Column(db.String(100))
    underdog_team = db.Column(db.String(100))
    
    favorite_points = db.Column(db.Numeric)
    underdog_points = db.Column(db.Numeric)
    
    # String format for correct answer. Either "Winner" or "Loser"
    correct_answer = db.Column(db.String(20))
    
    def to_dict(self):
        return {
            'prop_id': self.id,
            'game_id': self.game_id,
            'question': self.question,
            'favorite_points': self.favorite_points,
            'underdog_points': self.underdog_points,
            'favorite_team': self.favorite_team,
            'underdog_team': self.underdog_team,
            'correct_answer': self.correct_answer,
        }