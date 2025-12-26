from flask import abort
from app import db
from app.models.leagueModel import League
from app.models.propAnswers.overUnderAnswer import OverUnderAnswer
from app.models.propAnswers.winnerLoserAnswer import WinnerLoserAnswer
from app.repositories.leagueRepository import get_all_leagues, get_league_by_name, get_leagues_by_username, get_league_by_join_code
from app.repositories.playerRepository import get_player_by_username_and_leaguename, get_player_by_playername_and_leaguename
from app.repositories.gameRepository import get_game_by_id
from app.services.playerService import PlayerService
from app.validators.leagueValidator import validate_league_name, validate_league_exists, validate_join_code, validate_player_name, validate_player_exists
from app.validators.userValidator import validate_username, validate_user_exists
from app.validators.gameValidator import validate_game_exists, validate_game_id
import secrets
import string


class LeagueService:
    """
    Service class for handling league-related business logic.

    This class manages league creation, deletion, player management within leagues,
    game deletion, and retrieval of league information including user leagues.
    """

    @staticmethod
    def generate_join_code(length=8):
        """
        Generate a random alphanumeric join code for a league.

        Creates a cryptographically secure random string consisting of uppercase letters,
        lowercase letters, and digits.

        Args:
            length (int, optional): The length of the join code. Defaults to 8.

        Returns:
            str: A random alphanumeric string of the specified length.
        """
        # Can include uppercase, lowercase, and numbers
        characters = string.ascii_letters + string.digits
        return ''.join(secrets.choice(characters) for _ in range(length))

    @staticmethod
    def create_league(leagueName, username, playerName):
        """
        Create a new league with the creator as the first player and commissioner.

        Validates inputs, ensures the league name is unique, generates a join code,
        creates the league, and adds the creator as the first player and commissioner.

        Args:
            leagueName (str): The name for the new league.
            username (str): The username of the user creating the league.
            playerName (str): The player name for the creator in this league.

        Returns:
            dict: A success message if the league is created successfully.

        Raises:
            400: If validation fails for any input.
            409: If a league with the same name already exists.
            401: If there's an error during league creation.
        """
        # Validate inputs
        leagueName = validate_league_name(leagueName)
        username = validate_username(username)
        playerName = validate_player_name(playerName)

        # Checking to see if a league with the same name already exists. If it does, return error.
        league = get_league_by_name(leagueName)

        if (league is not None):
            print("name taken")
            abort(409, "League name already exists. Choose another league name.")

        try:
            newLeague = League(
                league_name = leagueName,
                join_code = LeagueService.generate_join_code(),
            )

            db.session.add(newLeague)
            db.session.commit()

            first_player = PlayerService.create_player(playerName, username, leagueName)

            # This line might be unnecessary.
            newLeague.commissioner_id = first_player.id
            newLeague.commissioner = first_player

            db.session.commit()

            newLeague.league_players.append(first_player)

            db.session.add(first_player)
            db.session.commit()

            return {"message": "Successfully added league."}

        except Exception as error:

            print(f"Error: {error}")
            abort(401, "Error creating league. Please try again.")

    @staticmethod
    def get_all_user_leagues(username):
        """
        Retrieve all leagues that a user belongs to.

        Gets all leagues where the user has a player associated with their username.

        Args:
            username (str): The username to search for.

        Returns:
            list: A list of dictionaries containing league information.

        Raises:
            400: If username validation fails.
        """
        username = validate_username(username)
        leagues = get_leagues_by_username(username)
        return [league.to_dict() for league in leagues]

    @staticmethod
    def join_league(joinCode, username, playerName):
        """
        Allow a user to join an existing league using a join code.

        Validates the join code, finds the league, and creates a new player for the user
        in that league.

        Args:
            joinCode (str): The unique join code for the league.
            username (str): The username of the user joining.
            playerName (str): The player name to use in this league.

        Returns:
            dict: A success message if the user joins successfully.

        Raises:
            400: If validation fails for any input.
            404: If the league with the join code doesn't exist.
        """
        # Validate inputs
        joinCode = validate_join_code(joinCode)
        username = validate_username(username)
        playerName = validate_player_name(playerName)

        league = get_league_by_join_code(joinCode)
        validate_league_exists(league)

        leagueName = league.league_name

        try:
            new_player = PlayerService.create_player(playerName, username, leagueName)

            league.league_players.append(new_player)
            db.session.add(new_player)
            db.session.commit()
            return {"message": "Successfully joined league."}
        except Exception as error:
            print(f"Error: {error}")

    @staticmethod
    def delete_player(playerName, leagueName):
        """
        Remove a player from a league.

        Validates the player and league exist, removes the player from the league,
        and handles commissioner reassignment if the deleted player was the commissioner.

        Args:
            playerName (str): The name of the player to remove.
            leagueName (str): The name of the league to remove the player from.

        Returns:
            dict: A success message if the player is deleted successfully.

        Raises:
            400: If validation fails for playerName or leagueName.
            404: If the league, player, or user doesn't exist.
        """
        # Validate inputs
        playerName = validate_player_name(playerName)
        leagueName = validate_league_name(leagueName)

        print("reached player delete")
        league = get_league_by_name(leagueName)
        validate_league_exists(league)

        player = get_player_by_playername_and_leaguename(playerName, leagueName)
        validate_player_exists(player)

        user = player.user
        validate_user_exists(user)

        if (league.commissioner is player):
            league.commissioner = None
            league.commissioner_id = None

        league.league_players.remove(player)

        #user.user_players.remove(player)

        db.session.delete(player)
        db.session.commit()

        return {"message": "Player deleted successfully."}

    @staticmethod
    def delete_game(leagueName, game_id):
        """
        Delete a game and all associated props and answers from a league.

        Removes all winner/loser prop answers, over/under prop answers, and the props themselves
        before deleting the game. Note: Variable option prop deletion is not yet implemented.

        Args:
            leagueName (str): The name of the league containing the game.
            game_id (int): The unique identifier of the game to delete.

        Returns:
            None

        Raises:
            400: If validation fails for leagueName or game_id.
            404: If the league or game doesn't exist.
        """
        # Validate inputs
        leagueName = validate_league_name(leagueName)
        game_id = validate_game_id(game_id)

        league = get_league_by_name(leagueName)
        validate_league_exists(league)

        game = get_game_by_id(game_id)
        validate_game_exists(game)

        # First, remove all the answers associated with the winner/loser props
        for winnerLoserProp in game.winner_loser_props:
            # Delete all answers associated with this prop
            winnerLoserAnswers = WinnerLoserAnswer.query.filter_by(prop_id=winnerLoserProp.id).all()
            for answer in winnerLoserAnswers:
                db.session.delete(answer)
                db.session.commit()

            # Delete the winnerLoserProp after removing the answers
            db.session.delete(winnerLoserProp)
            db.session.commit()

        # Then, remove all the answers associated with the over/under props
        for overUnderProp in game.over_under_props:
            # Delete all answers associated with this prop
            overUnderAnswers = OverUnderAnswer.query.filter_by(prop_id=overUnderProp.id).all()
            for answer in overUnderAnswers:
                db.session.delete(answer)
                db.session.commit()

            # Delete the overUnderProp after removing the answers
            db.session.delete(overUnderProp)
            db.session.commit()

        # DELETE EVERYTHING IN THE VARIABLEOPTIONPROP
        ######
        ######
        ######
        ######
        ######
        ######

        # Finally, delete the game
        db.session.delete(game)
        db.session.commit()

    @staticmethod
    def delete_league(leagueName):
        """
        Delete a league and all associated games and players.

        Removes all games in the league (which cascades to delete all props and answers),
        removes all players, then deletes the league itself.

        Args:
            leagueName (str): The name of the league to delete.

        Returns:
            dict: A success message if the league is deleted successfully.

        Raises:
            400: If leagueName validation fails.
            404: If the league doesn't exist.
        """
        # Validate inputs
        leagueName = validate_league_name(leagueName)

        league = get_league_by_name(leagueName)
        validate_league_exists(league)

        for game in league.league_games:
            LeagueService.delete_game(leagueName, game.id)

        for player in league.league_players:
            LeagueService.delete_player(player.name, leagueName)

        db.session.delete(league)
        db.session.commit()

        return {"message": "League deleted successfully."}
