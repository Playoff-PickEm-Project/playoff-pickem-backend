from flask import abort
from app.repositories.leagueRepository import get_league_by_name
from app.repositories.playerRepository import get_player_by_username_and_leaguename
from app.repositories.gameRepository import get_game_by_id
from app.repositories.propRepository import get_all_winner_loser_props_for_game, get_all_over_under_props_for_game

# Retrieving a player's answers if they have already answered a game's form.
def retrieve_winner_loser_answers(leaguename, username):
    league = get_league_by_name(leaguename)
    
    if (league is None):
        abort(401, "League was not found.")
        
    player = get_player_by_username_and_leaguename(username, leaguename)
    
    if (player is None):
        abort(401, "Player not found.")
        
    winner_loser_answers = {}
        
    for answer in player.player_winner_loser_answers:
        winner_loser_answers[answer.prop_id] = answer.answer
        
    return winner_loser_answers
    
# Retrieving a player's answers if they have already answered a game's form.
def retrieve_over_under_answers(leaguename, username):
    league = get_league_by_name(leaguename)
    
    if (league is None):
        abort(401, "League was not found.")
        
    player = get_player_by_username_and_leaguename(username, leaguename)
    
    if (player is None):
        abort(401, "Player not found.")
        
    over_under_answers = {}
    
    for answer in player.player_over_under_answers:
        over_under_answers[answer.prop_id] = answer.answer
        
    return over_under_answers

def get_saved_correct_answers(game_id):
    game = get_game_by_id(game_id)

    if game is None:
        abort(401, "Game not found.")

    # Fetch props and correct answers
    winner_loser_props = get_all_winner_loser_props_for_game(game_id)
    over_under_props = get_all_over_under_props_for_game(game_id)
    
    result = []

    if winner_loser_props:
        result.extend({'prop_id': prop.id, 'correct_answer': prop.correct_answer} for prop in winner_loser_props)

    if over_under_props:
        result.extend({'prop_id': prop.id, 'correct_answer': prop.correct_answer} for prop in over_under_props)

    return result