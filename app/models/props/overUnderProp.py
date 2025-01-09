from flask_sqlalchemy import SQLAlchemy
from app import db

class OverUnderProp(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    
    question = db.Column(db.String(200))
    
    over_points = db.Column(db.Integer)
    under_points = db.Column(db.Integer)
    
    # String format for correct answer. Either "Over" or "Under"
    correct_answer = db.Column(db.String(10))
    
    def to_dict(self):
        return {
            'prop_id': self.id,
            'game_id': self.game_id,
            'question': self.question,
            'over_points': self.over_points,
            'under_points': self.under_points,
            'correct_answer': self.correct_answer
        }