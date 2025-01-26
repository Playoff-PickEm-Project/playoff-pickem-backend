from flask_sqlalchemy import SQLAlchemy
from app import db

class HashMapAnswers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    answer_choice = db.Column(db.String(100))
    answer_points = db.Column(db.Integer)
    
    prop_id = db.Column(db.Integer, db.ForeignKey('variable_option_prop.id'))
    
    def to_dict(self):
        return {
            'id': self.id,
            'prop_id': self.id,
            'answer_choice': self.answer_choice,
            'answer_points': self.answer_points,
        }