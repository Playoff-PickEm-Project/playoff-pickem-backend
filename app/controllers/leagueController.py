from flask import Blueprint, jsonify, request
from app.services.leagueService import create_league, get_all_user_leagues, join_league, delete_league, delete_player
from app.services.playerService import get_player_standings
from app.services.gameService import create_game, view_games_in_league
from app.repositories.leagueRepository import get_league_by_name

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

@leagueController.route('/delete_player', methods=['POST'])
def deletePlayer():
    data = request.get_json()
    
    leaguename = data.get('leaguename')
    playerName = data.get('playerName')
    
    result = delete_player(playerName, leaguename)
    
    return {"Message": "Player deleted successfully."}

@leagueController.route('/delete_league', methods=['POST'])
def deleteLeague():
    data = request.get_json()
    leaguename = data.get('leagueName')
    
    result = delete_league(leaguename)
    
    return jsonify(result)


@leagueController.route('/get_player_standings', methods=['GET'])
def getPlayerStandings():
    leaguename = request.args.get('leagueName')
    
    result = get_player_standings(leaguename)
    
    return jsonify(result)

@leagueController.route('/create_game', methods=['POST'])
def createGame():
    data = request.get_json()
    leagueName = data.get('leagueName')
    gameName = data.get('gameName')
    date = data.get('date')
    winnerLoserQuestions = data.get('winnerLoserQuestions')
    overUnderQuestions = data.get('overUnderQuestions')
    variableOptionQuestions = data.get('variableOptionQuestions')
        
    result = create_game(leagueName, gameName, date, winnerLoserQuestions, overUnderQuestions, variableOptionQuestions)
    
    return jsonify(result)

@leagueController.route('/get_games', methods=['GET'])
def viewGamesInLeague():
    leaguename = request.args.get('leagueName')
    
    result = view_games_in_league(leaguename)
    
    return jsonify(result)

@leagueController.route('/get_league_by_name', methods=['GET'])
def getLeagueByName():
    leaguename = request.args.get('leagueName')
    
    result = get_league_by_name(leaguename)
    
    if result is None:
        return {"Message": "idk"}
    
    return jsonify(result.to_dict())