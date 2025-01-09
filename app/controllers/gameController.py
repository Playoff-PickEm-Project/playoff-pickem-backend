from flask import Blueprint, jsonify, request
from app.services.gameService import answer_over_under_prop, answer_winner_loser_prop, answer_game

gameController = Blueprint('gameController', __name__)

@gameController.route('/answer_winner_loser_prop', methods=['POST'])
def answerWinnerLoserProp():
    data = request.get_json()
    
    leagueName = data.get('leagueName')
    username = data.get('username')
    prop_id = data.get('prop_id')
    answer = data.get('answer')
    
    result = answer_winner_loser_prop(leagueName, username, prop_id, answer)
    
    return jsonify(result)

@gameController.route('/answer_over_under_prop', methods=['POST'])
def answerOverUnderProp():
    data = request.get_json()
    
    leagueName = data.get('leagueName')
    username = data.get('username')
    prop_id = data.get('prop_id')
    answer = data.get('answer')
    
    result = answer_over_under_prop(leagueName, username, prop_id, answer)
    
    return jsonify(result)

@gameController.route('/answer_game', methods=['POST'])
def answerGame():
    data = request.get_json()
    
    leagueName = data.get('leagueName')
    username = data.get('username')
    game_id = data.get('game_id')
    answer = data.get('answer')
    
    result = answer_game(leagueName, username, game_id, answer)
    
    return jsonify(result)