from flask import abort

def validate_league_name(league_name):
    """Validate league name is not None or empty string."""
    if not league_name or (isinstance(league_name, str) and league_name.strip() == ""):
        abort(400, "League name is required and cannot be empty")
    return league_name.strip() if isinstance(league_name, str) else league_name

def validate_league_exists(league, custom_message=None):
    """Validate that a league object is not None."""
    if league is None:
        message = custom_message or "League not found"
        abort(404, message)
    return league

def validate_join_code(join_code):
    """Validate join code is not None or empty string."""
    if not join_code or (isinstance(join_code, str) and join_code.strip() == ""):
        abort(400, "Join code is required and cannot be empty")
    return join_code.strip() if isinstance(join_code, str) else join_code

def validate_player_name(player_name):
    """Validate player name is not None or empty string."""
    if not player_name or (isinstance(player_name, str) and player_name.strip() == ""):
        abort(400, "Player name is required and cannot be empty")
    return player_name.strip() if isinstance(player_name, str) else player_name

def validate_player_exists(player, custom_message=None):
    """Validate that a player object is not None."""
    if player is None:
        message = custom_message or "Player not found"
        abort(404, message)
    return player
