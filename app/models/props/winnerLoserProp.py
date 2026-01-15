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

    ## Fields for live polling and team tracking
    # ESPN team IDs or abbreviations for API polling
    team_a_id = db.Column(db.String(50), nullable=True)  # ESPN team ID (e.g., "BAL")
    team_b_id = db.Column(db.String(50), nullable=True)  # ESPN team ID (e.g., "KC")

    # Full team names for display
    team_a_name = db.Column(db.String(100), nullable=True)  # "Baltimore Ravens"
    team_b_name = db.Column(db.String(100), nullable=True)  # "Kansas City Chiefs"

    # Live scores (updated during polling)
    team_a_score = db.Column(db.Integer, nullable=True)
    team_b_score = db.Column(db.Integer, nullable=True)

    # ID of the winning team after game ends (used for grading)
    winning_team_id = db.Column(db.String(50), nullable=True)

    # Whether this prop is mandatory (must be answered) or optional (player can choose)
    # Winner/Loser props default to mandatory
    is_mandatory = db.Column(db.Boolean, default=True, nullable=False)

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
            'team_a_id': self.team_a_id,
            'team_b_id': self.team_b_id,
            'team_a_name': self.team_a_name,
            'team_b_name': self.team_b_name,
            'team_a_score': self.team_a_score,
            'team_b_score': self.team_b_score,
            'winning_team_id': self.winning_team_id,
            'is_mandatory': self.is_mandatory,
        }