from flask import jsonify, request, Blueprint
from app.services.propService import retrieve_over_under_answers, retrieve_winner_loser_answers
from app.services.gameService import set_correct_winner_loser_prop, set_correct_over_under_prop

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