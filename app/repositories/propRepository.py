from app.models.propAnswers.variableOptionAnswer import VariableOptionAnswer
from app.models.props.variableOptionProp import VariableOptionProp
from app.models.props.winnerLoserProp import WinnerLoserProp
from app.models.props.overUnderProp import OverUnderProp
from app.models.propAnswers.overUnderAnswer import OverUnderAnswer
from app.models.propAnswers.winnerLoserAnswer import WinnerLoserAnswer

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