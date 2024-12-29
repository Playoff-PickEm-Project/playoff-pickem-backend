from flask_sqlalchemy import SQLAlchemy
from app import db
from gameModel import Game

class Prop(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    # Many-to-One relationship - each prop belongs to a game
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    game = db.relationship('Game', foreign_keys=[game_id], back_populates='props')
    
    # Answer format
    

class overUnder:
    pass
    
    
class multipleAnswers:
    pass

class winnerLoser:
    pass


# brainstorming
    # each prop should theoretically be a form
    # no, each game has a list of props. so each game should read from a form of multiple props
    # 