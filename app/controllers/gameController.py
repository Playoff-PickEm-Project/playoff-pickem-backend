from flask import Blueprint, jsonify, request
from app.services.gameService import answer_over_under_prop, answer_winner_loser_prop, answer_game, grade_game, get_games_from_league
from app.repositories.gameRepository import get_game_by_id

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

@gameController.route('/get_game_by_id', methods=['GET'])
def getGameByID():
    game_id = request.args.get('game_id')
    
    game = get_game_by_id(game_id)
    
    return jsonify(game.to_dict())

@gameController.route('/grade_game', methods=['POST'])
def gradeGame():
    data = request.get_json()
    game_id = data.get('game_id')
    
    result = grade_game(game_id)
    
    return jsonify(result)

@gameController.route('/get_games_in_league', methods=['GET'])
def getGamesFromLeague():
    leaguename = request.args.get('leagueName')
    
    result = get_games_from_league(leaguename)
    
    return jsonify(result)