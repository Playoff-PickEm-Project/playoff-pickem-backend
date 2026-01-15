from app.models.propAnswers.variableOptionAnswer import VariableOptionAnswer
from app.models.props.variableOptionProp import VariableOptionProp
from app.models.props.winnerLoserProp import WinnerLoserProp
from app.models.props.overUnderProp import OverUnderProp
from app.models.propAnswers.overUnderAnswer import OverUnderAnswer
from app.models.propAnswers.winnerLoserAnswer import WinnerLoserAnswer
from app.models.playerPropSelection import PlayerPropSelection
from app import db

def get_winner_loser_prop_by_id(id):
    return WinnerLoserProp.query.get(id)

def get_over_under_prop_by_id(id):
    return OverUnderProp.query.get(id)

def get_variable_option_prop_by_id(id):
    return VariableOptionProp.query.get(id)

def get_winner_loser_answers_for_prop(prop_id):
    return WinnerLoserAnswer.query.filter_by(prop_id=prop_id).all()

def get_over_under_answers_for_prop(prop_id):
    return OverUnderAnswer.query.filter_by(prop_id=prop_id).all()

def get_variable_option_answers_for_prop(prop_id):
    return VariableOptionAnswer.query.filter_by(prop_id=prop_id).all()

def get_all_winner_loser_props_for_game(game_id):
    return WinnerLoserProp.query.filter_by(game_id=game_id).all()
    
def get_all_over_under_props_for_game(game_id):
    return OverUnderProp.query.filter_by(game_id=game_id).all()

def get_all_variable_option_props_for_game(game_id):
    return VariableOptionProp.query.filter_by(game_id=game_id).all()

# PlayerPropSelection repository functions

def get_player_prop_selections_for_game(player_id, game_id):
    """Get all prop selections a player has made for a specific game"""
    return PlayerPropSelection.query.filter_by(player_id=player_id, game_id=game_id).all()

def get_player_prop_selection_count(player_id, game_id):
    """Get the count of props a player has selected for a game"""
    return PlayerPropSelection.query.filter_by(player_id=player_id, game_id=game_id).count()

def create_player_prop_selection(player_id, game_id, prop_type, prop_id):
    """Create a new prop selection for a player"""
    selection = PlayerPropSelection(
        player_id=player_id,
        game_id=game_id,
        prop_type=prop_type,
        prop_id=prop_id
    )
    db.session.add(selection)
    db.session.commit()
    return selection

def delete_player_prop_selection(selection_id):
    """Delete a prop selection"""
    selection = PlayerPropSelection.query.get(selection_id)
    if selection:
        db.session.delete(selection)
        db.session.commit()
        return True
    return False

def check_prop_already_selected(player_id, game_id, prop_type, prop_id):
    """Check if a player has already selected this specific prop"""
    return PlayerPropSelection.query.filter_by(
        player_id=player_id,
        game_id=game_id,
        prop_type=prop_type,
        prop_id=prop_id
    ).first() is not None

def delete_all_player_selections_for_game(player_id, game_id):
    """Delete all prop selections for a player for a specific game"""
    PlayerPropSelection.query.filter_by(player_id=player_id, game_id=game_id).delete()
    db.session.commit()