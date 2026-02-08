"""
Anytime TD Option Model

This model represents an individual player option within an Anytime TD Scorer prop.
Each option has its own player, TD line, point value, and live TD tracking.

Example:
    Travis Kelce - 0.5 TD line - 5 points - Currently 2 TDs
    Patrick Mahomes - 1.5 TD line - 12 points - Currently 1 TD
"""

from flask_sqlalchemy import SQLAlchemy
from app import db


class AnytimeTdOption(db.Model):
    """
    Anytime TD Option Model

    Represents a single player option within an Anytime TD prop. Each option
    has its own TD line threshold and point value.

    Attributes:
        id (int): Unique identifier for the option
        player_name (str): Name of the player (e.g., "Travis Kelce")
        td_line (float): TD threshold for this player (e.g., 0.5 for 1+, 1.5 for 2+)
        points (float): Points awarded if player scores >= td_line touchdowns
        current_tds (int): Live count of TDs scored by this player (updated by polling)
        anytime_td_prop_id (int): Foreign key to parent AnytimeTdProp

    Relationships:
        anytime_td_prop: The parent prop this option belongs to (many-to-one)
    """

    # Table name
    __tablename__ = 'anytime_td_option'

    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # Player name for this option
    player_name = db.Column(db.String(200), nullable=False)

    # TD line threshold (0.5 = 1+ TD, 1.5 = 2+ TDs, etc.)
    td_line = db.Column(db.Float, nullable=False, default=0.5)

    # Points awarded if this player hits their TD line
    points = db.Column(db.Float, nullable=False)

    # Current number of TDs scored by this player (updated from live stats)
    current_tds = db.Column(db.Integer, nullable=True, default=0)

    # Foreign key to parent prop
    anytime_td_prop_id = db.Column(
        db.Integer,
        db.ForeignKey('anytime_td_prop.id'),
        nullable=False
    )

    def to_dict(self):
        """
        Convert the option to a dictionary for JSON serialization.

        Returns:
            dict: Dictionary representation of the option

        Example:
            {
                'id': 1,
                'player_name': 'Travis Kelce',
                'td_line': 0.5,
                'points': 5,
                'current_tds': 2,
                'anytime_td_prop_id': 10
            }
        """
        return {
            'id': self.id,
            'player_name': self.player_name,
            'td_line': self.td_line,
            'points': self.points,
            'current_tds': self.current_tds if self.current_tds is not None else 0,
            'anytime_td_prop_id': self.anytime_td_prop_id
        }

    def has_hit_line(self):
        """
        Check if this player has hit their TD line.

        Returns:
            bool: True if current_tds >= td_line, False otherwise

        Example:
            If td_line is 0.5 and current_tds is 1, returns True
            If td_line is 1.5 and current_tds is 1, returns False
        """
        if self.current_tds is None:
            return False
        return self.current_tds >= self.td_line
