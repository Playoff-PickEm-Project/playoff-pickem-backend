from flask_sqlalchemy import SQLAlchemy
from app import db

class VariableOptionAnswer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    answer = db.Column(db.String(100))
    
    prop_id = db.Column(db.Integer, db.ForeignKey('variable_option_prop.id'))
    
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'))
    
    def toDict(self):
        return {
            'id': self.id,
            'answer': self.answer,
            'prop_id': self.prop_id,
            'player_id': self.player_id,
        }