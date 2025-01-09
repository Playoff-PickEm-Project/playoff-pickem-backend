from flask import abort
from app import db
from app.models.gameModel import Game
from app.models.props.overUnderProp import OverUnderProp
from app.models.props.winnerLoserProp import WinnerLoserProp
from app.models.propAnswers.winnerLoserAnswer import WinnerLoserAnswer
from app.models.propAnswers.overUnderAnswer import OverUnderAnswer
from app.repositories.leagueRepository import get_league_by_name
from app.repositories.gameRepository import get_game_by_id
from app.repositories.playerRepository import get_player_by_username_and_leaguename

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
    
    new_answer = WinnerLoserAnswer(
        answer = answer,
        prop_id = prop_id,
        player_id = player.id
    )
    
    db.session.add(new_answer)
    db.session.commit()
    
    player.player_winner_loser_answers.append(new_answer)
    db.session.commit()
    
    return {"Message": "Winner/Loser prop successfully answered."}

# Method to allow for a player to save their answers for a specific game. (Over/Under Prop)
def answer_over_under_prop(leagueName, username, prop_id, answer):
    player = get_player_by_username_and_leaguename(username, leagueName)
    
    new_answer = OverUnderAnswer(
        answer = answer,
        prop_id = prop_id,
        player_id = player.id
    )
    
    db.session.add(new_answer)
    db.session.commit()
    
    player.player_over_under_answers.append(new_answer)
    db.session.commit()
    
    return {"Message": "Winner/Loser prop successfully answered."}


# This method is to create a game within a league.
def create_game(leagueName, gameName, date, winnerLoserQuestions, overUnderQuestions):
    league = get_league_by_name(leagueName)
    
    if (league is None):
        abort(401, "League not found")
    
    new_game = Game(
        league_id = league.id,
        game_name = gameName,
        start_time = date
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