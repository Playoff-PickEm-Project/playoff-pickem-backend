from app.models.leagueModel import League
from app.repositories.usersRepository import get_user_by_username

# Query to get a league by its id.
def get_league_by_id(id):
    return League.query.get(id)

# Query to return all leagues.
def get_all_leagues():
    return League.query.all()

# Query to get a league based on its league name. Note that this works because league names must be unique.
def get_league_by_name(leaguename):
    return League.query.filter_by(league_name=leaguename).first()

# Query to get the leagues that a user is a part of. Starts by identifying the user, identifying all of the players the 
# user has, and accessing each league through that.
def get_leagues_by_username(username):
    # Get the user and league we care about.
    user = get_user_by_username(username)
    
    # Check that user and league exist.
    if user is None:
        return None
    
    players = user.user_players
        
    leagues = set()
    
    for player in players:
        l = get_league_by_id(player.league_id)
        if (l):
            leagues.add(l)
            
    return list(leagues)

def get_league_by_join_code(joinCode):
    return League.query.filter_by(join_code=joinCode).first()