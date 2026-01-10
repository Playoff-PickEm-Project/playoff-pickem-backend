from flask import abort
from app import db
from app.repositories.leagueRepository import get_league_by_name
from app.repositories.playerRepository import get_player_by_id, get_player_by_username_and_leaguename
from app.repositories.gameRepository import get_game_by_id
from app.repositories.propRepository import get_all_variable_option_props_for_game, get_all_winner_loser_props_for_game, get_all_over_under_props_for_game, get_over_under_answers_for_prop, get_winner_loser_answers_for_prop, get_winner_loser_prop_by_id, get_over_under_prop_by_id
from app.validators.leagueValidator import validate_league_name, validate_league_exists, validate_player_exists
from app.validators.userValidator import validate_username
from app.validators.gameValidator import validate_game_exists, validate_game_id
from app.validators.propValidator import validate_prop_exists, validate_prop_id, validate_answer, validate_question


class PropService:
    """
    Service class for handling proposition-related business logic.

    This class manages retrieval of player answers, editing props, setting correct answers,
    and retrieving saved correct answers for all three prop types: WinnerLoser, OverUnder,
    and VariableOption.
    """

    @staticmethod
    def retrieve_winner_loser_answers(leaguename, username):
        """
        Retrieve a player's winner/loser answers for all props they've answered.

        Gets all winner/loser prop answers for a specific player in a league.

        Args:
            leaguename (str): The name of the league.
            username (str): The username of the player.

        Returns:
            dict: A dictionary mapping prop_id to the player's answer.

        Raises:
            400: If validation fails for leaguename or username.
            404: If the league or player doesn't exist.
        """
        leaguename = validate_league_name(leaguename)
        username = validate_username(username)

        league = get_league_by_name(leaguename)
        validate_league_exists(league)

        player = get_player_by_username_and_leaguename(username, leaguename)
        validate_player_exists(player)

        winner_loser_answers = {}

        for answer in player.player_winner_loser_answers:
            winner_loser_answers[answer.prop_id] = answer.answer

        return winner_loser_answers

    @staticmethod
    def retrieve_over_under_answers(leaguename, username):
        """
        Retrieve a player's over/under answers for all props they've answered.

        Gets all over/under prop answers for a specific player in a league.

        Args:
            leaguename (str): The name of the league.
            username (str): The username of the player.

        Returns:
            dict: A dictionary mapping prop_id to the player's answer.

        Raises:
            400: If validation fails for leaguename or username.
            404: If the league or player doesn't exist.
        """
        leaguename = validate_league_name(leaguename)
        username = validate_username(username)

        league = get_league_by_name(leaguename)
        validate_league_exists(league)

        player = get_player_by_username_and_leaguename(username, leaguename)
        validate_player_exists(player)

        over_under_answers = {}

        for answer in player.player_over_under_answers:
            over_under_answers[answer.prop_id] = answer.answer

        return over_under_answers

    @staticmethod
    def retrieve_variable_option_answers(leaguename, username):
        """
        Retrieve a player's variable option answers for all props they've answered.

        Gets all variable option prop answers for a specific player in a league.

        Args:
            leaguename (str): The name of the league.
            username (str): The username of the player.

        Returns:
            dict: A dictionary mapping prop_id to the player's answer.

        Raises:
            400: If validation fails for leaguename or username.
            404: If the league or player doesn't exist.
        """
        leaguename = validate_league_name(leaguename)
        username = validate_username(username)

        league = get_league_by_name(leaguename)
        validate_league_exists(league)

        player = get_player_by_username_and_leaguename(username, leaguename)
        validate_player_exists(player)

        variable_option_answers = {}

        for answer in player.player_variable_option_answers:
            variable_option_answers[answer.prop_id] = answer.answer

        return variable_option_answers

    @staticmethod
    def get_saved_correct_answers(game_id):
        """
        Retrieve all saved correct answers for a game.

        Gets the correct answers (if set) for all props in a game, including
        winner/loser, over/under, and variable option props.

        Args:
            game_id (int): The unique identifier of the game.

        Returns:
            list: A list of dictionaries containing prop_id and correct_answer for each prop.

        Raises:
            400: If game_id validation fails.
            404: If the game doesn't exist.
        """
        game_id = validate_game_id(game_id)
        game = get_game_by_id(game_id)
        validate_game_exists(game)

        # Fetch props and correct answers
        winner_loser_props = get_all_winner_loser_props_for_game(game_id)
        over_under_props = get_all_over_under_props_for_game(game_id)
        variable_option_props = get_all_variable_option_props_for_game(game_id)

        result = []

        # For winner_loser_props
        if winner_loser_props:
            for prop in winner_loser_props:
                print(prop.correct_answer)
                result.append({
                    'prop_id': prop.id,
                    'prop_type': 'winner_loser',
                    'correct_answer': prop.correct_answer
                })

        # For over_under_props
        if over_under_props:
            for prop in over_under_props:
                print(prop.correct_answer)
                result.append({
                    'prop_id': prop.id,
                    'prop_type': 'over_under',
                    'correct_answer': prop.correct_answer
                })

        if variable_option_props:
            for prop in variable_option_props:
                print(prop.correct_answer)

                if prop.correct_answer:
                    for answer in prop.correct_answer:
                        result.append({
                            'prop_id': prop.id,
                            'prop_type': 'variable_option',
                            'correct_answer': answer
                        })

        return result

    @staticmethod
    def edit_winner_loser_prop(prop_id, question, favoritePoints, underdogPoints, favorite_team=None, underdog_team=None):
        """
        Edit a winner/loser prop's question, point values, and team names.

        Updates the prop's question, favorite points, underdog points, and optionally
        the team names. If favoritePoints exceeds underdogPoints, the favorite and
        underdog teams are swapped.

        Args:
            prop_id (int): The unique identifier of the prop to edit.
            question (str): The new question text.
            favoritePoints (int): The points awarded for picking the favorite.
            underdogPoints (int): The points awarded for picking the underdog.
            favorite_team (str, optional): The favorite team name.
            underdog_team (str, optional): The underdog team name.

        Returns:
            None

        Raises:
            400: If validation fails for prop_id or question.
            404: If the prop doesn't exist.
        """
        prop_id = validate_prop_id(prop_id)
        question = validate_question(question)

        prop = get_winner_loser_prop_by_id(prop_id)
        validate_prop_exists(prop)

        # Update team names if provided
        if favorite_team is not None:
            prop.favorite_team = favorite_team
        if underdog_team is not None:
            prop.underdog_team = underdog_team

        if (favoritePoints > underdogPoints):
            fav_team_tmp = prop.favorite_team
            prop.favorite_team = prop.underdog_team
            prop.underdog_team = fav_team_tmp

        prop.question = question
        prop.favorite_points = favoritePoints
        prop.underdog_points = underdogPoints

        db.session.commit()

    @staticmethod
    def edit_over_under_prop(prop_id, question, overPoints, underPoints, player_name=None, player_id=None, stat_type=None, line_value=None):
        """
        Edit an over/under prop's question, point values, and player information.

        Updates the prop's question, over points, under points, and optionally
        player information for ESPN-tracked props.

        Args:
            prop_id (int): The unique identifier of the prop to edit.
            question (str): The new question text.
            overPoints (int): The points awarded for picking over.
            underPoints (int): The points awarded for picking under.
            player_name (str, optional): The player's name for ESPN tracking.
            player_id (str, optional): The ESPN player ID.
            stat_type (str, optional): The stat type (e.g., "passing_yards").
            line_value (float, optional): The over/under line value.

        Returns:
            None

        Raises:
            400: If validation fails for prop_id or question.
            404: If the prop doesn't exist.
        """
        prop_id = validate_prop_id(prop_id)
        question = validate_question(question)

        prop = get_over_under_prop_by_id(prop_id)
        validate_prop_exists(prop)

        prop.question = question
        prop.over_points = overPoints
        prop.under_points = underPoints

        # Update ESPN-related fields if provided
        if player_name is not None:
            prop.player_name = player_name
        if player_id is not None:
            prop.player_id = player_id
        if stat_type is not None:
            prop.stat_type = stat_type
        if line_value is not None:
            prop.line_value = line_value

        db.session.commit()

    @staticmethod
    def edit_variable_option_prop(prop_id, question, options):
        """
        Edit a variable option prop's question and options.

        Updates the prop's question and recreates all options with new values.

        Args:
            prop_id (int): The unique identifier of the prop to edit.
            question (str): The new question text.
            options (list): List of option dictionaries with 'answer_choice' and 'answer_points'.

        Returns:
            None

        Raises:
            400: If validation fails for prop_id or question.
            404: If the prop doesn't exist.
        """
        from app.models.props.variableOptionPropOption import VariableOptionPropOption

        prop_id = validate_prop_id(prop_id)
        question = validate_question(question)

        prop = get_variable_option_prop_by_id(prop_id)
        validate_prop_exists(prop)

        prop.question = question

        # Delete existing options
        for option in prop.options:
            db.session.delete(option)

        # Create new options
        for opt_data in options:
            new_option = VariableOptionPropOption(
                prop_id=prop_id,
                answer_choice=opt_data.get('answer_choice'),
                answer_points=opt_data.get('answer_points')
            )
            db.session.add(new_option)
            prop.options.append(new_option)

        db.session.commit()
