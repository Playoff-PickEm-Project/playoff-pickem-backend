from flask import abort
from app import db
from app.models.gameModel import Game
from app.models.props.overUnderProp import OverUnderProp
from app.models.props.winnerLoserProp import WinnerLoserProp
from app.repositories.leagueRepository import get_league_by_name
from app.repositories.gameRepository import get_game_by_id

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
    
    new_prop = WinnerLoserProp(
        game_id = game_id,
        question = question,
        favorite_points = favoritePoints,
        underdog_points = underdogPoints
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