"""
ESPN Client Service for fetching live NFL game data.

This service provides methods to interact with ESPN's public JSON API
for retrieving live game data, scores, and player statistics.
"""

import requests
from typing import Dict, List, Optional, Any


class ESPNClientService:
    """
    Service class for interacting with ESPN's public NFL API.

    This service fetches live game data including scores, game status,
    and player statistics without requiring authentication.
    """

    BASE_URL = "https://site.api.espn.com/apis/site/v2/sports/football/nfl"

    @staticmethod
    def get_game_data(external_game_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch live game data from ESPN API for a specific game.

        Args:
            external_game_id (str): The ESPN game ID to fetch data for.

        Returns:
            dict: Game data including status, scores, and statistics if successful.
            None: If the request fails or game is not found.

        Raises:
            requests.RequestException: If the HTTP request fails.
        """
        try:
            url = f"{ESPNClientService.BASE_URL}/summary"
            params = {"event": external_game_id}
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching game data for {external_game_id}: {e}")
            return None

    @staticmethod
    def get_game_status(game_data: Dict[str, Any]) -> Optional[str]:
        """
        Extract the game status from ESPN game data.

        Args:
            game_data (dict): The game data returned from get_game_data().

        Returns:
            str: Game status (e.g., "STATUS_IN_PROGRESS", "STATUS_FINAL", "STATUS_SCHEDULED").
            None: If status cannot be determined.
        """
        try:
            return game_data.get("header", {}).get("competitions", [{}])[0].get("status", {}).get("type", {}).get("name")
        except (IndexError, KeyError, TypeError):
            return None

    @staticmethod
    def is_game_completed(game_data: Dict[str, Any]) -> bool:
        """
        Check if a game has finished based on ESPN game data.

        Args:
            game_data (dict): The game data returned from get_game_data().

        Returns:
            bool: True if game status is "STATUS_FINAL", False otherwise.
        """
        status = ESPNClientService.get_game_status(game_data)
        return status == "STATUS_FINAL"

    @staticmethod
    def is_game_in_progress(game_data: Dict[str, Any]) -> bool:
        """
        Check if a game is currently in progress based on ESPN game data.

        Args:
            game_data (dict): The game data returned from get_game_data().

        Returns:
            bool: True if game status is "STATUS_IN_PROGRESS", False otherwise.
        """
        status = ESPNClientService.get_game_status(game_data)
        return status == "STATUS_IN_PROGRESS"

    @staticmethod
    def get_team_scores(game_data: Dict[str, Any]) -> Dict[str, int]:
        """
        Extract current scores for both teams from ESPN game data.

        Args:
            game_data (dict): The game data returned from get_game_data().

        Returns:
            dict: Dictionary with team IDs as keys and scores as values.
                  Example: {"BAL": 28, "KC": 24}
                  Returns empty dict if scores cannot be extracted.
        """
        try:
            competitors = game_data.get("header", {}).get("competitions", [{}])[0].get("competitors", [])
            scores = {}
            for team in competitors:
                team_id = team.get("team", {}).get("abbreviation")
                score = int(team.get("score", 0))
                if team_id:
                    scores[team_id] = score
            return scores
        except (IndexError, KeyError, TypeError, ValueError):
            return {}

    @staticmethod
    def get_team_names(game_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Extract team abbreviations to full team names mapping from ESPN game data.

        Args:
            game_data (dict): The game data returned from get_game_data().

        Returns:
            dict: Dictionary with team abbreviations as keys and full names as values.
                  Example: {"JAX": "Jacksonville Jaguars", "IND": "Indianapolis Colts"}
        """
        try:
            competitors = game_data.get("header", {}).get("competitions", [{}])[0].get("competitors", [])
            team_names = {}
            for team in competitors:
                team_id = team.get("team", {}).get("abbreviation")
                team_name = team.get("team", {}).get("displayName")
                if team_id and team_name:
                    team_names[team_id] = team_name
            return team_names
        except (IndexError, KeyError, TypeError):
            return {}

    @staticmethod
    def get_winning_team_id(game_data: Dict[str, Any]) -> Optional[str]:
        """
        Determine the winning team ID from completed game data.

        Args:
            game_data (dict): The game data returned from get_game_data().

        Returns:
            str: The abbreviation of the winning team (e.g., "BAL", "KC").
            None: If game is not completed or winner cannot be determined.
        """
        if not ESPNClientService.is_game_completed(game_data):
            return None

        scores = ESPNClientService.get_team_scores(game_data)
        if not scores or len(scores) < 2:
            return None

        # Find team with highest score
        winning_team = max(scores.items(), key=lambda x: x[1])
        return winning_team[0]

    @staticmethod
    def get_player_stats(game_data: Dict[str, Any], player_name: str, stat_type: str) -> Optional[float]:
        """
        Extract a specific player's stat from ESPN game data.

        Args:
            game_data (dict): The game data returned from get_game_data().
            player_name (str): The player's name to search for (e.g., "Zay Flowers").
            stat_type (str): The type of stat to retrieve. Supported values:
                - "passing_yards", "passing_tds", "passing_interceptions", "passing_completions"
                - "rushing_yards", "rushing_tds"
                - "receiving_yards", "receiving_tds", "receiving_receptions"

        Returns:
            float: The stat value for the player.
            None: If player or stat is not found.
        """
        try:
            # Map our stat types to ESPN's stat category names
            stat_category_map = {
                "passing_yards": ("passing", "passingYards"),
                "passing_tds": ("passing", "passingTouchdowns"),
                "passing_interceptions": ("passing", "interceptions"),
                "passing_completions": ("passing", "completions"),
                "rushing_yards": ("rushing", "rushingYards"),
                "rushing_tds": ("rushing", "rushingTouchdowns"),
                "receiving_yards": ("receiving", "receivingYards"),
                "receiving_tds": ("receiving", "receivingTouchdowns"),
                "receiving_receptions": ("receiving", "receptions"),
            }

            if stat_type not in stat_category_map:
                return None

            category, stat_key = stat_category_map[stat_type]

            # Navigate through ESPN's JSON structure to find player stats
            box_score = game_data.get("boxscore", {})
            players = box_score.get("players", [])

            # Search through both teams' player lists
            for team in players:
                statistics = team.get("statistics", [])

                # Find the correct stat category (passing, rushing, or receiving)
                for stat_group in statistics:
                    if stat_group.get("name", "").lower() == category:
                        athletes = stat_group.get("athletes", [])

                        # Search for the player by name
                        for athlete in athletes:
                            athlete_name = athlete.get("athlete", {}).get("displayName", "")
                            if athlete_name.lower() == player_name.lower():
                                # Find the specific stat in the athlete's stats
                                stats = athlete.get("stats", [])
                                stat_keys = stat_group.get("keys", [])

                                # Map stat keys to values
                                for idx, key in enumerate(stat_keys):
                                    if key == stat_key and idx < len(stats):
                                        return float(stats[idx])

            return None
        except (IndexError, KeyError, TypeError, ValueError):
            return None

    @staticmethod
    def get_scoreboard(date: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Fetch NFL scoreboard data for a specific date.

        Args:
            date (str, optional): Date in YYYYMMDD format (e.g., "20250115").
                                 If None, fetches current day's games.

        Returns:
            dict: Scoreboard data containing all games for the specified date.
            None: If the request fails.
        """
        try:
            url = f"{ESPNClientService.BASE_URL}/scoreboard"
            params = {"dates": date} if date else {}
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching scoreboard: {e}")
            return None

    @staticmethod
    def get_available_players(external_game_id: str, positions: Optional[List[str]] = None) -> List[Dict[str, str]]:
        """
        Get list of available players for a game from team rosters, optionally filtered by position.

        Args:
            external_game_id (str): The ESPN game ID.
            positions (list, optional): List of position abbreviations to filter by
                                       (e.g., ["QB", "RB", "WR", "TE"]).
                                       If None, returns all players.

        Returns:
            list: List of dictionaries containing player information:
                  [{"name": "Player Name", "id": "player_id", "position": "QB"}, ...]
                  Returns empty list if game not found or error occurs.
        """
        try:
            # Get game data to find the team IDs
            game_data = ESPNClientService.get_game_data(external_game_id)
            if not game_data:
                return []

            players = []

            # Get team IDs from the game
            competitors = game_data.get("header", {}).get("competitions", [{}])[0].get("competitors", [])

            # Fetch roster for each team
            for competitor in competitors:
                team_id = competitor.get("team", {}).get("id")
                if not team_id:
                    continue

                # Fetch team roster from ESPN's roster endpoint
                roster_url = f"{ESPNClientService.BASE_URL.replace('/summary', '')}/teams/{team_id}/roster"
                try:
                    roster_response = requests.get(roster_url, timeout=10)
                    roster_response.raise_for_status()
                    roster_data = roster_response.json()

                    # Parse roster data
                    athletes = roster_data.get("athletes", [])
                    for athlete_group in athletes:
                        items = athlete_group.get("items", [])
                        for athlete in items:
                            player_name = athlete.get("displayName")
                            player_id = athlete.get("id")
                            player_position = athlete.get("position", {}).get("abbreviation")

                            # Filter by position if specified
                            if positions and player_position not in positions:
                                continue

                            if player_name and player_id:
                                players.append({
                                    "name": player_name,
                                    "id": str(player_id),
                                    "position": player_position
                                })
                except requests.RequestException as e:
                    print(f"Error fetching roster for team {team_id}: {e}")
                    continue

            # Remove duplicates
            unique_players = {p["id"]: p for p in players}
            return list(unique_players.values())

        except (IndexError, KeyError, TypeError) as e:
            print(f"Error getting players for game {external_game_id}: {e}")
            return []
