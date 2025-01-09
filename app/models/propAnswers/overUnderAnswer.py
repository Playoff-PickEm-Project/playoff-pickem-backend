from flask_sqlalchemy import SQLAlchemy
from app import db

class OverUnderAnswer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    answer = db.Column(db.String(256))
    
    # Which prop does this answer belong to
    prop_id = db.Column(db.Integer, db.ForeignKey('over_under_prop.id'))
    
    # Which player does this answer belong to
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'))
    
    def toDict(self):
        return {
            'id': self.id,
            'answer': self.answer,
            'prop_id': self.prop_id,
            'player_id': self.player_id,
        }