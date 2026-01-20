"""
Anytime TD Scorer Prop Model

This model represents a touchdown scorer prediction prop where users select
one player from multiple options, each with their own TD line (e.g., 0.5 for 1+ TD,
1.5 for 2+ TDs). Points are awarded if the selected player scores touchdowns
greater than or equal to their specific line.

Example:
    A prop might have options like:
    - Travis Kelce (0.5 TD line, +5 pts)
    - Patrick Mahomes (1.5 TD line, +12 pts)
    - Rashee Rice (1.5 TD line, +10 pts)

The prop can be auto-graded using live game statistics from the polling system.
"""

from flask_sqlalchemy import SQLAlchemy
from app import db


class AnytimeTdProp(db.Model):
    """
    Anytime TD Scorer Prop Model

    Represents a prop where users predict which player will score touchdowns.
    Each prop contains multiple player options (AnytimeTdOption), and users
    select one player. Grading is automatic based on live TD statistics.

    Attributes:
        id (int): Unique identifier for the prop
        question (str): The prop question text (e.g., "Pick a player to score a TD")
        game_id (int): Foreign key to the game this prop belongs to
        is_mandatory (bool): Whether all players must answer this prop
        correct_answer (list): List of player names who hit their TD line (JSON array)

    Relationships:
        game: The game this prop belongs to
        options: List of player options for this prop (one-to-many)
        answers: Player answers for this prop (one-to-many)
    """

    # Table name
    __tablename__ = 'anytime_td_prop'

    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # Prop question/description
    question = db.Column(db.String(500), nullable=False)

    # Foreign key to game
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)

    # Whether this prop is mandatory for all players
    is_mandatory = db.Column(db.Boolean, default=False, nullable=False)

    # Correct answer(s) - JSON array of player names who scored >= their line
    # Example: ["Travis Kelce", "Patrick Mahomes"]
    correct_answer = db.Column(db.JSON, nullable=True)

    # Relationships
    # One-to-many: One prop has many options (players to choose from)
    options = db.relationship(
        'AnytimeTdOption',
        backref='anytime_td_prop',
        lazy=True,
        cascade='all, delete-orphan'
    )

    # One-to-many: One prop has many answers (player selections)
    answers = db.relationship(
        'AnytimeTdAnswer',
        backref='anytime_td_prop',
        lazy=True,
        cascade='all, delete-orphan'
    )

    def to_dict(self):
        """
        Convert the prop to a dictionary for JSON serialization.

        Returns:
            dict: Dictionary representation including all options

        Example:
            {
                'prop_id': 1,
                'question': 'Pick a player to score a TD',
                'game_id': 5,
                'is_mandatory': False,
                'correct_answer': ['Travis Kelce'],
                'options': [
                    {
                        'id': 1,
                        'player_name': 'Travis Kelce',
                        'td_line': 0.5,
                        'points': 5,
                        'current_tds': 2
                    },
                    ...
                ]
            }
        """
        return {
            'prop_id': self.id,
            'question': self.question,
            'game_id': self.game_id,
            'is_mandatory': self.is_mandatory,
            'correct_answer': self.correct_answer,
            'options': [option.to_dict() for option in self.options] if self.options else []
        }
