from flask import jsonify, request, Blueprint
from app.services.propService import retrieve_over_under_answers, retrieve_variable_option_answers, retrieve_winner_loser_answers, get_saved_correct_answers, edit_over_under_prop, edit_winner_loser_prop, correct_over_under_prop, correct_winner_loser_prop
from app.services.gameService import set_correct_variable_option_prop, set_correct_winner_loser_prop, set_correct_over_under_prop
from app.services.playerService import edit_points

propController = Blueprint("propController", __name__)

@propController.route("/retrieve_winner_loser_answers", methods=['GET'])
def retrieveWinnerLoserAnswers():
    leaguename = request.args.get('leagueName')
    username = request.args.get('username')
    
    result = retrieve_winner_loser_answers(leaguename, username)
    
    return jsonify(result)

@propController.route("/retrieve_over_under_answers", methods=['GET'])
def retrieveOverUnderAnswers():
    leaguename = request.args.get('leagueName')
    username = request.args.get('username')
    
    result = retrieve_over_under_answers(leaguename, username)
    
    return jsonify(result)

@propController.route("/retrieve_variable_option_answers", methods=['GET'])
def retrieveVariableOptionAnswers():
    leaguename = request.args.get('leagueName')
    username = request.args.get('username')
    
    result = retrieve_variable_option_answers(leaguename, username)
    
    return jsonify(result)

@propController.route("/set_correct_winner_loser_prop", methods=['POST'])
def setCorrectWinnerLoserProp():
    data = request.get_json()
    
    # leaguename, prop_id, answer
    leaguename = data.get("leagueName")
    prop_id = data.get('prop_id')
    answer = data.get('answer')
    
    result = set_correct_winner_loser_prop(leaguename, prop_id, answer)
    
    return jsonify(result)

@propController.route("/set_correct_over_under_prop", methods=['POST'])
def setCorrectOverUnderProp():
    data = request.get_json()
    
    # leaguename, prop_id, answer
    leaguename = data.get("leagueName")
    prop_id = data.get('prop_id')
    answer = data.get('answer')
    
    result = set_correct_over_under_prop(leaguename, prop_id, answer)
    
    return jsonify(result)

@propController.route("/set_correct_variable_option_prop", methods=['POST'])
def setCorrectVariableOptionProp():
    data = request.get_json()
    
    # leaguename, prop_id, answer
    leaguename = data.get("leagueName")
    prop_id = data.get('prop_id')
    answer = data.get('answers')
    
    result = set_correct_variable_option_prop(leaguename, prop_id, answer)
    
    return jsonify(result)

@propController.route("/get_correct_prop_answers", methods=['GET'])
def getCorrectPropAnswers():
    game_id = request.args.get('game_id')
    
    result = get_saved_correct_answers(game_id)
    
    return jsonify(result)

@propController.route("/update_winner_loser_prop", methods=['POST'])
def updateWinnerLoserProp():
    data = request.get_json()
    
    #prop_id, question, favoritePoints, underdogPoints
    prop_id = data.get('prop_id')
    question = data.get('question')
    favoritePoints = data.get('favorite_points')
    underdogPoints = data.get('underdog_points')
    
    edit_winner_loser_prop(prop_id, question, favoritePoints, underdogPoints)
    
    return {"Message": "Successfully edited prop."}

@propController.route("/update_over_under_prop", methods=['POST'])
def updateOverUnderProp():
    data = request.get_json()
    
    #prop_id, question, favoritePoints, underdogPoints
    prop_id = data.get('prop_id')
    question = data.get('question')
    overPoints = data.get('over_points')
    underPoints = data.get('under_points')
    
    edit_over_under_prop(prop_id, question, overPoints, underPoints)
    
    return {"Message": "Successfully edited prop."}

@propController.route("/correct_winner_loser_prop", methods=['POST'])
def correctWinnerLoserProp():
    data = request.get_json()
    prop_id = data.get('prop_id')
    answer = data.get('answer')
    
    result = correct_winner_loser_prop(prop_id, answer)
    return jsonify(result)

@propController.route("/correct_over_under_prop", methods=['POST'])
def correctOverUnderProp():
    data = request.get_json()
    prop_id = data.get('prop_id')
    ans = data.get('answer')
    
    result = correct_over_under_prop(prop_id, ans)
    return jsonify(result)

@propController.route("/save_new_points", methods=['POST'])
def saveNewPoints():
    data = request.get_json()
    
    player_id = data.get('player_id')
    new_points = data.get('new_points')
    
    edit_points(player_id, new_points)
    
    return {"Message": "New points saved successfully."}