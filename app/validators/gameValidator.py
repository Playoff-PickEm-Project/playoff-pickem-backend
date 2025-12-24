from flask import abort

def validate_game_name(game_name):
    """Validate game name is not None or empty string."""
    if not game_name or (isinstance(game_name, str) and game_name.strip() == ""):
        abort(400, "Game name is required and cannot be empty")
    return game_name.strip() if isinstance(game_name, str) else game_name

def validate_game_exists(game, custom_message=None):
    """Validate that a game object is not None."""
    if game is None:
        message = custom_message or "Game not found"
        abort(404, message)
    return game

def validate_game_id(game_id):
    """Validate game ID is not None."""
    if game_id is None:
        abort(400, "Game ID is required")
    return game_id

def validate_start_time(start_time):
    """Validate start time is not None."""
    if start_time is None:
        abort(400, "Start time is required")
    return start_time
