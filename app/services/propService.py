from flask import abort
from app import db
from app.repositories.leagueRepository import get_league_by_name
from app.repositories.playerRepository import get_player_by_id, get_player_by_username_and_leaguename
from app.repositories.gameRepository import get_game_by_id
from app.repositories.propRepository import get_all_variable_option_props_for_game, get_all_winner_loser_props_for_game, get_all_over_under_props_for_game, get_over_under_answers_for_prop, get_winner_loser_answers_for_prop, get_winner_loser_prop_by_id, get_over_under_prop_by_id

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

def retrieve_variable_option_answers(leaguename, username):
    league = get_league_by_name(leaguename)
    
    if (league is None):
        abort(401, "League was not found.")
        
    player = get_player_by_username_and_leaguename(username, leaguename)
    
    if (player is None):
        abort(401, "Player not found.")
        
    variable_option_answers = {}
    
    for answer in player.player_variable_option_answers:
        variable_option_answers[answer.prop_id] = answer.answer
        
    return variable_option_answers

def get_saved_correct_answers(game_id):
    game = get_game_by_id(game_id)

    if game is None:
        abort(401, "Game not found.")

    # Fetch props and correct answers
    winner_loser_props = get_all_winner_loser_props_for_game(game_id)
    over_under_props = get_all_over_under_props_for_game(game_id)
    variable_option_props = get_all_variable_option_props_for_game(game_id)
    
    result = []

    # For winner_loser_props
    if winner_loser_props:
        for prop in winner_loser_props:
            print(prop.correct_answer)
            result.append({'prop_id': prop.id, 'correct_answer': prop.correct_answer})

    # For over_under_props
    if over_under_props:
        for prop in over_under_props:
            print(prop.correct_answer)
            result.append({'prop_id': prop.id, 'correct_answer': prop.correct_answer})
            
    if variable_option_props:
        for prop in variable_option_props:
            print(prop.correct_answer)
            
            if prop.correct_answer:
                for answer in prop.correct_answer:
                    result.append({'prop_id': prop.id, 'correct_answer': answer})

    return result

def edit_winner_loser_prop(prop_id, question, favoritePoints, underdogPoints):
    prop = get_winner_loser_prop_by_id(prop_id)
    
    if (favoritePoints > underdogPoints):
        fav_team_tmp = prop.favorite_team
        prop.favorite_team = prop.underdog_team
        prop.underdog_team = fav_team_tmp
    
    prop.question = question
    prop.favorite_points = favoritePoints
    prop.underdog_points = underdogPoints
    
    db.session.commit()
    
def edit_over_under_prop(prop_id, question, overPoints, underPoints):
    prop = get_over_under_prop_by_id(prop_id)
    
    prop.question = question
    prop.over_points = overPoints
    prop.under_points = underPoints
    
    db.session.commit()
    
def correct_winner_loser_prop(prop_id, ans):
    p = get_winner_loser_prop_by_id(prop_id)
    game = get_game_by_id(p.game_id)
    if game.graded != 0:
        for prop in game.winner_loser_props:
            # Get all the answers for the current prop (for all players)
            answers = get_winner_loser_answers_for_prop(prop.id)
            
            # Iterate through each answer to grade it
            for answer in answers:
                player = get_player_by_id(answer.player_id)  # Get the player who submitted the answer
                
                # Check if the player's answer matches the correct answer
                if answer.answer == prop.correct_answer:
                    # If the answer is correct, assign the appropriate points
                    if answer.answer == prop.favorite_team:
                        player.points -= prop.favorite_points  # Add favorite points
                    elif answer.answer == prop.underdog_team:
                        player.points -= prop.underdog_points

    p.correct_answer = ans
    db.session.commit()
    
def correct_over_under_prop(prop_id, ans):
    p = get_over_under_prop_by_id(prop_id)
    game = get_game_by_id(p.game_id)
    db.session.refresh(game)
    
    if game.graded != 0:
        for prop in game.over_under_props:
            answers = get_over_under_answers_for_prop(prop.id)
            
            for answer in answers:
                player = get_player_by_id(answer.player_id)
                
                # IDK WHY LOWERCASE BUT KEEP AN EYE ON
                if answer.answer == prop.correct_answer:
                    if answer.answer == "over":
                        player.points -= prop.over_points
                    elif answer.answer == "under":
                        player.points -= prop.under_points
    
    p.correct_answer = ans
    try:
        db.session.commit()
    except Exception as e:
        print(f"Commit failed: {e}")
        db.session.rollback()