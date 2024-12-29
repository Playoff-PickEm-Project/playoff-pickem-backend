from flask import Blueprint, jsonify, request
from app.services.leagueService import create_league

leagueController = Blueprint('leagueController', __name__)

@leagueController.route('/create_league', methods=['POST'])
def createLeague():
    data = request.get_json()
    leaguename = data.get('leagueName')
    username = data.get('username')
    playerName = data.get('playerName')
    
    result = create_league(leaguename, username, playerName)
    
    return jsonify(result)