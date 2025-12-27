from flask_sqlalchemy import SQLAlchemy
from app import db

class OverUnderProp(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))

    question = db.Column(db.String(200))

    over_points = db.Column(db.Numeric)
    under_points = db.Column(db.Numeric)

    # String format for correct answer. Either "Over" or "Under"
    correct_answer = db.Column(db.String(10))

    ## Fields for live polling and stat tracking
    # Player information for ESPN API polling
    player_name = db.Column(db.String(100), nullable=True)
    player_id = db.Column(db.String(50), nullable=True)  # ESPN player ID

    # Stat type to track (e.g., "passing_yards", "rushing_yards", "receiving_yards", "passing_tds", etc.)
    stat_type = db.Column(db.String(50), nullable=True)

    # The line value for the over/under (e.g., 69.5 yards)
    line_value = db.Column(db.Numeric, nullable=True)

    # Current stat value (updated during polling)
    current_value = db.Column(db.Numeric, nullable=True)

    def to_dict(self):
        return {
            'prop_id': self.id,
            'game_id': self.game_id,
            'question': self.question,
            'over_points': self.over_points,
            'under_points': self.under_points,
            'correct_answer': self.correct_answer,
            'player_name': self.player_name,
            'player_id': self.player_id,
            'stat_type': self.stat_type,
            'line_value': float(self.line_value) if self.line_value is not None else None,
            'current_value': float(self.current_value) if self.current_value is not None else None,
        }