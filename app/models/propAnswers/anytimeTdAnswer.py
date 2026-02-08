"""
Anytime TD Answer Model

This model stores a player's answer to an Anytime TD Scorer prop.
Each answer represents a player's selection of which player they think
will score touchdowns.

Example:
    Player "John" selects "Travis Kelce" for prop #5
"""

from flask_sqlalchemy import SQLAlchemy
from app import db


class AnytimeTdAnswer(db.Model):
    """
    Anytime TD Answer Model

    Represents a player's answer to an Anytime TD prop. The answer is
    the name of the player they selected from the available options.

    Attributes:
        id (int): Unique identifier for the answer
        answer (str): The player name selected (e.g., "Travis Kelce")
        prop_id (int): Foreign key to the AnytimeTdProp
        player_id (int): Foreign key to the Player who submitted this answer

    Relationships:
        anytime_td_prop: The prop this answer belongs to (many-to-one)
        player: The player who submitted this answer (many-to-one)
    """

    # Table name
    __tablename__ = 'anytime_td_answer'

    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # The player name selected as the answer (e.g., "Travis Kelce")
    answer = db.Column(db.String(200), nullable=False)

    # Foreign key to the prop
    prop_id = db.Column(
        db.Integer,
        db.ForeignKey('anytime_td_prop.id'),
        nullable=False
    )

    # Foreign key to the player who answered
    player_id = db.Column(
        db.Integer,
        db.ForeignKey('player.id'),
        nullable=False
    )

    def to_dict(self):
        """
        Convert the answer to a dictionary for JSON serialization.

        Returns:
            dict: Dictionary representation of the answer

        Example:
            {
                'id': 1,
                'answer': 'Travis Kelce',
                'prop_id': 10,
                'player_id': 5
            }
        """
        return {
            'id': self.id,
            'answer': self.answer,
            'prop_id': self.prop_id,
            'player_id': self.player_id
        }

    def __repr__(self):
        """
        String representation of the answer.

        Returns:
            str: Human-readable representation
        """
        return f"<AnytimeTdAnswer(id={self.id}, answer='{self.answer}', player_id={self.player_id})>"
