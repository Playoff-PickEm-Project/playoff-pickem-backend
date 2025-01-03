from flask import Blueprint, jsonify, request
from app.services.leagueService import create_league, get_all_user_leagues, join_league

leagueController = Blueprint('leagueController', __name__)

@leagueController.route('/create_league', methods=['POST'])
def createLeague():
    data = request.get_json()
    leaguename = data.get('leagueName')
    username = data.get('username')
    playerName = data.get('playerName')
    
    result = create_league(leaguename, username, playerName)
    
    return jsonify(result)

@leagueController.route('/get_users_leagues', methods=['GET'])
def getUserLeagues():
    username = request.args.get('username')
    
    result = get_all_user_leagues(username)
    
    return jsonify(result)

@leagueController.route('/join_league', methods=['POST'])
def joinLeague():
    data = request.get_json()
    joinCode = data.get('joinCode')
    username = data.get('username')
    playerName = data.get('playerName')
    
    result = join_league(joinCode, username, playerName)
    
    return jsonify(result)