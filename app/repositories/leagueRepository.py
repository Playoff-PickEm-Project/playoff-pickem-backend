from app.models.leagueModel import League
from app.repositories.usersRepository import get_user_by_username

def get_all_leagues():
    return League.query.all()

def get_league_by_name(leaguename):
    return League.query.filter_by(league_name=leaguename).first()

def get_leagues_by_username(username):
    # Get the user and league we care about.
    user = get_user_by_username(username)
    
    # Check that user and league exist.
    if user is None:
        return None
    
    players = user.user_players
    
    leagues = set()
    
    for player in players:
        if (player.league):
            leagues.add(player.league)
            
    return list(leagues)