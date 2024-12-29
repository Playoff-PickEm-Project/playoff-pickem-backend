from app.models.leagueModel import League

def get_all_leagues():
    return League.query.all()

def get_league_by_name(leaguename):
    return League.query.filter_by(league_name=leaguename).first()