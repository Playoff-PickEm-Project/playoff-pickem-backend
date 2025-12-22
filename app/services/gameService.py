from flask import abort
from app import db
from app.models.gameModel import Game
from app.models.propAnswers.variableOptionAnswer import VariableOptionAnswer
from app.models.props.overUnderProp import OverUnderProp
from app.models.props.winnerLoserProp import WinnerLoserProp
from app.models.propAnswers.winnerLoserAnswer import WinnerLoserAnswer
from app.models.propAnswers.overUnderAnswer import OverUnderAnswer
from app.models.props.hashMapAnswers import HashMapAnswers
from app.models.props.variableOptionProp import VariableOptionProp
from app.repositories.leagueRepository import get_league_by_name
from app.repositories.gameRepository import get_game_by_id
from app.repositories.playerRepository import get_player_by_username_and_leaguename, get_player_by_id
from app.repositories.propRepository import get_variable_option_answers_for_prop, get_variable_option_prop_by_id, get_winner_loser_prop_by_id, get_over_under_prop_by_id, get_over_under_answers_for_prop, get_winner_loser_answers_for_prop

# Method to save answers for a game (overall). Uses helper functions to answer each specific type of prop, by iterating through each of the 
# props in the game.
def answer_game(leagueName, username, game_id, answer):
    game = get_game_by_id(game_id)
    
    if (game is None):
        abort(401, "Game was not found.")
    
    for winnerLoserProp in game.winner_loser_props:
        answer_winner_loser_prop(leagueName, username, winnerLoserProp.id, answer)
    
    for overUnderProp in game.over_under_props:
        answer_over_under_prop(leagueName, username, overUnderProp.id, answer)
        
    for variableOptionProp in game.variable_option_props:
        answer_variable_option_prop(leagueName, username, variableOptionProp.id, answer)
        
    return {"Message": "Game answered by player successfully."}

# Method to allow for a player to save their answers for a specific prop. (Winner/Loser Prop)
def answer_winner_loser_prop(leagueName, username, prop_id, answer):
    player = get_player_by_username_and_leaguename(username, leagueName)
    
    if player is None:
        abort(401, "Player not found")
    
    # Check if the player has already answered this prop_id
    existing_answer = WinnerLoserAnswer.query.filter_by(prop_id=prop_id, player_id=player.id).first()
    
    if existing_answer:
        # If the player has already answered, update the existing answer
        existing_answer.answer = answer
        db.session.commit()
        return {"Message": "Winner/Loser prop answer updated successfully."}
    else:
        # If the player hasn't answered yet, create a new answer
        new_answer = WinnerLoserAnswer(
            answer=answer,
            prop_id=prop_id,
            player_id=player.id
        )
        db.session.add(new_answer)
        db.session.commit()

        player.player_winner_loser_answers.append(new_answer)
        db.session.commit()

        return {"Message": "Winner/Loser prop successfully answered."}

# Method to allow for a player to save their answers for a specific prop. (Over/Under Prop)
def answer_over_under_prop(leagueName, username, prop_id, answer):
    player = get_player_by_username_and_leaguename(username, leagueName)
    
    if player is None:
        abort(401, "Player not found")
    
    # Check if the player has already answered this prop_id
    existing_answer = OverUnderAnswer.query.filter_by(prop_id=prop_id, player_id=player.id).first()
    
    if existing_answer:
        # If the player has already answered, update the existing answer
        existing_answer.answer = answer
        db.session.commit()
        return {"Message": "Over/Under prop answer updated successfully."}
    else:
        # If the player hasn't answered yet, create a new answer
        new_answer = OverUnderAnswer(
            answer=answer,
            prop_id=prop_id,
            player_id=player.id
        )
        db.session.add(new_answer)
        db.session.commit()

        player.player_over_under_answers.append(new_answer)
        db.session.commit()

        return {"Message": "Over/Under prop successfully answered."}

# Method to allow for a player to save their answers for a specific prop. (Variable # of options Prop)
def answer_variable_option_prop(leagueName, username, prop_id, answer):
    player = get_player_by_username_and_leaguename(username, leagueName)
    
    if player is None:
        abort(401, "Player not found")
    
    # Check if the player has already answered this prop_id
    existing_answer = VariableOptionAnswer.query.filter_by(prop_id=prop_id, player_id=player.id).first()
    print("HERE")
    
    if existing_answer:
        # If the player has already answered, update the existing answer
        existing_answer.answer = answer
        db.session.commit()
        return {"Message": "Over/Under prop answer updated successfully."}
    else:
        # If the player hasn't answered yet, create a new answer
        new_answer = VariableOptionAnswer(
            answer=answer,
            prop_id=prop_id,
            player_id=player.id
        )
        db.session.add(new_answer)
        db.session.commit()

        player.player_variable_option_answers.append(new_answer)
        db.session.commit()

        return {"Message": "Over/Under prop successfully answered."}

# This method is to create a game within a league.
def create_game(leagueName, gameName, date, winnerLoserQuestions, overUnderQuestions, variableOptionQuestions):
		# Get the league the request is being made from.
    league = get_league_by_name(leagueName)
    
    if (league is None):
        abort(401, "League not found")
    
    # Create a new game with the basic fields that we know must be true (based on arguments).
    new_game = Game(
        league_id = league.id,
        game_name = gameName,
        start_time = date,
        graded = 0
    )
    
    print(date)
    
    # Db.session.add adds the game into the database (note that we import the db from our __init__ file I believe). 
    # Db.session.commit() saves the changes I believe.
    db.session.add(new_game)
    db.session.commit()
    
    # Iterate through each type of question to create an individual prop for it.
    for winnerLoserProp in winnerLoserQuestions:
        createWinnerLoserQuestion(winnerLoserProp, new_game.id)
        
    for overUnderProp in overUnderQuestions:
        createOverUnderQuestion(overUnderProp, new_game.id)
        
    for variableOptionProp in variableOptionQuestions:
        createVariableOptionQuestion(variableOptionProp, new_game.id)
        
    league.league_games.append(new_game)
    
    db.session.commit()
        
    return {"message": "Created game successfully."}

# Method to create a variable option prop.
def createVariableOptionQuestion(variableOptionProp, game_id):
    game = get_game_by_id(game_id)
    
    # From the argument, retrieve the question and answer choices (a list of tuples basically; idk if that's exactly accurate tho).
    question = variableOptionProp.get("question")
    options = variableOptionProp.get("options")
    
    # Rest from here on out is pretty self explanatory. Just setting the fields based on the arg.
    new_prop = VariableOptionProp(
        game_id = game_id,
        question = question,
    )
    
    new_prop.options = []
    
    game.variable_option_props.append(new_prop)
    
    for option in options:
        print(option)
        new_choice = HashMapAnswers(
            answer_choice = option.get('choice_text'),
            answer_points = option.get('points')
        )
        db.session.add(new_choice)
        
        new_prop.options.append(new_choice)
    
    db.session.add(new_prop)

    db.session.commit()    
    return {"message": "Created prop successfully."}
    
# Method to create a winner loser prop. Similar to previous method.
def createWinnerLoserQuestion(winnerLoserProp, game_id):
    game = get_game_by_id(game_id)
    print(winnerLoserProp)

    question = winnerLoserProp.get("question")
    favoritePoints = winnerLoserProp.get("favoritePoints")
    underdogPoints = winnerLoserProp.get("underdogPoints")
    favoriteTeam = winnerLoserProp.get("favoriteTeam")
    underdogTeam = winnerLoserProp.get("underdogTeam")
    
    new_prop = WinnerLoserProp(
        game_id = game_id,
        question = question,
        favorite_points = favoritePoints,
        underdog_points = underdogPoints,
        favorite_team = favoriteTeam,
        underdog_team = underdogTeam
    )
    
    game.winner_loser_props.append(new_prop)
    
    db.session.add(new_prop)
    db.session.commit()
    
    return {"message": "Created winner/loser prop successfully."}
    
# Method to create over under question. Similar to previous method.
def createOverUnderQuestion(overUnderProp, game_id):
    game = get_game_by_id(game_id)
    
    question = overUnderProp.get("question")
    overPoints = overUnderProp.get("overPoints")
    underPoints = overUnderProp.get("underPoints")
    
    new_prop = OverUnderProp(
        game_id = game_id,
        question = question,
        over_points = overPoints,
        under_points = underPoints
    )
    
    game.over_under_props.append(new_prop)
    
    db.session.add(new_prop)
    db.session.commit()
    
    return {"message": "Created over/under prop successfully."}

# Method to view all of the games within a league.
def view_games_in_league(leagueName):
    league = get_league_by_name(leagueName)
    
    return [game.to_dict() for game in league.league_games]

# Method to grade a game. I will not write a full comment out for this because we need to clean this up, including the regrading part.
def grade_game(game_id):
    game = get_game_by_id(game_id)
        
    if (game is None):
        abort(401, "Game not found.")
        
    # if game.graded != 0:
    #     for prop in game.winner_loser_props:
    #         # Get all the answers for the current prop (for all players)
    #         answers = get_winner_loser_answers_for_prop(prop.id)
            
    #         # Iterate through each answer to grade it
    #         for answer in answers:
    #             player = get_player_by_id(answer.player_id)  # Get the player who submitted the answer
                
    #             # Check if the player's answer matches the correct answer
    #             if answer.answer == prop.correct_answer:
    #                 # If the answer is correct, assign the appropriate points
    #                 if answer.answer == prop.favorite_team:
    #                     player.points -= prop.favorite_points  # Add favorite points
    #                 elif answer.answer == prop.underdog_team:
    #                     player.points -= prop.underdog_points
                        
    # if game.graded != 0:
    #     for prop in game.over_under_props:
    #         answers = get_over_under_answers_for_prop(prop.id)
            
    #         for answer in answers:
    #             player = get_player_by_id(answer.player_id)
                
    #             # IDK WHY LOWERCASE BUT KEEP AN EYE ON
    #             if answer.answer == prop.correct_answer:
    #                 if answer.answer == "over":
    #                     player.points -= prop.over_points
    #                 elif answer.answer == "under":
    #                     player.points -= prop.under_points
    
    # Iterate through the winner_loser_props of the game
    for prop in game.winner_loser_props:
        # Get all the answers for the current prop (for all players)
        answers = get_winner_loser_answers_for_prop(prop.id)
        
        # Iterate through each answer to grade it
        for answer in answers:
            player = get_player_by_id(answer.player_id)  # Get the player who submitted the answer
            print("REGRADING NEW CORRECT ANSWER", prop.correct_answer)
            print("ANSWER.ANSWER", answer.answer)
            
            # Check if the player's answer matches the correct answer
            if player is not None and answer.answer == prop.correct_answer:
                print("HERE")
                # If the answer is correct, assign the appropriate points
                if answer.answer == prop.favorite_team:
                    print("Before: ", player.points)
                    player.points += prop.favorite_points  # Add favorite points
                    print("After: ", player.points)
                elif answer.answer == prop.underdog_team:
                    print("Before: ", player.points)
                    player.points += prop.underdog_points  # Add underdog points
                    print("After: ", player.points)
                                    
    for prop in game.over_under_props:
        answers = get_over_under_answers_for_prop(prop.id)
        
        for answer in answers:
            player = get_player_by_id(answer.player_id)
            print(answer.answer)
            
            # IDK WHY LOWERCASE BUT KEEP AN EYE ON
            if player is not None and answer.answer == prop.correct_answer:
                if answer.answer == "over":
                    player.points += prop.over_points
                elif answer.answer == "under":
                    player.points += prop.under_points
                    
    for prop in game.variable_option_props:
        answers = get_variable_option_answers_for_prop(prop.id)
        
        for answer in answers:
            player = get_player_by_id(answer.player_id)
            
            for correct in prop.correct_answer:
                if player is not None and answer.answer == correct:
                    points_to_add = 0
                    
                    for option in prop.options:
                        if answer.answer == option.answer_choice:
                            points_to_add = option.answer_points
                    
                    print(points_to_add)
                    player.points += points_to_add
                    
    game.graded = 1
    
    db.session.commit()

# Method intended to set the correct answers for variable option prop. Again, need to do more testing with this, won't comment.
def set_correct_variable_option_prop(leaguename, prop_id, ans):
    p = get_variable_option_prop_by_id(prop_id)
    print(prop_id)
    
    if (p is None):
        abort(401, "Prop not found")
    
    game = Game.query.filter_by(id=p.game_id).first()
    
    if (game is None):
        abort(401, "Game not found")
      
    # NOT SURE FIX LATER?????????  
    # if game.graded != 0:
    #     for prop in game.variable_option_props:
    #         answers = get_variable_option_answers_for_prop(prop.id)
            
    #         for answer in answers:
    #             pass
    
    print(ans)
    p.correct_answer = ans
    db.session.commit()
    
# Similar to previous method, for winner loser prop.
def set_correct_winner_loser_prop(leaguename, prop_id, ans):        
    p = get_winner_loser_prop_by_id(prop_id)
    
    game = Game.query.filter_by(id=p.game_id).first()
    if (game is None):
        abort(401, "Game not found")

    if (p is None):
        abort(401, "Prop not found")
        
    if game.graded != 0:
        for prop in game.winner_loser_props:
            # Get all the answers for the current prop (for all players)
            answers = get_winner_loser_answers_for_prop(prop.id)
            
            # Iterate through each answer to grade it
            for answer in answers:
                player = get_player_by_id(answer.player_id)  # Get the player who submitted the answer
                
                # Check if the player's answer matches the correct answer
                if answer.answer == prop.correct_answer:
                    print(prop.correct_answer)
                    # If the answer is correct, assign the appropriate points
                    if answer.answer == prop.favorite_team:
                        player.points -= prop.favorite_points  # Add favorite points
                    elif answer.answer == prop.underdog_team:
                        player.points -= prop.underdog_points
    
    p.correct_answer = ans
    db.session.commit()

# Similar to previous method, for over under prop.
def set_correct_over_under_prop(leaguename, prop_id, ans):
    p = get_over_under_prop_by_id(prop_id)
    
    game = Game.query.filter_by(id=p.game_id).first()
    print(game.graded)
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

    if (p is None):
        abort(401, "Prop not found")

    print("ANSWER: ", ans)
    p.correct_answer = ans
    db.session.commit()
    print("prop answer: ", p.correct_answer)

# Method to get all of games within a league.
### Note: I AM NOW REALIZING THIS IS A DUPLICATE METHOD. FIND WHERE THIS IS USED AND REPLACE WITH ORIGINAL THEN DELETE.
def get_games_from_league(leaguename):
    league = get_league_by_name(leaguename)

    if league is None:
        abort(401, "League not found")
        
    return [game.to_dict() for game in league.league_games]

# Method to get all of the answers for a game.
def get_all_picks_from_game(game_id):
    # Fetch the game object using the provided game_id
    game = get_game_by_id(game_id)

    picks = []

    # Loop through all winner-loser props and get answers for each one
    for prop in game.winner_loser_props:
        answers = get_winner_loser_answers_for_prop(prop.id)

        # Iterate through the answers and associate each player's name with their answer
        for answer in answers:
            player = get_player_by_id(answer.player_id)
            if player is not None:
                picks.append({
                    "player_name": player.name,  # Assuming the answer has a player_name attribute
                    "answer": answer.answer,            # Assuming the answer has an answer attribute (could be 'favorite' or 'underdog')
                    "prop_id": prop.id,                  # Optionally, you can include the prop_id to track which prop the answer belongs to
                    "correct_answer": prop.correct_answer,
                    "question": prop.question
                })
    
    # Loop through all over-under props and get answers for each one
    for prop in game.over_under_props:
        answers = get_over_under_answers_for_prop(prop.id)

        # Iterate through the answers and associate each player's name with their answer
        for answer in answers:
            player = get_player_by_id(answer.player_id)
            if player is not None:
                picks.append({
                    "player_name": player.name,  # Assuming the answer has a player_name attribute
                    "answer": answer.answer,            # Assuming the answer has an answer attribute (could be 'over' or 'under')
                    "prop_id": prop.id,                  # Optionally, you can include the prop_id to track which prop the answer belongs to
                    "correct_answer": prop.correct_answer,
                    "question": prop.question
                })
                
    # Loop through all over-under props and get answers for each one
    for prop in game.variable_option_props:
        answers = get_variable_option_answers_for_prop(prop.id)

        # Iterate through the answers and associate each player's name with their answer
        for answer in answers:
            player = get_player_by_id(answer.player_id)
            if player is not None:
                picks.append({
                    "player_name": player.name,  # Assuming the answer has a player_name attribute
                    "answer": answer.answer,            # Assuming the answer has an answer attribute (could be 'over' or 'under')
                    "prop_id": prop.id,                  # Optionally, you can include the prop_id to track which prop the answer belongs to
                    "correct_answer": prop.correct_answer,
                    "question": prop.question
                })

    # Return the list of all picks (player names and their answers)
    return picks