from flask_sqlalchemy import SQLAlchemy
from app import db
from app.models.props.hashMapAnswers import HashMapAnswers
from sqlalchemy.dialects.postgresql import ARRAY

class VariableOptionProp(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    question = db.Column(db.String(100))
    
    options = db.relationship('HashMapAnswers', foreign_keys=[HashMapAnswers.prop_id])
    
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    
    correct_answer = db.Column(ARRAY(db.String))

    # Whether this prop is mandatory (must be answered) or optional (player can choose)
    # Variable option props default to optional
    is_mandatory = db.Column(db.Boolean, default=False, nullable=False)

    def to_dict(self):
        return {
            'prop_id': self.id,
            'game_id': self.game_id,
            'question': self.question,
            'options': [option.to_dict() for option in self.options],
            'correct_answer': self.correct_answer,
            'is_mandatory': self.is_mandatory,
        }