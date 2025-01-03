from flask import abort
from app import db
from app.models.leagueModel import League
from app.repositories.leagueRepository import get_all_leagues, get_league_by_name, get_leagues_by_username, get_league_by_join_code
from app.services.playerService import create_player
import secrets
import string

# Generating a random string of size 30, to act as a join code for the league.
def generate_join_code(length=30):
    # Can include uppercase, lowercase, and numbers
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))

def create_league(leagueName, username, playerName):
    league = get_league_by_name(leagueName)
    
    if (league is not None):
        print("name taken")
        abort(401, "League name already exists. Choose another league name.") 

    try:
        newLeague = League(
            league_name = leagueName,
            join_code = generate_join_code(),
        )
        
        db.session.add(newLeague)
        db.session.commit()
                
        first_player = create_player(playerName, username, leagueName)
        
        # This line might be unnecessary.
        newLeague.commissioner_id = first_player.id
        newLeague.commissioner = first_player
        
        db.session.commit()
        
        newLeague.league_players.append(first_player)
                
        db.session.add(first_player)
        db.session.commit()
                
        return {"message": "Successfully added league."}
        
    except Exception as error:
        print(f"Error: {error}")
        abort(401, "Error creating league. Please try again.")
        
def get_all_user_leagues(username):
    leagues = get_leagues_by_username(username)
    print(leagues)
    return [league.to_dict() for league in leagues]

def join_league(joinCode, username, playerName):
    league = get_league_by_join_code(joinCode)
    
    if (league is None):
        abort(401, "League not found")
    
    leagueName = league.league_name
    
    try:
        new_player = create_player(playerName, username, leagueName)
        
        league.league_players.append(new_player)
        db.session.add(new_player)
        db.session.commit()
        return {"message": "Successfully joined league."}
    except Exception as error:
        print(f"Error: {error}")