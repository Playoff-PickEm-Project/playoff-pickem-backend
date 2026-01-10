from flask import Blueprint, jsonify, request
from app.services.game.gameService import GameService
from app.services.game.gradeGameService import GradeGameService
from app.services.leagueService import LeagueService
from app.repositories.gameRepository import get_game_by_id

"""
Game Controller

Handles all game-related HTTP endpoints including answering props, grading games,
deleting games, and retrieving game information and player picks.
"""

gameController = Blueprint('gameController', __name__)

@gameController.route('/answer_winner_loser_prop', methods=['POST'])
def answerWinnerLoserProp():
    """
    Save or update a player's answer for a winner/loser prop.

    Expects JSON body with:
        - leagueName (str): The name of the league
        - username (str): The username of the player
        - prop_id (int): The ID of the winner/loser prop
        - answer (str): The player's answer (team name)

    Returns:
        JSON: Success message
    """
    data = request.get_json()

    leagueName = data.get('leagueName')
    username = data.get('username')
    prop_id = data.get('prop_id')
    answer = data.get('answer')

    result = GameService.answer_winner_loser_prop(leagueName, username, prop_id, answer)

    return jsonify(result)

@gameController.route('/answer_over_under_prop', methods=['POST'])
def answerOverUnderProp():
    """
    Save or update a player's answer for an over/under prop.

    Expects JSON body with:
        - leagueName (str): The name of the league
        - username (str): The username of the player
        - prop_id (int): The ID of the over/under prop
        - answer (str): The player's answer ("over" or "under")

    Returns:
        JSON: Success message
    """
    data = request.get_json()

    leagueName = data.get('leagueName')
    username = data.get('username')
    prop_id = data.get('prop_id')
    answer = data.get('answer')

    result = GameService.answer_over_under_prop(leagueName, username, prop_id, answer)

    return jsonify(result)

@gameController.route('/answer_variable_option_prop', methods=['POST'])
def answerVariableOptionProp():
    """
    Save or update a player's answer for a variable option prop.

    Expects JSON body with:
        - leagueName (str): The name of the league
        - username (str): The username of the player
        - prop_id (int): The ID of the variable option prop
        - answer (str): The player's selected answer choice

    Returns:
        JSON: Success message
    """
    data = request.get_json()

    leagueName = data.get('leagueName')
    username = data.get('username')
    prop_id = data.get('prop_id')
    answer = data.get('answer')

    result = GameService.answer_variable_option_prop(leagueName, username, prop_id, answer)

    return jsonify(result)

@gameController.route('/answer_game', methods=['POST'])
def answerGame():
    """
    Save answers for all props in a game for a specific player.

    Expects JSON body with:
        - leagueName (str): The name of the league
        - username (str): The username of the player
        - game_id (int): The ID of the game
        - answer (dict): Dictionary containing answers for all props

    Returns:
        JSON: Success message
    """
    data = request.get_json()

    leagueName = data.get('leagueName')
    username = data.get('username')
    game_id = data.get('game_id')
    answer = data.get('answer')

    result = GameService.answer_game(leagueName, username, game_id, answer)

    return jsonify(result)

@gameController.route('/get_game_by_id', methods=['GET'])
def getGameByID():
    """
    Retrieve a game by its ID.

    Query Parameters:
        - game_id (int): The ID of the game

    Returns:
        JSON: Game object as dictionary
    """
    game_id = request.args.get('game_id')

    game = get_game_by_id(game_id)

    return jsonify(game.to_dict())

@gameController.route('/grade_game', methods=['POST'])
def gradeGame():
    """
    Grade a game by awarding points to players for correct answers.

    Expects JSON body with:
        - game_id (int): The ID of the game to grade

    Returns:
        JSON: Success response
    """
    data = request.get_json()
    game_id = data.get('game_id')

    result = GradeGameService.grade_game(game_id)

    return jsonify(result)

@gameController.route('/delete_game', methods=['POST'])
def deleteGame():
    """
    Delete a game and all associated props and answers.

    Expects JSON body with:
        - game_id (int): The ID of the game to delete
        - leaguename (str): The name of the league containing the game

    Returns:
        JSON: Success response
    """
    data = request.get_json()

    game_id = data.get('game_id')
    leaguename = data.get('leaguename')

    result = LeagueService.delete_game(leaguename, game_id)

    return jsonify(result)

@gameController.route('/add_winner_loser_prop', methods=['POST'])
def addWinnerLoserProp():
    """
    Add a new Winner/Loser prop to an existing game.

    Expects JSON body with:
        - game_id (int): The ID of the game to add the prop to
        - question (str): The prop question text
        - favorite_team (str): Name of the favorite team
        - underdog_team (str): Name of the underdog team
        - favorite_points (float): Points awarded for picking favorite
        - underdog_points (float): Points awarded for picking underdog

    Returns:
        JSON: Success response with the newly created prop's ID
    """
    data = request.get_json()
    result = GameService.add_winner_loser_prop(data)
    return jsonify(result)

@gameController.route('/add_over_under_prop', methods=['POST'])
def addOverUnderProp():
    """
    Add a new Over/Under prop to an existing game.

    Expects JSON body with:
        - game_id (int): The ID of the game to add the prop to
        - question (str): The prop question text
        - over_points (float): Points awarded for picking over
        - under_points (float): Points awarded for picking under
        - player_name (str, optional): Name of player for stat tracking
        - player_id (str, optional): ESPN player ID for live stat tracking
        - stat_type (str, optional): Type of stat to track (e.g., "passing_yards")
        - line_value (float, optional): The over/under line value

    Returns:
        JSON: Success response with the newly created prop's ID
    """
    data = request.get_json()
    result = GameService.add_over_under_prop(data)
    return jsonify(result)

@gameController.route('/add_variable_option_prop', methods=['POST'])
def addVariableOptionProp():
    """
    Add a new Variable Option (multiple choice) prop to an existing game.

    Expects JSON body with:
        - game_id (int): The ID of the game to add the prop to
        - question (str): The prop question text
        - options (list): List of option objects with 'choice_text' and 'points'
            Example: [{"choice_text": "Option A", "points": 1.0}, ...]

    Returns:
        JSON: Success response with the newly created prop's ID
    """
    data = request.get_json()
    result = GameService.add_variable_option_prop(data)
    return jsonify(result)

@gameController.route('/delete_prop', methods=['POST'])
def deleteProp():
    """
    Delete a specific prop from a game.

    Works for all prop types (Winner/Loser, Over/Under, Variable Option).
    Also deletes all associated player answers.

    Expects JSON body with:
        - prop_id (int): The ID of the prop to delete
        - prop_type (str): Type of prop - "winner_loser", "over_under", or "variable_option"

    Returns:
        JSON: Success response
    """
    data = request.get_json()
    result = GameService.delete_prop(data)
    return jsonify(result)

@gameController.route('/update_game', methods=['POST'])
def updateGame():
    """
    Update game metadata (name, start time, external game ID).

    Expects JSON body with:
        - game_id (int): The ID of the game to update
        - game_name (str, optional): New game name
        - start_time (str, optional): New start time (ISO format)
        - external_game_id (str, optional): New ESPN game ID

    Returns:
        JSON: Success response with message
    """
    data = request.get_json()
    result = GameService.update_game(data)
    return jsonify(result)

@gameController.route('/view_all_answers_for_game', methods=['GET'])
def getAllPicksFromGame():
    """
    Retrieve all player answers/picks for all props in a game.

    Query Parameters:
        - game_id (int): The ID of the game

    Returns:
        JSON: List of all player picks with player names, answers, and prop info
    """
    game_id = request.args.get('game_id')

    result = GameService.get_all_picks_from_game(game_id)

    return jsonify(result)