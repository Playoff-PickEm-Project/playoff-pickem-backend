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
from app.repositories.leagueRepository import get_league_by_name
from app.repositories.gameRepository import get_game_by_id
from app.repositories.playerRepository import get_player_by_username_and_leaguename, get_player_by_id
from app.repositories.propRepository import get_variable_option_answers_for_prop, get_variable_option_prop_by_id, get_winner_loser_prop_by_id, get_over_under_prop_by_id, get_over_under_answers_for_prop, get_winner_loser_answers_for_prop
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
    def create_game(leagueName, gameName, date, winnerLoserQuestions, overUnderQuestions, variableOptionQuestions):
        """
        Create a new game within a league with multiple prop types.

        Creates a game with the specified name and date, then creates all winner/loser,
        over/under, and variable option props for that game.

        Args:
            leagueName (str): The name of the league to create the game in.
            gameName (str): The name of the game.
            date (str): The start time/date for the game.
            winnerLoserQuestions (list): List of dictionaries containing winner/loser prop data.
            overUnderQuestions (list): List of dictionaries containing over/under prop data.
            variableOptionQuestions (list): List of dictionaries containing variable option prop data.

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
            graded = 0
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

        # Rest from here on out is pretty self explanatory. Just setting the fields based on the arg.
        new_prop = VariableOptionProp(
            game_id = game_id,
            question = question,
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

        # Loop through all over-under props and get answers for each one
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

        # Return the list of all picks (player names and their answers)
        return picks
