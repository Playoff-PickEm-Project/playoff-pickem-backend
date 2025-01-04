from app.models.gameModel import Game

def get_game_by_id(id):
    return Game.query.get(id)