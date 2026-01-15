from flask import abort
from app.models.playerModel import Player
from app.repositories.playerRepository import get_all_players, get_player_by_id, get_player_by_username_and_leaguename
from app.repositories.leagueRepository import get_league_by_name
from app.repositories.usersRepository import get_user_by_username
from app import db
from app.validators.leagueValidator import validate_league_name, validate_league_exists, validate_player_name, validate_player_exists
from app.validators.userValidator import validate_username, validate_user_exists


class PlayerService:
    """
    Service class for handling player-related business logic.

    This class manages player creation, retrieval of player standings,
    and modification of player points within leagues.
    """

    @staticmethod
    def create_player(playerName, username, leaguename):
        """
        Create a new player in a specific league.

        Validates the player name, username, and league name, then creates a new player
        associated with a user and league. Ensures the player name is unique within the league.

        Args:
            playerName (str): The display name for the player in the league.
            username (str): The username of the user creating this player.
            leaguename (str): The name of the league to join.

        Returns:
            Player: The newly created player object (not yet committed to database).

        Raises:
            400: If validation fails for playerName, username, or leaguename.
            404: If the league or user doesn't exist.
            409: If a player with the same name already exists in the league.
        """
        # Validate inputs
        playerName = validate_player_name(playerName)
        username = validate_username(username)
        leaguename = validate_league_name(leaguename)

        league = get_league_by_name(leaguename)
        validate_league_exists(league)

        user = get_user_by_username(username)
        validate_user_exists(user)

        for player in league.league_players:
            if (player.name == playerName):
                abort(409, "Already exists someone in the league with this player name. Choose another player name")

        new_player = Player(
            name = playerName,
            user_id = user.id,
            points = 0,
        )

        new_player.league_id = league.id
        new_player.league = league


        return new_player

    @staticmethod
    def get_player_standings(leagueName):
        """
        Retrieve player standings for a specific league.

        Gets all players in a league along with their points and ranking information.

        Args:
            leagueName (str): The name of the league to retrieve standings for.

        Returns:
            dict: A dictionary containing league information including all players and their standings.

        Raises:
            400: If leagueName validation fails.
            404: If the league doesn't exist.
        """
        leagueName = validate_league_name(leagueName)
        league = get_league_by_name(leagueName)
        validate_league_exists(league)

        return league.to_dict()

    @staticmethod
    def edit_points(player_id, new_points):
        """
        Update the points for a specific player.

        Modifies the point total for a player, typically used for manual adjustments
        or corrections by league commissioners.

        Args:
            player_id (int): The unique identifier of the player to update.
            new_points (int/float): The new point total to set for the player.

        Returns:
            None

        Raises:
            404: If the player doesn't exist.
        """
        player = get_player_by_id(player_id)
        validate_player_exists(player)

        player.points = new_points

        db.session.commit()

    @staticmethod
    def get_player_by_username_and_leaguename(username, leaguename):
        """
        Get a player by username and league name.

        Args:
            username (str): The username of the user.
            leaguename (str): The name of the league.

        Returns:
            Player: The player object if found, None otherwise.

        Raises:
            400: If validation fails.
            404: If the player doesn't exist.
        """
        username = validate_username(username)
        leaguename = validate_league_name(leaguename)

        player = get_player_by_username_and_leaguename(username, leaguename)
        validate_player_exists(player)

        return player
