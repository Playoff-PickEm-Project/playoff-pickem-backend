from flask import abort
from app import db
from app.models.gameModel import Game
from app.models.props.overUnderProp import OverUnderProp
from app.models.props.winnerLoserProp import WinnerLoserProp
from app.models.propAnswers.winnerLoserAnswer import WinnerLoserAnswer
from app.models.propAnswers.overUnderAnswer import OverUnderAnswer
from app.repositories.leagueRepository import get_league_by_name
from app.repositories.gameRepository import get_game_by_id
from app.repositories.playerRepository import get_player_by_username_and_leaguename, get_player_by_id
from app.repositories.propRepository import get_winner_loser_prop_by_id, get_over_under_prop_by_id, get_over_under_answers_for_prop, get_winner_loser_answers_for_prop

# Method to save answers for a game (overall)
def answer_game(leagueName, username, game_id, answer):
    game = get_game_by_id(game_id)
    
    if (game is None):
        abort(401, "Game was not found.")
    
    for winnerLoserProp in game.winner_loser_props:
        answer_winner_loser_prop(leagueName, username, winnerLoserProp.id, answer)
    
    for overUnderProp in game.over_under_props:
        answer_over_under_prop(leagueName, username, overUnderProp.id, answer)
        
    return {"Message": "Game answered by player successfully."}

# Method to allow for a player to save their answers for a specific game. (Winner/Loser Prop)
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



# This method is to create a game within a league.
def create_game(leagueName, gameName, date, winnerLoserQuestions, overUnderQuestions):
    league = get_league_by_name(leagueName)
    
    if (league is None):
        abort(401, "League not found")
    
    new_game = Game(
        league_id = league.id,
        game_name = gameName,
        start_time = date,
        graded = 0
    )
    
    print(date)
    
    db.session.add(new_game)
    db.session.commit()
    
    for winnerLoserProp in winnerLoserQuestions:
        createWinnerLoserQuestion(winnerLoserProp, new_game.id)
        
    for overUnderProp in overUnderQuestions:
        createOverUnderQuestion(overUnderProp, new_game.id)
        
    league.league_games.append(new_game)
    
    db.session.commit()
        
    return {"message": "Created game successfully."}

def createWinnerLoserQuestion(winnerLoserProp, game_id):
    game = get_game_by_id(game_id)

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

def view_games_in_league(leagueName):
    league = get_league_by_name(leagueName)
    
    return [game.to_dict() for game in league.league_games]

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
                    
    game.graded = 1
    
    db.session.commit()
    
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
    
def get_games_from_league(leaguename):
    league = get_league_by_name(leaguename)

    if league is None:
        abort(401, "League not found")
        
    return [game.to_dict() for game in league.league_games]

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

    # Return the list of all picks (player names and their answers)
    return picks