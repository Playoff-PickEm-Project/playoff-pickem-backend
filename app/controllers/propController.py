from flask import jsonify, request, Blueprint
from app.services.propService import PropService
from app.services.game.gradeGameService import GradeGameService
from app.services.playerService import PlayerService

"""
Prop Controller

Handles all proposition-related HTTP endpoints including retrieving player answers,
setting correct answers for grading/regrading, editing props, and updating player points.
"""

propController = Blueprint("propController", __name__)

@propController.route("/retrieve_winner_loser_answers", methods=['GET'])
def retrieveWinnerLoserAnswers():
    """
    Retrieve a player's winner/loser prop answers.

    Query Parameters:
        - leagueName (str): The name of the league
        - username (str): The username of the player

    Returns:
        JSON: Dictionary mapping prop_id to player's answer
    """
    leaguename = request.args.get('leagueName')
    username = request.args.get('username')

    result = PropService.retrieve_winner_loser_answers(leaguename, username)

    return jsonify(result)

@propController.route("/retrieve_over_under_answers", methods=['GET'])
def retrieveOverUnderAnswers():
    """
    Retrieve a player's over/under prop answers.

    Query Parameters:
        - leagueName (str): The name of the league
        - username (str): The username of the player

    Returns:
        JSON: Dictionary mapping prop_id to player's answer
    """
    leaguename = request.args.get('leagueName')
    username = request.args.get('username')

    result = PropService.retrieve_over_under_answers(leaguename, username)

    return jsonify(result)

@propController.route("/retrieve_variable_option_answers", methods=['GET'])
def retrieveVariableOptionAnswers():
    """
    Retrieve a player's variable option prop answers.

    Query Parameters:
        - leagueName (str): The name of the league
        - username (str): The username of the player

    Returns:
        JSON: Dictionary mapping prop_id to player's answer
    """
    leaguename = request.args.get('leagueName')
    username = request.args.get('username')

    result = PropService.retrieve_variable_option_answers(leaguename, username)

    return jsonify(result)

@propController.route("/set_correct_winner_loser_prop", methods=['POST'])
def setCorrectWinnerLoserProp():
    """
    Set the correct answer for a winner/loser prop (with regrading if needed).

    Expects JSON body with:
        - leagueName (str): The name of the league
        - prop_id (int): The ID of the winner/loser prop
        - answer (str): The correct answer (team name)

    Returns:
        JSON: Success response
    """
    data = request.get_json()

    leaguename = data.get("leagueName")
    prop_id = data.get('prop_id')
    answer = data.get('answer')

    result = GradeGameService.set_correct_winner_loser_prop(leaguename, prop_id, answer)

    return jsonify(result)

@propController.route("/set_correct_over_under_prop", methods=['POST'])
def setCorrectOverUnderProp():
    """
    Set the correct answer for an over/under prop (with regrading if needed).

    Expects JSON body with:
        - leagueName (str): The name of the league
        - prop_id (int): The ID of the over/under prop
        - answer (str): The correct answer ("over" or "under")

    Returns:
        JSON: Success response
    """
    data = request.get_json()

    leaguename = data.get("leagueName")
    prop_id = data.get('prop_id')
    answer = data.get('answer')

    result = GradeGameService.set_correct_over_under_prop(leaguename, prop_id, answer)

    return jsonify(result)

@propController.route("/set_correct_variable_option_prop", methods=['POST'])
def setCorrectVariableOptionProp():
    """
    Set the correct answer(s) for a variable option prop (with regrading if needed).

    Expects JSON body with:
        - leagueName (str): The name of the league
        - prop_id (int): The ID of the variable option prop
        - answers (list): List of correct answer choices

    Returns:
        JSON: Success response
    """
    data = request.get_json()

    leaguename = data.get("leagueName")
    prop_id = data.get('prop_id')
    answer = data.get('answers')

    result = GradeGameService.set_correct_variable_option_prop(leaguename, prop_id, answer)

    return jsonify(result)

@propController.route("/get_correct_prop_answers", methods=['GET'])
def getCorrectPropAnswers():
    """
    Retrieve all saved correct answers for a game.

    Query Parameters:
        - game_id (int): The ID of the game

    Returns:
        JSON: List of prop_id and correct_answer for each prop
    """
    game_id = request.args.get('game_id')

    result = PropService.get_saved_correct_answers(game_id)

    return jsonify(result)

@propController.route("/update_winner_loser_prop", methods=['POST'])
def updateWinnerLoserProp():
    """
    Edit a winner/loser prop's question and point values.

    Expects JSON body with:
        - prop_id (int): The ID of the prop to edit
        - question (str): The new question text
        - favorite_points (int): Points for picking the favorite
        - underdog_points (int): Points for picking the underdog

    Returns:
        JSON: Success message
    """
    data = request.get_json()

    prop_id = data.get('prop_id')
    question = data.get('question')
    favoritePoints = data.get('favorite_points')
    underdogPoints = data.get('underdog_points')

    PropService.edit_winner_loser_prop(prop_id, question, favoritePoints, underdogPoints)

    return {"Message": "Successfully edited prop."}

@propController.route("/update_over_under_prop", methods=['POST'])
def updateOverUnderProp():
    """
    Edit an over/under prop's question and point values.

    Expects JSON body with:
        - prop_id (int): The ID of the prop to edit
        - question (str): The new question text
        - over_points (int): Points for picking over
        - under_points (int): Points for picking under

    Returns:
        JSON: Success message
    """
    data = request.get_json()

    prop_id = data.get('prop_id')
    question = data.get('question')
    overPoints = data.get('over_points')
    underPoints = data.get('under_points')

    PropService.edit_over_under_prop(prop_id, question, overPoints, underPoints)

    return {"Message": "Successfully edited prop."}

@propController.route("/save_new_points", methods=['POST'])
def saveNewPoints():
    """
    Update a player's point total (manual adjustment).

    Expects JSON body with:
        - player_id (int): The ID of the player
        - new_points (int/float): The new point total

    Returns:
        JSON: Success message
    """
    data = request.get_json()

    player_id = data.get('player_id')
    new_points = data.get('new_points')

    PlayerService.edit_points(player_id, new_points)

    return {"Message": "New points saved successfully."}