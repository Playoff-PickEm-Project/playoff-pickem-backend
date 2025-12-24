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