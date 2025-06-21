from app.models.gameModel import Game

# Query method to retrieve an instance of a game by its id.
def get_game_by_id(id):
    return Game.query.get(id)