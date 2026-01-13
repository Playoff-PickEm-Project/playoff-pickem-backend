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
    Edit a winner/loser prop's question, point values, and team names.

    Expects JSON body with:
        - prop_id (int): The ID of the prop to edit
        - question (str): The new question text
        - favorite_points (int): Points for picking the favorite
        - underdog_points (int): Points for picking the underdog
        - favorite_team (str, optional): The favorite team name
        - underdog_team (str, optional): The underdog team name

    Returns:
        JSON: Success message
    """
    data = request.get_json()

    prop_id = data.get('prop_id')
    question = data.get('question')
    favoritePoints = data.get('favorite_points')
    underdogPoints = data.get('underdog_points')
    favorite_team = data.get('favorite_team')
    underdog_team = data.get('underdog_team')

    PropService.edit_winner_loser_prop(prop_id, question, favoritePoints, underdogPoints, favorite_team, underdog_team)

    return {"Message": "Successfully edited prop."}

@propController.route("/update_over_under_prop", methods=['POST'])
def updateOverUnderProp():
    """
    Edit an over/under prop's question, point values, and player information.

    Expects JSON body with:
        - prop_id (int): The ID of the prop to edit
        - question (str): The new question text
        - over_points (int): Points for picking over
        - under_points (int): Points for picking under
        - player_name (str, optional): The player's name for ESPN tracking
        - player_id (str, optional): The ESPN player ID
        - stat_type (str, optional): The stat type (e.g., "passing_yards")
        - line_value (float, optional): The over/under line value

    Returns:
        JSON: Success message
    """
    data = request.get_json()

    prop_id = data.get('prop_id')
    question = data.get('question')
    overPoints = data.get('over_points')
    underPoints = data.get('under_points')
    player_name = data.get('player_name')
    player_id = data.get('player_id')
    stat_type = data.get('stat_type')
    line_value = data.get('line_value')

    PropService.edit_over_under_prop(prop_id, question, overPoints, underPoints, player_name, player_id, stat_type, line_value)

    return {"Message": "Successfully edited prop."}

@propController.route("/update_variable_option_prop", methods=['POST'])
def updateVariableOptionProp():
    """
    Edit a variable option prop's question and options.

    Expects JSON body with:
        - prop_id (int): The ID of the prop to edit
        - question (str): The new question text
        - options (list): List of options with 'answer_choice' and 'answer_points'

    Returns:
        JSON: Success message
    """
    data = request.get_json()

    prop_id = data.get('prop_id')
    question = data.get('question')
    options = data.get('options')

    PropService.edit_variable_option_prop(prop_id, question, options)

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

@propController.route("/get_player_selected_props", methods=['GET'])
def get_player_selected_props():
    """
    Get all props a player has selected to answer for a specific game.

    Query Parameters:
        - player_id (int): The player's ID
        - game_id (int): The game's ID

    Returns:
        JSON: List of selected props with their details
    """
    player_id = request.args.get('player_id', type=int)
    game_id = request.args.get('game_id', type=int)

    selections = PropService.get_player_selected_props(player_id, game_id)

    return jsonify([selection.to_dict() for selection in selections])

@propController.route("/select_prop", methods=['POST'])
def select_prop():
    """
    Allow a player to select a prop they want to answer for a game.

    Request Body:
        - player_id (int): The player's ID
        - game_id (int): The game's ID
        - prop_type (str): 'winner_loser', 'over_under', or 'variable_option'
        - prop_id (int): The prop's ID

    Returns:
        JSON: The created selection object
    """
    try:
        data = request.get_json()

        player_id = data.get('player_id')
        game_id = data.get('game_id')
        prop_type = data.get('prop_type')
        prop_id = data.get('prop_id')

        print(f"DEBUG: Selecting prop - player_id={player_id}, game_id={game_id}, prop_type={prop_type}, prop_id={prop_id}")

        selection = PropService.select_prop_for_player(player_id, game_id, prop_type, prop_id)

        return jsonify({
            "message": "Prop selected successfully",
            "selection": selection.to_dict()
        }), 201
    except Exception as e:
        print(f"ERROR in select_prop: {str(e)}")
        return jsonify({"description": str(e)}), 400

@propController.route("/deselect_prop/<int:selection_id>", methods=['DELETE'])
def deselect_prop(selection_id):
    """
    Allow a player to deselect a prop they previously selected.

    Path Parameters:
        - selection_id (int): The PlayerPropSelection ID

    Request Body:
        - player_id (int): The player's ID (for authorization)

    Returns:
        JSON: Success message
    """
    data = request.get_json()
    player_id = data.get('player_id')

    PropService.deselect_prop_for_player(selection_id, player_id)

    return jsonify({"message": "Prop deselected successfully"}), 200

@propController.route("/reset_player_selections", methods=['POST'])
def reset_player_selections():
    """
    Remove all prop selections for a player for a specific game.

    Request Body:
        - player_id (int): The player's ID
        - game_id (int): The game's ID

    Returns:
        JSON: Success message
    """
    data = request.get_json()

    player_id = data.get('player_id')
    game_id = data.get('game_id')

    PropService.reset_player_selections_for_game(player_id, game_id)

    return jsonify({"message": "All prop selections reset successfully"}), 200