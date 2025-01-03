from flask import abort
from app.models.playerModel import Player
from app.repositories.playerRepository import get_all_players, get_player_by_id, get_player_by_username_and_leaguename
from app.repositories.leagueRepository import get_league_by_name
from app.repositories.usersRepository import get_user_by_username
from app import db

def create_player(playerName, username, leaguename):
    league = get_league_by_name(leaguename)
    
    if (leaguename is None):
        abort(401, "League not found")
        
    user = get_user_by_username(username)
    
    if (user is None):
        abort(401, "User not found")
        
    for player in league.league_players:
        if (player.name is playerName):
            abort(401, "Already exists someone in the league with this player name. Choose another player name")
            
    new_player = Player(
        name = playerName,
        user_id = user.id
    )
    
    new_player.league_id = league.id
    new_player.league = league
    
    return new_player
    