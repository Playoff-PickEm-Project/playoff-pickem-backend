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
from app.models.props.anytimeTdProp import AnytimeTdProp
from app.models.props.anytimeTdOption import AnytimeTdOption
from app.models.propAnswers.anytimeTdAnswer import AnytimeTdAnswer
from app.repositories.leagueRepository import get_league_by_name
from app.repositories.gameRepository import get_game_by_id
from app.repositories.playerRepository import get_player_by_username_and_leaguename, get_player_by_id
from app.repositories.propRepository import get_variable_option_answers_for_prop, get_variable_option_prop_by_id, get_winner_loser_prop_by_id, get_over_under_prop_by_id, get_over_under_answers_for_prop, get_winner_loser_answers_for_prop, get_anytime_td_prop_by_id, get_anytime_td_answers_for_prop
from app.validators.leagueValidator import validate_league_name, validate_league_exists, validate_player_exists
from app.validators.userValidator import validate_username
from app.validators.gameValidator import validate_game_exists, validate_game_id
from app.validators.propValidator import validate_prop_id, validate_answer


class GameService:
    """
    Service class for handling game-related business logic.

    This class manages game creation, player answer submission for all prop types,
    retrieval of games and picks, and creation of individual props within games.
    """

    @staticmethod
    def answer_game(leagueName, username, game_id, answer):
        """
        Save answers for all props in a game for a specific player.

        Iterates through all winner/loser, over/under, and variable option props
        in the game and saves the player's answers using helper methods.

        Args:
            leagueName (str): The name of the league containing the game.
            username (str): The username of the player answering.
            game_id (int): The unique identifier of the game.
            answer (dict): Dictionary containing answers mapped to prop_ids.

        Returns:
            dict: A success message if all answers are saved successfully.

        Raises:
            400: If validation fails for leagueName, username, or game_id.
            404: If the game doesn't exist.
        """
        leagueName = validate_league_name(leagueName)
        username = validate_username(username)
        game_id = validate_game_id(game_id)

        game = get_game_by_id(game_id)
        validate_game_exists(game)

        for winnerLoserProp in game.winner_loser_props:
            GameService.answer_winner_loser_prop(leagueName, username, winnerLoserProp.id, answer)

        for overUnderProp in game.over_under_props:
            GameService.answer_over_under_prop(leagueName, username, overUnderProp.id, answer)

        for variableOptionProp in game.variable_option_props:
            GameService.answer_variable_option_prop(leagueName, username, variableOptionProp.id, answer)

        for anytimeTdProp in game.anytime_td_props:
            GameService.answer_anytime_td_prop(leagueName, username, anytimeTdProp.id, answer)

        return {"Message": "Game answered by player successfully."}

    @staticmethod
    def answer_winner_loser_prop(leagueName, username, prop_id, answer):
        """
        Save or update a player's answer for a winner/loser prop.

        If the player has already answered this prop, updates their existing answer.
        Otherwise, creates a new answer record.

        Args:
            leagueName (str): The name of the league.
            username (str): The username of the player.
            prop_id (int): The unique identifier of the winner/loser prop.
            answer (dict): Dictionary containing the answer for this prop.

        Returns:
            dict: A success message indicating whether the answer was created or updated.

        Raises:
            400: If validation fails for any input.
            404: If the player doesn't exist.
        """
        leagueName = validate_league_name(leagueName)
        username = validate_username(username)
        prop_id = validate_prop_id(prop_id)
        answer = validate_answer(answer)

        player = get_player_by_username_and_leaguename(username, leagueName)
        validate_player_exists(player)

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

    @staticmethod
    def answer_over_under_prop(leagueName, username, prop_id, answer):
        """
        Save or update a player's answer for an over/under prop.

        If the player has already answered this prop, updates their existing answer.
        Otherwise, creates a new answer record.

        Args:
            leagueName (str): The name of the league.
            username (str): The username of the player.
            prop_id (int): The unique identifier of the over/under prop.
            answer (dict): Dictionary containing the answer for this prop.

        Returns:
            dict: A success message indicating whether the answer was created or updated.

        Raises:
            400: If validation fails for any input.
            404: If the player doesn't exist.
        """
        leagueName = validate_league_name(leagueName)
        username = validate_username(username)
        prop_id = validate_prop_id(prop_id)
        answer = validate_answer(answer)

        player = get_player_by_username_and_leaguename(username, leagueName)
        validate_player_exists(player)

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

    @staticmethod
    def answer_variable_option_prop(leagueName, username, prop_id, answer):
        """
        Save or update a player's answer for a variable option prop.

        If the player has already answered this prop, updates their existing answer.
        Otherwise, creates a new answer record.

        Args:
            leagueName (str): The name of the league.
            username (str): The username of the player.
            prop_id (int): The unique identifier of the variable option prop.
            answer (dict): Dictionary containing the answer for this prop.

        Returns:
            dict: A success message indicating whether the answer was created or updated.

        Raises:
            400: If validation fails for any input.
            404: If the player doesn't exist.
        """
        leagueName = validate_league_name(leagueName)
        username = validate_username(username)
        prop_id = validate_prop_id(prop_id)
        answer = validate_answer(answer)

        player = get_player_by_username_and_leaguename(username, leagueName)
        validate_player_exists(player)

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

    @staticmethod
    def answer_anytime_td_prop(leagueName, username, prop_id, answer):
        """
        Save or update a player's answer for an anytime TD prop.

        The answer should be the player name selected from the available options
        (e.g., "Travis Kelce"). If the player has already answered this prop,
        updates their existing answer. Otherwise, creates a new answer record.

        Args:
            leagueName (str): The name of the league.
            username (str): The username of the player.
            prop_id (int): The unique identifier of the anytime TD prop.
            answer (dict): Dictionary containing the answer for this prop
                          (should include the selected player name).

        Returns:
            dict: A success message indicating whether the answer was created or updated.

        Raises:
            400: If validation fails for any input.
            404: If the player doesn't exist.

        Example:
            answer_anytime_td_prop("MyLeague", "john@example.com", 5, "Travis Kelce")
        """
        leagueName = validate_league_name(leagueName)
        username = validate_username(username)
        prop_id = validate_prop_id(prop_id)
        answer = validate_answer(answer)

        player = get_player_by_username_and_leaguename(username, leagueName)
        validate_player_exists(player)

        # Check if the player has already answered this prop_id
        existing_answer = AnytimeTdAnswer.query.filter_by(prop_id=prop_id, player_id=player.id).first()

        if existing_answer:
            # If the player has already answered, update the existing answer
            existing_answer.answer = answer
            db.session.commit()
            return {"Message": "Anytime TD prop answer updated successfully."}
        else:
            # If the player hasn't answered yet, create a new answer
            new_answer = AnytimeTdAnswer(
                answer=answer,
                prop_id=prop_id,
                player_id=player.id
            )
            db.session.add(new_answer)
            db.session.commit()

            return {"Message": "Anytime TD prop successfully answered."}

    @staticmethod
    def create_game(leagueName, gameName, date, winnerLoserQuestions, overUnderQuestions, variableOptionQuestions, anytimeTdQuestions=None, externalGameId=None, propLimit=2):
        """
        Create a new game within a league with multiple prop types.

        Creates a game with the specified name and date, then creates all winner/loser,
        over/under, variable option, and anytime TD props for that game.

        Args:
            leagueName (str): The name of the league to create the game in.
            gameName (str): The name of the game.
            date (str): The start time/date for the game.
            winnerLoserQuestions (list): List of dictionaries containing winner/loser prop data.
            overUnderQuestions (list): List of dictionaries containing over/under prop data.
            variableOptionQuestions (list): List of dictionaries containing variable option prop data.
            anytimeTdQuestions (list, optional): List of dictionaries containing anytime TD prop data.
            externalGameId (str, optional): ESPN game ID for live polling.
            propLimit (int, optional): Number of optional props players must answer. Defaults to 2.

        Returns:
            dict: A success message if the game is created successfully.

        Raises:
            401: If the league doesn't exist or there's an error creating the game.
        """
        # Get the league the request is being made from.
        league = get_league_by_name(leagueName)

        if (league is None):
            abort(401, "League not found")

        # Create a new game with the basic fields that we know must be true (based on arguments).
        new_game = Game(
            league_id = league.id,
            game_name = gameName,
            start_time = date,
            graded = 0,
            external_game_id = externalGameId,  # Store ESPN game ID for polling
            prop_limit = propLimit
        )

        print(date)

        # Db.session.add adds the game into the database (note that we import the db from our __init__ file I believe).
        # Db.session.commit() saves the changes I believe.
        db.session.add(new_game)
        db.session.commit()

        # Iterate through each type of question to create an individual prop for it.
        for winnerLoserProp in winnerLoserQuestions:
            GameService.createWinnerLoserQuestion(winnerLoserProp, new_game.id)

        for overUnderProp in overUnderQuestions:
            GameService.createOverUnderQuestion(overUnderProp, new_game.id)

        for variableOptionProp in variableOptionQuestions:
            GameService.createVariableOptionQuestion(variableOptionProp, new_game.id)

        # Create anytime TD props if provided
        if anytimeTdQuestions:
            for anytimeTdProp in anytimeTdQuestions:
                GameService.createAnytimeTdQuestion(anytimeTdProp, new_game.id)

        league.league_games.append(new_game)

        db.session.commit()

        return {"message": "Created game successfully."}

    @staticmethod
    def createVariableOptionQuestion(variableOptionProp, game_id):
        """
        Create a variable option prop for a game.

        Creates a prop with multiple answer choices, each with their own point values.

        Args:
            variableOptionProp (dict): Dictionary containing question and options data.
            game_id (int): The unique identifier of the game this prop belongs to.

        Returns:
            dict: A success message if the prop is created successfully.
        """
        game = get_game_by_id(game_id)

        # From the argument, retrieve the question and answer choices (a list of tuples basically; idk if that's exactly accurate tho).
        question = variableOptionProp.get("question")
        options = variableOptionProp.get("options")
        is_mandatory = variableOptionProp.get("is_mandatory", False)

        # Rest from here on out is pretty self explanatory. Just setting the fields based on the arg.
        new_prop = VariableOptionProp(
            game_id = game_id,
            question = question,
            is_mandatory = is_mandatory
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

    @staticmethod
    def createWinnerLoserQuestion(winnerLoserProp, game_id):
        """
        Create a winner/loser prop for a game.

        Creates a prop with favorite and underdog teams and their respective point values.

        Args:
            winnerLoserProp (dict): Dictionary containing question, teams, and point data.
            game_id (int): The unique identifier of the game this prop belongs to.

        Returns:
            dict: A success message if the prop is created successfully.
        """
        game = get_game_by_id(game_id)
        print(winnerLoserProp)

        question = winnerLoserProp.get("question")
        favoritePoints = winnerLoserProp.get("favoritePoints")
        underdogPoints = winnerLoserProp.get("underdogPoints")
        favoriteTeam = winnerLoserProp.get("favoriteTeam")
        underdogTeam = winnerLoserProp.get("underdogTeam")
        favoriteTeamId = winnerLoserProp.get("favoriteTeamId")
        underdogTeamId = winnerLoserProp.get("underdogTeamId")
        is_mandatory = winnerLoserProp.get("is_mandatory", True)

        new_prop = WinnerLoserProp(
            game_id = game_id,
            question = question,
            favorite_points = favoritePoints,
            underdog_points = underdogPoints,
            favorite_team = favoriteTeam,
            underdog_team = underdogTeam,
            team_a_id = favoriteTeamId,
            team_b_id = underdogTeamId,
            team_a_name = favoriteTeam,
            team_b_name = underdogTeam,
            is_mandatory = is_mandatory
        )

        game.winner_loser_props.append(new_prop)

        db.session.add(new_prop)
        db.session.commit()

        return {"message": "Created winner/loser prop successfully."}

    @staticmethod
    def createOverUnderQuestion(overUnderProp, game_id):
        """
        Create an over/under prop for a game.

        Creates a prop with over and under point values.

        Args:
            overUnderProp (dict): Dictionary containing question and point data.
            game_id (int): The unique identifier of the game this prop belongs to.

        Returns:
            dict: A success message if the prop is created successfully.
        """
        game = get_game_by_id(game_id)

        question = overUnderProp.get("question")
        overPoints = overUnderProp.get("overPoints")
        underPoints = overUnderProp.get("underPoints")
        playerName = overUnderProp.get("playerName")
        playerId = overUnderProp.get("playerId")
        statType = overUnderProp.get("statType")
        lineValue = overUnderProp.get("lineValue")
        is_mandatory = overUnderProp.get("is_mandatory", False)

        new_prop = OverUnderProp(
            game_id = game_id,
            question = question,
            over_points = overPoints,
            under_points = underPoints,
            player_name = playerName,
            player_id = playerId,
            stat_type = statType,
            line_value = lineValue,
            is_mandatory = is_mandatory
        )

        game.over_under_props.append(new_prop)

        db.session.add(new_prop)
        db.session.commit()

        return {"message": "Created over/under prop successfully."}

    @staticmethod
    def createAnytimeTdQuestion(anytimeTdProp, game_id):
        """
        Create an anytime TD scorer prop for a game.

        Creates a prop with multiple player options, where each option has its own
        player name, TD line threshold, and point value. Users select one player,
        and points are awarded if that player scores TDs >= their specific line.

        Args:
            anytimeTdProp (dict): Dictionary containing:
                - question (str): The prop question text
                - is_mandatory (bool): Whether all players must answer this prop
                - options (list): List of player option dicts with:
                    - player_name (str): Name of the player (e.g., "Travis Kelce")
                    - td_line (float): TD threshold (e.g., 0.5 for 1+ TD, 1.5 for 2+ TDs)
                    - points (int): Points awarded if player hits their line
            game_id (int): The unique identifier of the game this prop belongs to.

        Returns:
            dict: A success message if the prop is created successfully.

        Example:
            anytimeTdProp = {
                "question": "Pick a player to score a TD",
                "is_mandatory": False,
                "options": [
                    {"player_name": "Travis Kelce", "td_line": 0.5, "points": 5},
                    {"player_name": "Patrick Mahomes", "td_line": 1.5, "points": 12}
                ]
            }
        """
        game = get_game_by_id(game_id)

        # Extract prop-level fields
        question = anytimeTdProp.get("question")
        options = anytimeTdProp.get("options")
        is_mandatory = anytimeTdProp.get("is_mandatory", False)

        # Create the prop
        new_prop = AnytimeTdProp(
            game_id = game_id,
            question = question,
            is_mandatory = is_mandatory
        )

        # Initialize empty options list
        new_prop.options = []

        # Add to game's relationship
        game.anytime_td_props.append(new_prop)

        # Create each player option with its own TD line and points
        for option in options:
            new_option = AnytimeTdOption(
                player_name = option.get('player_name'),
                td_line = option.get('td_line', 0.5),  # Default to 0.5 (1+ TD) if not specified
                points = option.get('points'),
                current_tds = 0  # Initialize to 0, will be updated by polling
            )
            db.session.add(new_option)
            new_prop.options.append(new_option)

        db.session.add(new_prop)
        db.session.commit()

        return {"message": "Created anytime TD prop successfully."}

    @staticmethod
    def view_games_in_league(leagueName):
        """
        Retrieve all games within a specific league.

        Gets all games associated with a league and returns them as dictionaries.

        Args:
            leagueName (str): The name of the league.

        Returns:
            list: A list of dictionaries containing game information.

        Raises:
            400: If leagueName validation fails.
            404: If the league doesn't exist.
        """
        leagueName = validate_league_name(leagueName)
        league = get_league_by_name(leagueName)
        validate_league_exists(league)

        return [game.to_dict() for game in league.league_games]

    @staticmethod
    def get_all_picks_from_game(game_id):
        """
        Retrieve all player answers/picks for all props in a game.

        Iterates through all winner/loser, over/under, and variable option props
        in the game and collects all player answers with associated player names,
        correct answers, and questions.

        Args:
            game_id (int): The unique identifier of the game.

        Returns:
            list: A list of dictionaries containing player picks with player names,
                  answers, prop IDs, correct answers, and questions.
        """
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

        # Loop through all variable option props and get answers for each one
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

        # Loop through all anytime TD props and get answers for each one
        for prop in game.anytime_td_props:
            answers = get_anytime_td_answers_for_prop(prop.id)

            # Iterate through the answers and associate each player's name with their answer
            for answer in answers:
                player = get_player_by_id(answer.player_id)
                if player is not None:
                    picks.append({
                        "player_name": player.name,
                        "answer": answer.answer,  # The player name they selected (e.g., "Travis Kelce")
                        "prop_id": prop.id,
                        "correct_answer": prop.correct_answer,  # JSON array of players who hit their lines
                        "question": prop.question
                    })

        # Return the list of all picks (player names and their answers)
        return picks

    @staticmethod
    def add_winner_loser_prop(data):
        """
        Add a new Winner/Loser prop to an existing game.

        Creates a new winner/loser prop with the provided data and associates it
        with the specified game.

        Args:
            data (dict): Dictionary containing:
                - game_id (int): The ID of the game to add the prop to
                - question (str): The prop question text
                - favorite_team (str): Name of the favorite team
                - underdog_team (str): Name of the underdog team
                - favorite_points (float): Points awarded for picking favorite
                - underdog_points (float): Points awarded for picking underdog
                - favorite_team_id (str, optional): ESPN team ID for favorite
                - underdog_team_id (str, optional): ESPN team ID for underdog

        Returns:
            dict: Success message with the newly created prop's ID

        Raises:
            400: If validation fails for game_id
            404: If the game doesn't exist
        """
        game_id = validate_game_id(data.get('game_id'))
        game = get_game_by_id(game_id)
        validate_game_exists(game)

        new_prop = WinnerLoserProp(
            game_id=game_id,
            question=data.get('question'),
            favorite_points=data.get('favorite_points'),
            underdog_points=data.get('underdog_points'),
            favorite_team=data.get('favorite_team'),
            underdog_team=data.get('underdog_team'),
            team_a_id=data.get('favorite_team_id'),
            team_b_id=data.get('underdog_team_id'),
            team_a_name=data.get('favorite_team'),
            team_b_name=data.get('underdog_team')
        )

        game.winner_loser_props.append(new_prop)
        db.session.add(new_prop)
        db.session.commit()

        return {"message": "Winner/Loser prop added successfully.", "prop_id": new_prop.id}

    @staticmethod
    def add_over_under_prop(data):
        """
        Add a new Over/Under prop to an existing game.

        Creates a new over/under prop with the provided data and associates it
        with the specified game. Optionally supports player stat tracking for live updates.

        Args:
            data (dict): Dictionary containing:
                - game_id (int): The ID of the game to add the prop to
                - question (str): The prop question text
                - over_points (float): Points awarded for picking over
                - under_points (float): Points awarded for picking under
                - player_name (str, optional): Name of player for stat tracking
                - player_id (str, optional): ESPN player ID for live stat tracking
                - stat_type (str, optional): Type of stat to track (e.g., "passing_yards")
                - line_value (float, optional): The over/under line value

        Returns:
            dict: Success message with the newly created prop's ID

        Raises:
            400: If validation fails for game_id
            404: If the game doesn't exist
        """
        game_id = validate_game_id(data.get('game_id'))
        game = get_game_by_id(game_id)
        validate_game_exists(game)

        new_prop = OverUnderProp(
            game_id=game_id,
            question=data.get('question'),
            over_points=data.get('over_points'),
            under_points=data.get('under_points'),
            player_name=data.get('player_name'),
            player_id=data.get('player_id'),
            stat_type=data.get('stat_type'),
            line_value=data.get('line_value')
        )

        game.over_under_props.append(new_prop)
        db.session.add(new_prop)
        db.session.commit()

        return {"message": "Over/Under prop added successfully.", "prop_id": new_prop.id}

    @staticmethod
    def add_variable_option_prop(data):
        """
        Add a new Variable Option (multiple choice) prop to an existing game.

        Creates a new variable option prop with multiple answer choices and their
        respective point values.

        Args:
            data (dict): Dictionary containing:
                - game_id (int): The ID of the game to add the prop to
                - question (str): The prop question text
                - options (list): List of option dicts with 'choice_text' and 'points'
                    Example: [{"choice_text": "Option A", "points": 1.0}, ...]

        Returns:
            dict: Success message with the newly created prop's ID

        Raises:
            400: If validation fails for game_id
            404: If the game doesn't exist
        """
        game_id = validate_game_id(data.get('game_id'))
        game = get_game_by_id(game_id)
        validate_game_exists(game)

        new_prop = VariableOptionProp(
            game_id=game_id,
            question=data.get('question'),
        )

        new_prop.options = []
        game.variable_option_props.append(new_prop)

        # Create option choices
        options = data.get('options', [])
        for option in options:
            new_choice = HashMapAnswers(
                answer_choice=option.get('choice_text'),
                answer_points=option.get('points')
            )
            db.session.add(new_choice)
            new_prop.options.append(new_choice)

        db.session.add(new_prop)
        db.session.commit()

        return {"message": "Variable Option prop added successfully.", "prop_id": new_prop.id}

    @staticmethod
    def add_anytime_td_prop(data):
        """
        Add a new Anytime TD prop to an existing game.

        Creates a new anytime TD prop with multiple player options, where each option
        has its own TD line and point value.

        Args:
            data (dict): Dictionary containing:
                - game_id (int): The ID of the game to add the prop to
                - question (str): The prop question text
                - is_mandatory (bool, optional): Whether this prop is mandatory
                - options (list): List of option dicts with:
                    - player_name (str): Name of the player
                    - td_line (float): TD threshold (0.5 = 1+, 1.5 = 2+, etc.)
                    - points (int): Points awarded if player hits their line
                Example: [
                    {"player_name": "Travis Kelce", "td_line": 0.5, "points": 5},
                    {"player_name": "Patrick Mahomes", "td_line": 1.5, "points": 12}
                ]

        Returns:
            dict: Success message with the newly created prop's ID

        Raises:
            400: If validation fails for game_id
            404: If the game doesn't exist
        """
        game_id = validate_game_id(data.get('game_id'))
        game = get_game_by_id(game_id)
        validate_game_exists(game)

        new_prop = AnytimeTdProp(
            game_id=game_id,
            question=data.get('question'),
            is_mandatory=data.get('is_mandatory', False)
        )

        new_prop.options = []
        game.anytime_td_props.append(new_prop)

        # Create player options with their individual TD lines and points
        options = data.get('options', [])
        for option in options:
            new_option = AnytimeTdOption(
                player_name=option.get('player_name'),
                td_line=option.get('td_line', 0.5),
                points=option.get('points'),
                current_tds=0
            )
            db.session.add(new_option)
            new_prop.options.append(new_option)

        db.session.add(new_prop)
        db.session.commit()

        return {"message": "Anytime TD prop added successfully.", "prop_id": new_prop.id}

    @staticmethod
    def delete_prop(data):
        """
        Delete a specific prop from a game.

        Removes the prop and all associated player answers. Works for all four
        prop types: Winner/Loser, Over/Under, Variable Option, and Anytime TD.

        Args:
            data (dict): Dictionary containing:
                - prop_id (int): The ID of the prop to delete
                - prop_type (str): Type of prop - "winner_loser", "over_under",
                                   "variable_option", or "anytime_td"

        Returns:
            dict: Success message

        Raises:
            400: If validation fails for prop_id or invalid prop_type
            404: If the prop doesn't exist
        """
        prop_id = validate_prop_id(data.get('prop_id'))
        prop_type = data.get('prop_type')

        if prop_type == 'winner_loser':
            prop = get_winner_loser_prop_by_id(prop_id)
            if not prop:
                abort(404, "Winner/Loser prop not found")

            # Delete all associated answers
            WinnerLoserAnswer.query.filter_by(prop_id=prop_id).delete()
            db.session.delete(prop)

        elif prop_type == 'over_under':
            prop = get_over_under_prop_by_id(prop_id)
            if not prop:
                abort(404, "Over/Under prop not found")

            # Delete all associated answers
            OverUnderAnswer.query.filter_by(prop_id=prop_id).delete()
            db.session.delete(prop)

        elif prop_type == 'variable_option':
            prop = get_variable_option_prop_by_id(prop_id)
            if not prop:
                abort(404, "Variable Option prop not found")

            # Delete all associated answers
            VariableOptionAnswer.query.filter_by(prop_id=prop_id).delete()

            # Delete all associated option choices
            for option in prop.options:
                db.session.delete(option)

            db.session.delete(prop)

        elif prop_type == 'anytime_td':
            prop = get_anytime_td_prop_by_id(prop_id)
            if not prop:
                abort(404, "Anytime TD prop not found")

            # Delete all associated answers
            AnytimeTdAnswer.query.filter_by(prop_id=prop_id).delete()

            # Delete all associated player options (cascade should handle this, but being explicit)
            for option in prop.options:
                db.session.delete(option)

            db.session.delete(prop)

        else:
            abort(400, "Invalid prop_type. Must be 'winner_loser', 'over_under', 'variable_option', or 'anytime_td'")

        db.session.commit()

        return {"message": f"{prop_type.replace('_', ' ').title()} prop deleted successfully."}

    @staticmethod
    def update_game(data):
        """
        Update game metadata (name, start time, external game ID).

        Allows commissioners to modify game details after creation.

        Args:
            data (dict): Dictionary containing:
                - game_id (int): The ID of the game to update
                - game_name (str, optional): New game name
                - start_time (str, optional): New start time (ISO format string)
                - external_game_id (str, optional): New ESPN game ID for live polling

        Returns:
            dict: Success message

        Raises:
            400: If validation fails for game_id
            404: If the game doesn't exist
        """
        from datetime import datetime

        game_id = validate_game_id(data.get('game_id'))
        game = get_game_by_id(game_id)
        validate_game_exists(game)

        # Update game name if provided
        if 'game_name' in data and data['game_name']:
            game.game_name = data['game_name']

        # Update start time if provided
        if 'start_time' in data and data['start_time']:
            # Parse ISO format datetime string
            game.start_time = datetime.fromisoformat(data['start_time'].replace('Z', '+00:00'))

        # Update external game ID if provided
        if 'external_game_id' in data:
            game.external_game_id = data['external_game_id'] if data['external_game_id'] else None

        # Update prop_limit if provided
        if 'prop_limit' in data and data['prop_limit']:
            game.prop_limit = int(data['prop_limit'])

        db.session.commit()

        return {"message": "Game updated successfully."}
