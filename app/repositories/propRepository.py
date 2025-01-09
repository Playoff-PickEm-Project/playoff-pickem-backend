from app.models.props.winnerLoserProp import WinnerLoserProp
from app.models.props.overUnderProp import OverUnderProp
from app.models.propAnswers.overUnderAnswer import OverUnderAnswer
from app.models.propAnswers.winnerLoserAnswer import WinnerLoserAnswer

def get_winner_loser_prop_by_id(id):
    return WinnerLoserProp.query.get(id)

def get_over_under_prop_by_id(id):
    return OverUnderProp.query.get(id)

def get_winner_loser_answers_for_prop(prop_id):
    return WinnerLoserAnswer.query.filter_by(prop_id=prop_id).all()

def get_over_under_answers_for_prop(prop_id):
    return OverUnderAnswer.query.filter_by(prop_id=prop_id).all()