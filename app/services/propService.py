from flask import abort
from app import db
from app.repositories.leagueRepository import get_league_by_name
from app.repositories.playerRepository import get_player_by_id, get_player_by_username_and_leaguename
from app.repositories.gameRepository import get_game_by_id
from app.repositories.propRepository import (
    get_all_variable_option_props_for_game, get_all_winner_loser_props_for_game,
    get_all_over_under_props_for_game, get_over_under_answers_for_prop,
    get_winner_loser_answers_for_prop, get_winner_loser_prop_by_id, get_over_under_prop_by_id,
    get_player_prop_selections_for_game, get_player_prop_selection_count,
    create_player_prop_selection, delete_player_prop_selection,
    check_prop_already_selected, delete_all_player_selections_for_game
)
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

        # Update question and points
        prop.question = question
        prop.favorite_points = favoritePoints
        prop.underdog_points = underdogPoints

        # Update team names if provided
        if favorite_team is not None:
            prop.favorite_team = favorite_team
            prop.team_a_name = favorite_team  # Also update team_a for live stats
        if underdog_team is not None:
            prop.underdog_team = underdog_team
            prop.team_b_name = underdog_team  # Also update team_b for live stats

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

    @staticmethod
    def get_player_selected_props(player_id, game_id):
        """
        Get all props a player has selected to answer for a game.

        Args:
            player_id (int): The player's ID.
            game_id (int): The game's ID.

        Returns:
            list: A list of PlayerPropSelection objects.

        Raises:
            400: If validation fails.
            404: If game or player doesn't exist.
        """
        game_id = validate_game_id(game_id)
        game = get_game_by_id(game_id)
        validate_game_exists(game)

        player = get_player_by_id(player_id)
        validate_player_exists(player)

        return get_player_prop_selections_for_game(player_id, game_id)

    @staticmethod
    def select_prop_for_player(player_id, game_id, prop_type, prop_id):
        """
        Allow a player to select a prop they want to answer for a game.

        Validates that:
        - The game exists
        - The player exists
        - The prop exists and belongs to the game
        - The prop is not mandatory (mandatory props cannot be manually selected)
        - The player hasn't exceeded their prop_limit for OPTIONAL props
        - The player hasn't already selected this prop

        Args:
            player_id (int): The player's ID.
            game_id (int): The game's ID.
            prop_type (str): Type of prop ('winner_loser', 'over_under', 'variable_option').
            prop_id (int): The prop's ID.

        Returns:
            PlayerPropSelection: The created selection object.

        Raises:
            400: If validation fails or limits are exceeded.
            404: If game, player, or prop doesn't exist.
        """
        # Validate game and player
        game_id = validate_game_id(game_id)
        game = get_game_by_id(game_id)
        validate_game_exists(game)

        player = get_player_by_id(player_id)
        validate_player_exists(player)

        # Validate prop type
        if prop_type not in ['winner_loser', 'over_under', 'variable_option']:
            abort(400, description="Invalid prop_type. Must be 'winner_loser', 'over_under', or 'variable_option'.")

        # Validate prop exists and belongs to this game
        prop = None
        if prop_type == 'winner_loser':
            prop = get_winner_loser_prop_by_id(prop_id)
        elif prop_type == 'over_under':
            prop = get_over_under_prop_by_id(prop_id)
        elif prop_type == 'variable_option':
            from app.repositories.propRepository import get_variable_option_prop_by_id
            prop = get_variable_option_prop_by_id(prop_id)

        validate_prop_exists(prop)

        # Ensure game_id is an integer for comparison (frontend might send as string)
        if int(prop.game_id) != int(game_id):
            abort(400, description=f"This prop does not belong to the specified game.")

        # Check if prop is mandatory (mandatory props cannot be manually selected/deselected)
        if prop.is_mandatory:
            abort(400, description="Mandatory props cannot be manually selected. They are automatically required.")

        # Check if player has already selected this prop
        if check_prop_already_selected(player_id, game_id, prop_type, prop_id):
            abort(400, description="You have already selected this prop.")

        # Count only OPTIONAL prop selections (mandatory props don't count toward limit)
        current_selections = get_player_prop_selections_for_game(player_id, game_id)
        optional_count = sum(1 for s in current_selections if not PropService._is_prop_mandatory(s.prop_type, s.prop_id))

        if optional_count >= game.prop_limit:
            abort(400, description=f"You have already selected {game.prop_limit} optional props for this game.")

        # Create the selection
        return create_player_prop_selection(player_id, game_id, prop_type, prop_id)

    @staticmethod
    def _is_prop_mandatory(prop_type, prop_id):
        """Helper to check if a prop is mandatory."""
        if prop_type == 'winner_loser':
            prop = get_winner_loser_prop_by_id(prop_id)
        elif prop_type == 'over_under':
            prop = get_over_under_prop_by_id(prop_id)
        elif prop_type == 'variable_option':
            from app.repositories.propRepository import get_variable_option_prop_by_id
            prop = get_variable_option_prop_by_id(prop_id)
        else:
            return False
        return prop and prop.is_mandatory

    @staticmethod
    def deselect_prop_for_player(selection_id, player_id):
        """
        Allow a player to deselect a prop they previously selected.

        Deletes both the prop selection AND any answer the player submitted for that prop.
        Mandatory props cannot be deselected by players.

        Args:
            selection_id (int): The PlayerPropSelection ID.
            player_id (int): The player's ID (for authorization).

        Returns:
            bool: True if successful.

        Raises:
            400: If trying to deselect a mandatory prop.
            403: If selection doesn't belong to player.
            404: If selection doesn't exist.
        """
        from app.models.playerPropSelection import PlayerPropSelection
        from app.models.propAnswers.winnerLoserAnswer import WinnerLoserAnswer
        from app.models.propAnswers.overUnderAnswer import OverUnderAnswer
        from app.models.propAnswers.variableOptionAnswer import VariableOptionAnswer

        selection = PlayerPropSelection.query.get(selection_id)

        if not selection:
            abort(404, description="Prop selection not found.")

        if selection.player_id != player_id:
            abort(403, description="You can only deselect your own prop selections.")

        # Check if the prop is mandatory (players cannot deselect mandatory props)
        if PropService._is_prop_mandatory(selection.prop_type, selection.prop_id):
            abort(400, description="Mandatory props cannot be deselected.")

        # Delete any existing answer for this prop before deleting the selection
        prop_type = selection.prop_type
        prop_id = selection.prop_id

        if prop_type == 'winner_loser':
            existing_answer = WinnerLoserAnswer.query.filter_by(
                player_id=player_id,
                prop_id=prop_id
            ).first()
            if existing_answer:
                db.session.delete(existing_answer)
                db.session.commit()
        elif prop_type == 'over_under':
            existing_answer = OverUnderAnswer.query.filter_by(
                player_id=player_id,
                prop_id=prop_id
            ).first()
            if existing_answer:
                db.session.delete(existing_answer)
                db.session.commit()
        elif prop_type == 'variable_option':
            existing_answer = VariableOptionAnswer.query.filter_by(
                player_id=player_id,
                prop_id=prop_id
            ).first()
            if existing_answer:
                db.session.delete(existing_answer)
                db.session.commit()

        # Delete the prop selection
        return delete_player_prop_selection(selection_id)

    @staticmethod
    def reset_player_selections_for_game(player_id, game_id):
        """
        Remove all prop selections for a player for a specific game.

        Args:
            player_id (int): The player's ID.
            game_id (int): The game's ID.

        Returns:
            None

        Raises:
            400: If validation fails.
            404: If game or player doesn't exist.
        """
        game_id = validate_game_id(game_id)
        game = get_game_by_id(game_id)
        validate_game_exists(game)

        player = get_player_by_id(player_id)
        validate_player_exists(player)

        delete_all_player_selections_for_game(player_id, game_id)

    @staticmethod
    def validate_player_can_answer_prop(player_id, game_id, prop_type, prop_id):
        """
        Check if a player is allowed to answer a specific prop.

        A player can answer a prop if they have selected it in their PlayerPropSelection.

        Args:
            player_id (int): The player's ID.
            game_id (int): The game's ID.
            prop_type (str): Type of prop.
            prop_id (int): The prop's ID.

        Returns:
            bool: True if player can answer this prop.

        Raises:
            403: If player hasn't selected this prop.
        """
        if not check_prop_already_selected(player_id, game_id, prop_type, prop_id):
            abort(403, description="You must select this prop before answering it.")

        return True
