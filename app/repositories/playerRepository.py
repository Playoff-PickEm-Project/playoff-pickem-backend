from app.models.playerModel import Player
from app.repositories.usersRepository import get_user_by_username
from app.repositories.leagueRepository import get_league_by_name

def get_all_players():
    return Player.query.all()

def get_player_by_id(playerId):
    return Player.query.get(playerId)

def get_player_by_username_and_leaguename(username, leagueName):
    # Get the user and league we care about.
    user = get_user_by_username(username)
    league = get_league_by_name(leagueName)
    
    # Check that user and league exist.
    if user is None or league is None:
        return None
    
    return Player.query.filter(Player.user_id == user.id, Player.league_id == league.id).first()

def get_player_by_playername_and_leaguename(playerName, leagueName):
    league = get_league_by_name(leagueName)
    for player in league.league_players:
        if player.name == playerName:
            return player
    
    return None