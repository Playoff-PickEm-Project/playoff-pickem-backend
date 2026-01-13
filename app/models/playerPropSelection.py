# This model tracks which props a player has selected to answer for a specific game.
# Players can select up to game.prop_limit props per game (configurable per game).

from flask_sqlalchemy import SQLAlchemy
from app import db

class PlayerPropSelection(db.Model):
    # Unique id for this selection record
    id = db.Column(db.Integer, primary_key=True)

    # The player who made this selection
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    player = db.relationship('Player', back_populates='prop_selections')

    # The game this selection is for
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    game = db.relationship('Game')

    # The type of prop selected: 'winner_loser', 'over_under', or 'variable_option'
    prop_type = db.Column(db.String(50), nullable=False)

    # The ID of the specific prop (references different tables based on prop_type)
    prop_id = db.Column(db.Integer, nullable=False)

    # Composite index to ensure a player can't select the same prop twice for the same game
    __table_args__ = (
        db.UniqueConstraint('player_id', 'game_id', 'prop_type', 'prop_id', name='unique_player_prop_selection'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'player_id': self.player_id,
            'game_id': self.game_id,
            'prop_type': self.prop_type,
            'prop_id': self.prop_id,
        }
