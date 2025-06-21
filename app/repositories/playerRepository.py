from app.models.playerModel import Player
from app.repositories.usersRepository import get_user_by_username
from app.repositories.leagueRepository import get_league_by_name

# Query to get every single player.
def get_all_players():
    return Player.query.all()

# Query to get a player by its specific id.
def get_player_by_id(playerId):
    return Player.query.get(playerId)

# Query to get a player based on the league it is a part of (leagueName) and the user that the player is associated to (username).
def get_player_by_username_and_leaguename(username, leagueName):
    # Get the user and league we care about.
    user = get_user_by_username(username)
    league = get_league_by_name(leagueName)
    
    # Check that user and league exist.
    if user is None or league is None:
        return None
    
    return Player.query.filter(Player.user_id == user.id, Player.league_id == league.id).first()

# Query to get a player by a players name and the league they are in. Note that we cannot search by solely the players name, as that is
# not a unique field.
def get_player_by_playername_and_leaguename(playerName, leagueName):
    league = get_league_by_name(leagueName)
    for player in league.league_players:
        if player.name == playerName:
            return player
    
    return None