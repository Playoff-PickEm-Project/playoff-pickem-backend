from flask import abort
from app.models.playerModel import Player
from app.repositories.playerRepository import get_all_players, get_player_by_id, get_player_by_username_and_leaguename
from app.repositories.leagueRepository import get_league_by_name
from app.repositories.usersRepository import get_user_by_username
from app import db

# Method to create a player in the database, and set its fields corresponding to the league it is in.
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
        user_id = user.id,
        points = 0,
    )
    
    new_player.league_id = league.id
    new_player.league = league
    
    
    return new_player

# Method to retrieve player standings? Not too sure why this is the way it is tbh. figure out later
def get_player_standings(leagueName):
    league = get_league_by_name(leagueName)
        
    return league.to_dict()
    
# Method to edit the points of a specific player.
def edit_points(player_id, new_points):
    player = get_player_by_id(player_id)
    
    player.points = new_points
    
    db.session.commit()