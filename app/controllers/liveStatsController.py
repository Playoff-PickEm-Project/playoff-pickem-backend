"""
Live Stats Controller for handling ESPN data and live game updates.

This controller provides endpoints for:
- Fetching available players for a game (for prop creation)
- Getting live stats for a game
- Manually triggering polling (for testing/debugging)
"""

from flask import Blueprint, jsonify, request
from app.services.espnClientService import ESPNClientService
from app.services.game.pollingService import PollingService
from app.models.gameModel import Game
from app.validators.gameValidator import validate_game_id, validate_game_exists
from app.repositories.gameRepository import get_game_by_id

liveStatsController = Blueprint('liveStatsController', __name__)


@liveStatsController.route('/game/<int:game_id>/available_players', methods=['GET'])
def get_available_players(game_id):
    """
    Get list of available players for a game to use in prop creation.

    Filters to skill positions only (QB, RB, WR, TE).

    Args (URL):
        game_id (int): The ID of the game

    Returns:
        JSON: List of players with name, ID, and position
            [{"name": "Patrick Mahomes", "id": "123", "position": "QB"}, ...]

    Raises:
        400: If game_id is invalid
        404: If game not found or missing external_game_id
    """
    game_id = validate_game_id(game_id)
    game = get_game_by_id(game_id)
    validate_game_exists(game)

    if not game.external_game_id:
        return jsonify({"error": "Game does not have an ESPN game ID"}), 404

    # Filter to skill positions only
    skill_positions = ["QB", "RB", "WR", "TE"]
    players = ESPNClientService.get_available_players(game.external_game_id, positions=skill_positions)

    return jsonify({
        "game_id": game_id,
        "players": players
    })


@liveStatsController.route('/game/<int:game_id>/live_stats', methods=['GET'])
def get_live_stats(game_id):
    """
    Get live stats for a game including scores and prop current values.

    Returns:
        - Game status (in progress, completed, etc.)
        - Team scores
        - Current values for all O/U props
        - Current scores for all W/L props

    Args (URL):
        game_id (int): The ID of the game

    Returns:
        JSON: Live game data including:
            {
                "game_id": int,
                "is_completed": bool,
                "is_polling": bool,
                "team_a_score": int,
                "team_b_score": int,
                "over_under_props": [
                    {
                        "prop_id": int,
                        "player_name": str,
                        "stat_type": str,
                        "line_value": float,
                        "current_value": float
                    }
                ],
                "winner_loser_props": [
                    {
                        "prop_id": int,
                        "team_a_name": str,
                        "team_a_score": int,
                        "team_b_name": str,
                        "team_b_score": int
                    }
                ]
            }

    Raises:
        400: If game_id is invalid
        404: If game not found
    """
    game_id = validate_game_id(game_id)
    game = get_game_by_id(game_id)
    validate_game_exists(game)

    # Build response with live data
    over_under_stats = []
    for prop in game.over_under_props:
        over_under_stats.append({
            "prop_id": prop.id,
            "question": prop.question,
            "player_name": prop.player_name,
            "stat_type": prop.stat_type,
            "line_value": float(prop.line_value) if prop.line_value is not None else None,
            "current_value": float(prop.current_value) if prop.current_value is not None else None
        })

    winner_loser_stats = []
    for prop in game.winner_loser_props:
        winner_loser_stats.append({
            "prop_id": prop.id,
            "question": prop.question,
            "team_a_name": prop.team_a_name,
            "team_a_score": prop.team_a_score,
            "team_b_name": prop.team_b_name,
            "team_b_score": prop.team_b_score,
            "winning_team_id": prop.winning_team_id
        })

    return jsonify({
        "game_id": game_id,
        "game_name": game.game_name,
        "is_completed": game.is_completed,
        "is_polling": game.is_polling,
        "team_a_score": game.team_a_score,
        "team_b_score": game.team_b_score,
        "over_under_props": over_under_stats,
        "winner_loser_props": winner_loser_stats
    })


@liveStatsController.route('/game/<int:game_id>/manual_poll', methods=['POST'])
def manual_poll_game(game_id):
    """
    Manually trigger a poll for a specific game (for testing/debugging).

    This bypasses the scheduler and immediately polls ESPN for the game.

    Args (URL):
        game_id (int): The ID of the game to poll

    Returns:
        JSON: Success message or error

    Raises:
        400: If game_id is invalid
        404: If game not found or missing external_game_id
    """
    game_id = validate_game_id(game_id)

    result = PollingService.manually_trigger_poll(game_id)

    if result["success"]:
        return jsonify(result), 200
    else:
        return jsonify(result), 404


@liveStatsController.route('/scoreboard', methods=['GET'])
def get_scoreboard():
    """
    Get NFL scoreboard for a specific date.

    Useful for finding ESPN game IDs when creating new games.

    Args (Query params):
        date (str, optional): Date in YYYYMMDD format (e.g., "20250115")
                             If not provided, returns today's games

    Returns:
        JSON: ESPN scoreboard data

    Example:
        GET /scoreboard?date=20250115
    """
    date = request.args.get('date', None)

    scoreboard_data = ESPNClientService.get_scoreboard(date)

    if scoreboard_data:
        return jsonify(scoreboard_data), 200
    else:
        return jsonify({"error": "Failed to fetch scoreboard data"}), 500


@liveStatsController.route('/espn_game/<string:espn_game_id>/available_players', methods=['GET'])
def get_available_players_by_espn_id(espn_game_id):
    """
    Get list of available players for an ESPN game (for game creation).

    This endpoint accepts ESPN game IDs directly, useful when creating a new game
    that doesn't exist in the database yet.

    Filters to skill positions only (QB, RB, WR, TE).

    Args (URL):
        espn_game_id (str): The ESPN game ID (e.g., "401772915")

    Returns:
        JSON: List of players with name, ID, and position
            {"players": [{"name": "Patrick Mahomes", "id": "123", "position": "QB"}, ...]}

    Raises:
        404: If unable to fetch player data from ESPN
    """
    try:
        # Filter to skill positions only
        skill_positions = ["QB", "RB", "WR", "TE"]
        players = ESPNClientService.get_available_players(espn_game_id, positions=skill_positions)

        return jsonify({
            "espn_game_id": espn_game_id,
            "players": players
        }), 200
    except Exception as e:
        return jsonify({"error": f"Failed to fetch players: {str(e)}"}), 404
