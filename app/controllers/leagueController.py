from flask import Blueprint, jsonify, request
from app.services.leagueService import LeagueService
from app.services.playerService import PlayerService
from app.services.game.gameService import GameService
from app.repositories.leagueRepository import get_league_by_name

"""
League Controller

Handles all league-related HTTP endpoints including league creation, deletion,
player management, game management, and retrieval of league information.
"""

leagueController = Blueprint('leagueController', __name__)

@leagueController.route('/create_league', methods=['POST'])
def createLeague():
    """
    Create a new league with the creator as the first player and commissioner.

    Expects JSON body with:
        - leagueName (str): The name for the new league
        - username (str): The username of the user creating the league
        - playerName (str): The player name for the creator in this league

    Returns:
        JSON: Success message if the league is created successfully
    """
    data = request.get_json()
    leaguename = data.get('leagueName')
    username = data.get('username')
    playerName = data.get('playerName')

    result = LeagueService.create_league(leaguename, username, playerName)

    return jsonify(result)

@leagueController.route('/get_users_leagues', methods=['GET'])
def getUserLeagues():
    """
    Retrieve all leagues that a user belongs to.

    Query Parameters:
        - username (str): The username to search for

    Returns:
        JSON: List of league objects
    """
    username = request.args.get('username')

    result = LeagueService.get_all_user_leagues(username)

    return jsonify(result)

@leagueController.route('/join_league', methods=['POST'])
def joinLeague():
    """
    Allow a user to join an existing league using a join code.

    Expects JSON body with:
        - joinCode (str): The unique join code for the league
        - username (str): The username of the user joining
        - playerName (str): The player name to use in this league

    Returns:
        JSON: Success message if the user joins successfully
    """
    data = request.get_json()
    joinCode = data.get('joinCode')
    username = data.get('username')
    playerName = data.get('playerName')

    result = LeagueService.join_league(joinCode, username, playerName)

    return jsonify(result)

@leagueController.route('/delete_player', methods=['POST'])
def deletePlayer():
    """
    Remove a player from a league.

    Expects JSON body with:
        - leaguename (str): The name of the league
        - playerName (str): The name of the player to remove

    Returns:
        JSON: Success message if the player is deleted successfully
    """
    data = request.get_json()

    leaguename = data.get('leaguename')
    playerName = data.get('playerName')

    result = LeagueService.delete_player(playerName, leaguename)

    return {"Message": "Player deleted successfully."}

@leagueController.route('/delete_league', methods=['POST'])
def deleteLeague():
    """
    Delete a league and all associated games and players.

    Expects JSON body with:
        - leagueName (str): The name of the league to delete

    Returns:
        JSON: Success message if the league is deleted successfully
    """
    data = request.get_json()
    leaguename = data.get('leagueName')

    result = LeagueService.delete_league(leaguename)

    return jsonify(result)


@leagueController.route('/get_player_standings', methods=['GET'])
def getPlayerStandings():
    """
    Retrieve player standings for a specific league.

    Query Parameters:
        - leagueName (str): The name of the league

    Returns:
        JSON: League information including all players and their standings
    """
    leaguename = request.args.get('leagueName')

    result = PlayerService.get_player_standings(leaguename)

    return jsonify(result)

@leagueController.route('/create_game', methods=['POST'])
def createGame():
    """
    Create a new game within a league with multiple prop types.

    Expects JSON body with:
        - leagueName (str): The name of the league to create the game in
        - gameName (str): The name of the game
        - date (str): The start time/date for the game
        - winnerLoserQuestions (list): List of winner/loser prop data
        - overUnderQuestions (list): List of over/under prop data
        - variableOptionQuestions (list): List of variable option prop data

    Returns:
        JSON: Success message if the game is created successfully
    """
    data = request.get_json()
    leagueName = data.get('leagueName')
    gameName = data.get('gameName')
    date = data.get('date')
    winnerLoserQuestions = data.get('winnerLoserQuestions')
    overUnderQuestions = data.get('overUnderQuestions')
    variableOptionQuestions = data.get('variableOptionQuestions')

    result = GameService.create_game(leagueName, gameName, date, winnerLoserQuestions, overUnderQuestions, variableOptionQuestions)

    return jsonify(result)

@leagueController.route('/get_games', methods=['GET'])
def viewGamesInLeague():
    """
    Retrieve all games within a specific league.

    Query Parameters:
        - leagueName (str): The name of the league

    Returns:
        JSON: List of game objects
    """
    leaguename = request.args.get('leagueName')

    result = GameService.view_games_in_league(leaguename)

    return jsonify(result)

@leagueController.route('/get_league_by_name', methods=['GET'])
def getLeagueByName():
    """
    Retrieve a league by its name.

    Query Parameters:
        - leagueName (str): The name of the league to look up

    Returns:
        JSON: League object as dictionary
    """
    leaguename = request.args.get('leagueName')

    result = get_league_by_name(leaguename)

    if result is None:
        return {"Message": "idk"}

    return jsonify(result.to_dict())