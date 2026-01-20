from flask import abort
from app import db
from app.models.gameModel import Game
from app.repositories.gameRepository import get_game_by_id
from app.repositories.propRepository import (
    get_winner_loser_answers_for_prop,
    get_over_under_answers_for_prop,
    get_variable_option_answers_for_prop,
    get_winner_loser_prop_by_id,
    get_over_under_prop_by_id,
    get_variable_option_prop_by_id,
    get_anytime_td_prop_by_id,
    get_anytime_td_answers_for_prop,
    get_player_prop_selections_for_game
)
from app.repositories.playerRepository import get_player_by_id
from app.validators.gameValidator import validate_game_exists, validate_game_id
from app.validators.propValidator import validate_prop_exists, validate_prop_id, validate_answer
from app.validators.leagueValidator import validate_league_name


class GradeGameService:
    """
    Service class for handling game grading and regrading logic.

    This class manages grading games by calculating and awarding points to players
    based on their answers, and handles regrading by deducting old points when
    correct answers are changed after a game has been graded.
    """

    @staticmethod
    def _has_player_selected_prop(player_id, game_id, prop_type, prop_id):
        """
        Check if a player has selected a specific prop for a game.

        Args:
            player_id (int): The player's ID
            game_id (int): The game's ID
            prop_type (str): Type of prop ("winner_loser", "over_under", "variable_option", or "anytime_td")
            prop_id (int): The prop's ID

        Returns:
            bool: True if the player has selected this prop, False otherwise
        """
        selections = get_player_prop_selections_for_game(player_id, game_id)
        for selection in selections:
            if selection.prop_type == prop_type and selection.prop_id == prop_id:
                return True
        return False

    @staticmethod
    def auto_grade_props_from_live_data(game):
        """
        Automatically set correct answers for O/U and W/L props based on live data.

        This method is called after a game completes and before grading. It:
        - Sets correct_answer for Over/Under props by comparing current_value to line_value
        - Sets correct_answer for Winner/Loser props by comparing team scores

        Args:
            game (Game): The completed game object with updated live data.

        Returns:
            None
        """
        # Auto-grade Over/Under props
        for prop in game.over_under_props:
            # Only auto-grade if we have the necessary data
            if prop.current_value is not None and prop.line_value is not None:
                if prop.current_value > prop.line_value:
                    prop.correct_answer = "over"  # Lowercase to match player answers
                elif prop.current_value < prop.line_value:
                    prop.correct_answer = "under"  # Lowercase to match player answers
                # If exactly equal, could be a push - leave correct_answer as None or handle separately
                print(f"Auto-graded O/U prop {prop.id}: {prop.correct_answer} (current: {prop.current_value}, line: {prop.line_value})")

        # Auto-grade Winner/Loser props
        for prop in game.winner_loser_props:
            # Only auto-grade if we have team scores
            if prop.team_a_score is not None and prop.team_b_score is not None:
                if prop.team_a_score > prop.team_b_score:
                    # Team A won - set correct_answer to team_a_name
                    prop.correct_answer = prop.team_a_name
                elif prop.team_b_score > prop.team_a_score:
                    # Team B won - set correct_answer to team_b_name
                    prop.correct_answer = prop.team_b_name
                # If scores are equal, it's a tie - leave correct_answer as None
                print(f"Auto-graded W/L prop {prop.id}: {prop.correct_answer} (score: {prop.team_a_score}-{prop.team_b_score})")

        # Auto-grade Anytime TD props
        for prop in game.anytime_td_props:
            # Collect all players who hit their TD lines
            correct_players = []
            for option in prop.options:
                # Check if this player scored enough TDs to hit their line
                if option.has_hit_line():
                    correct_players.append(option.player_name)
                    print(f"Auto-graded Anytime TD prop {prop.id}: {option.player_name} hit line (TDs: {option.current_tds}, line: {option.td_line})")

            # Set correct_answer as JSON array of player names who hit their lines
            if correct_players:
                prop.correct_answer = correct_players
                print(f"Auto-graded Anytime TD prop {prop.id}: correct_answer = {correct_players}")

        db.session.commit()

    @staticmethod
    def grade_game(game_id):
        """
        Grade a game by awarding points to players for correct answers.

        Iterates through all winner/loser, over/under, and variable option props
        in the game and awards points to players whose answers match the correct answers.

        Args:
            game_id (int): The unique identifier of the game to grade.

        Returns:
            None

        Raises:
            400: If game_id validation fails.
            404: If the game doesn't exist.
        """
        game_id = validate_game_id(game_id)
        game = get_game_by_id(game_id)
        validate_game_exists(game)

        # Iterate through the winner_loser_props of the game
        for prop in game.winner_loser_props:
            # Get all the answers for the current prop (for all players)
            answers = get_winner_loser_answers_for_prop(prop.id)

            # Iterate through each answer to grade it
            for answer in answers:
                player = get_player_by_id(answer.player_id)  # Get the player who submitted the answer

                # For optional props, check if player selected this prop
                if not prop.is_mandatory:
                    if not GradeGameService._has_player_selected_prop(player.id, game.id, "winner_loser", prop.id):
                        continue  # Skip grading if player didn't select this optional prop

                # Check if the player's answer matches the correct answer
                if player is not None and answer.answer == prop.correct_answer:
                    print("HERE")
                    # If the answer is correct, assign the appropriate points
                    if answer.answer == prop.favorite_team:
                        print("Before: ", player.points)
                        player.points += prop.favorite_points  # Add favorite points
                        print("After: ", player.points)
                    elif answer.answer == prop.underdog_team:
                        print("Before: ", player.points)
                        player.points += prop.underdog_points  # Add underdog points
                        print("After: ", player.points)

        for prop in game.over_under_props:
            answers = get_over_under_answers_for_prop(prop.id)

            for answer in answers:
                player = get_player_by_id(answer.player_id)
                print(answer.answer)

                # For optional props, check if player selected this prop
                if not prop.is_mandatory:
                    if not GradeGameService._has_player_selected_prop(player.id, game.id, "over_under", prop.id):
                        continue  # Skip grading if player didn't select this optional prop

                # Case-insensitive comparison for safety
                if player is not None and answer.answer.lower() == prop.correct_answer.lower():
                    if answer.answer.lower() == "over":
                        player.points += prop.over_points
                    elif answer.answer.lower() == "under":
                        player.points += prop.under_points

        for prop in game.variable_option_props:
            answers = get_variable_option_answers_for_prop(prop.id)

            for answer in answers:
                player = get_player_by_id(answer.player_id)

                # For optional props, check if player selected this prop
                if not prop.is_mandatory:
                    if not GradeGameService._has_player_selected_prop(player.id, game.id, "variable_option", prop.id):
                        continue  # Skip grading if player didn't select this optional prop

                for correct in prop.correct_answer:
                    if player is not None and answer.answer == correct:
                        points_to_add = 0

                        for option in prop.options:
                            if answer.answer == option.answer_choice:
                                points_to_add = option.answer_points

                        print(points_to_add)
                        player.points += points_to_add

        # Grade Anytime TD props
        for prop in game.anytime_td_props:
            answers = get_anytime_td_answers_for_prop(prop.id)

            for answer in answers:
                player = get_player_by_id(answer.player_id)

                # For optional props, check if player selected this prop
                if not prop.is_mandatory:
                    if not GradeGameService._has_player_selected_prop(player.id, game.id, "anytime_td", prop.id):
                        continue  # Skip grading if player didn't select this optional prop

                # Check if the player's selected player is in the correct_answer array
                # correct_answer is a JSON array of player names who hit their TD lines
                if player is not None and prop.correct_answer and answer.answer in prop.correct_answer:
                    # Find the corresponding option to get the points
                    points_to_add = 0
                    for option in prop.options:
                        if option.player_name == answer.answer:
                            points_to_add = option.points
                            break

                    print(f"Anytime TD: Awarding {points_to_add} points to {player.name} for selecting {answer.answer}")
                    player.points += points_to_add

        game.graded = 1

        db.session.commit()

    @staticmethod
    def set_correct_variable_option_prop(leaguename, prop_id, ans):
        """
        Set the correct answer for a variable option prop and handle regrading.

        If the game has already been graded, deducts points from players who got
        the old correct answer before updating to the new correct answer.

        Args:
            leaguename (str): The name of the league (for validation context).
            prop_id (int): The unique identifier of the variable option prop.
            ans (list): A list of correct answer choices for the prop.

        Returns:
            None

        Raises:
            400: If validation fails for leaguename or prop_id.
            404: If the prop or game doesn't exist.
        """
        leaguename = validate_league_name(leaguename)
        prop_id = validate_prop_id(prop_id)
        # ans is a list for variable options, don't validate as single answer

        p = get_variable_option_prop_by_id(prop_id)
        validate_prop_exists(p)
        print(prop_id)

        game = Game.query.filter_by(id=p.game_id).first()
        validate_game_exists(game)

        # If game already graded, deduct points for OLD correct answer before updating
        if game.graded != 0:
            # Only get answers for THIS specific prop
            answers = get_variable_option_answers_for_prop(prop_id)
            old_correct_answers = p.correct_answer  # Get OLD correct answer before updating

            for answer in answers:
                player = get_player_by_id(answer.player_id)

                # If player's answer matched the OLD correct answer, deduct those points
                if player is not None and answer.answer in old_correct_answers:
                    points_to_reduce = 0

                    for opt in p.options:
                        if opt.answer_choice == answer.answer:
                            points_to_reduce = opt.answer_points
                            break

                    player.points -= points_to_reduce
                    print(f"Deducted {points_to_reduce} points from player {player.name}")

        # Update to NEW correct answer
        print(ans)
        p.correct_answer = ans
        db.session.commit()

    @staticmethod
    def set_correct_winner_loser_prop(leaguename, prop_id, ans):
        """
        Set the correct answer for a winner/loser prop and handle regrading.

        If the game has already been graded, deducts points from players who got
        the old correct answer before updating to the new correct answer.

        Args:
            leaguename (str): The name of the league (for validation context).
            prop_id (int): The unique identifier of the winner/loser prop.
            ans (str): The correct answer (team name).

        Returns:
            None

        Raises:
            400: If validation fails for leaguename, prop_id, or ans.
            404: If the prop or game doesn't exist.
        """
        leaguename = validate_league_name(leaguename)
        prop_id = validate_prop_id(prop_id)
        ans = validate_answer(ans)

        p = get_winner_loser_prop_by_id(prop_id)
        validate_prop_exists(p)

        game = Game.query.filter_by(id=p.game_id).first()
        validate_game_exists(game)

        # If game already graded, deduct points for OLD correct answer before updating
        if game.graded != 0:
            # Only get answers for THIS specific prop
            answers = get_winner_loser_answers_for_prop(prop_id)
            old_correct_answer = p.correct_answer  # Get OLD correct answer before updating

            for answer in answers:
                player = get_player_by_id(answer.player_id)

                # If player's answer matched the OLD correct answer, deduct those points
                if player is not None and answer.answer == old_correct_answer:
                    print(f"Old correct answer: {old_correct_answer}")
                    # Deduct points based on which team they picked
                    if answer.answer == p.favorite_team:
                        player.points -= p.favorite_points
                        print(f"Deducted {p.favorite_points} points from player {player.name}")
                    elif answer.answer == p.underdog_team:
                        player.points -= p.underdog_points
                        print(f"Deducted {p.underdog_points} points from player {player.name}")

        # Update to NEW correct answer
        print("Correct winner/loser answer: ", ans)
        p.correct_answer = ans
        db.session.commit()

        print("Checking winner/loser prop answer saved or not: ", p.correct_answer)

    @staticmethod
    def set_correct_over_under_prop(leaguename, prop_id, ans):
        """
        Set the correct answer for an over/under prop and handle regrading.

        If the game has already been graded, deducts points from players who got
        the old correct answer before updating to the new correct answer. Uses
        case-insensitive comparison for "over" and "under" answers.

        Args:
            leaguename (str): The name of the league (for validation context).
            prop_id (int): The unique identifier of the over/under prop.
            ans (str): The correct answer ("over" or "under").

        Returns:
            None

        Raises:
            400: If validation fails for leaguename, prop_id, or ans.
            404: If the prop or game doesn't exist.
        """
        leaguename = validate_league_name(leaguename)
        prop_id = validate_prop_id(prop_id)
        ans = validate_answer(ans)

        p = get_over_under_prop_by_id(prop_id)
        validate_prop_exists(p)

        game = Game.query.filter_by(id=p.game_id).first()
        validate_game_exists(game)

        print(f"Game graded status: {game.graded}")

        # If game already graded, deduct points for OLD correct answer before updating
        if game.graded != 0:
            # Only get answers for THIS specific prop
            answers = get_over_under_answers_for_prop(prop_id)
            old_correct_answer = p.correct_answer  # Get OLD correct answer before updating

            for answer in answers:
                player = get_player_by_id(answer.player_id)

                # If player's answer matched the OLD correct answer, deduct those points (case-insensitive)
                if player is not None and answer.answer.lower() == old_correct_answer.lower():
                    if answer.answer.lower() == "over":
                        player.points -= p.over_points
                        print(f"Deducted {p.over_points} points from player {player.name}")
                    elif answer.answer.lower() == "under":
                        player.points -= p.under_points
                        print(f"Deducted {p.under_points} points from player {player.name}")

        # Update to NEW correct answer
        print("ANSWER: ", ans)
        p.correct_answer = ans
        db.session.commit()
        print("prop answer: ", p.correct_answer)

    @staticmethod
    def set_correct_anytime_td_prop(leaguename, prop_id, ans):
        """
        Set the correct answer for an anytime TD prop and handle regrading.

        The correct answer should be an array of player names who hit their TD lines.
        If the game has already been graded, deducts points from players who got
        the old correct answer before updating to the new correct answer.

        Args:
            leaguename (str): The name of the league (for validation context).
            prop_id (int): The unique identifier of the anytime TD prop.
            ans (list): A list of player names who hit their TD lines.
                       Example: ["Travis Kelce", "Patrick Mahomes"]

        Returns:
            None

        Raises:
            400: If validation fails for leaguename or prop_id.
            404: If the prop or game doesn't exist.
        """
        leaguename = validate_league_name(leaguename)
        prop_id = validate_prop_id(prop_id)
        # ans is a list for anytime TD props, don't validate as single answer

        p = get_anytime_td_prop_by_id(prop_id)
        validate_prop_exists(p)
        print(prop_id)

        game = Game.query.filter_by(id=p.game_id).first()
        validate_game_exists(game)

        # If game already graded, deduct points for OLD correct answer before updating
        if game.graded != 0:
            # Only get answers for THIS specific prop
            answers = get_anytime_td_answers_for_prop(prop_id)
            old_correct_answers = p.correct_answer if p.correct_answer else []  # Get OLD correct answers before updating

            for answer in answers:
                player = get_player_by_id(answer.player_id)

                # If player's answer matched the OLD correct answer, deduct those points
                if player is not None and answer.answer in old_correct_answers:
                    # Find the corresponding option to get the points to deduct
                    points_to_reduce = 0
                    for opt in p.options:
                        if opt.player_name == answer.answer:
                            points_to_reduce = opt.points
                            break

                    player.points -= points_to_reduce
                    print(f"Deducted {points_to_reduce} points from player {player.name}")

        # Update to NEW correct answer
        print(ans)
        p.correct_answer = ans
        db.session.commit()
