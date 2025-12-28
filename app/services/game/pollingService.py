"""
Polling Service for live NFL game updates.

This service manages the periodic polling of ESPN API for live game data,
updating prop values and game scores in real-time, and triggering auto-grading
when games complete.
"""

from datetime import datetime, timezone
from typing import List, Optional
from app import db
from app.models.gameModel import Game
from app.models.props.overUnderProp import OverUnderProp
from app.models.props.winnerLoserProp import WinnerLoserProp
from app.services.espnClientService import ESPNClientService
from app.services.game.gradeGameService import GradeGameService


class PollingService:
    """
    Service class for polling live NFL game data and updating prop values.

    This service queries the database for games that should be actively polled,
    fetches live data from ESPN, updates prop current values, and triggers
    auto-grading when games complete.
    """

    @staticmethod
    def get_games_to_poll() -> List[Game]:
        """
        Query database for games that should be actively polled.

        Returns games where:
        - start_time has passed (game has started)
        - is_completed is False (game is not finished)
        - external_game_id is set (we have an ESPN game ID to poll)

        Returns:
            list: List of Game objects that need to be polled.
        """
        now = datetime.now(timezone.utc)
        games = Game.query.filter(
            Game.start_time <= now,
            Game.is_completed == False,  # noqa: E712
            Game.external_game_id.isnot(None)
        ).all()
        return games

    @staticmethod
    def poll_game(game: Game) -> bool:
        """
        Poll ESPN API for a single game and update database with live data.

        This method:
        1. Fetches live game data from ESPN
        2. Updates game scores
        3. Updates all Over/Under prop current values
        4. Updates all Winner/Loser prop scores
        5. Checks if game is completed
        6. Triggers auto-grading if game has ended

        Args:
            game (Game): The game object to poll.

        Returns:
            bool: True if polling succeeded, False if ESPN request failed.
        """
        if not game.external_game_id:
            return False

        # Fetch live data from ESPN
        game_data = ESPNClientService.get_game_data(game.external_game_id)
        if not game_data:
            print(f"Failed to fetch data for game {game.id} ({game.game_name})")
            return False

        # Mark game as actively polling if not already
        if not game.is_polling:
            game.is_polling = True

        # Update game-level scores
        scores = ESPNClientService.get_team_scores(game_data)
        if scores:
            # Get full team names from ESPN to match with our team_a_name/team_b_name
            team_names_map = ESPNClientService.get_team_names(game_data)

            # Try to match scores to team_a and team_b based on winner/loser prop team names
            if game.winner_loser_props:
                prop = game.winner_loser_props[0]  # Use first winner/loser prop as reference
                if prop.team_a_name and prop.team_b_name:
                    # Match team names to ESPN team IDs
                    for team_id, score in scores.items():
                        team_full_name = team_names_map.get(team_id, "")
                        if prop.team_a_name in team_full_name or team_full_name in prop.team_a_name:
                            game.team_a_score = score
                        elif prop.team_b_name in team_full_name or team_full_name in prop.team_b_name:
                            game.team_b_score = score
                else:
                    # Fallback: just assign in order
                    team_ids = list(scores.keys())
                    if len(team_ids) >= 2:
                        game.team_a_score = scores.get(team_ids[0], 0)
                        game.team_b_score = scores.get(team_ids[1], 0)
            else:
                # No winner/loser props, just assign in order
                team_ids = list(scores.keys())
                if len(team_ids) >= 2:
                    game.team_a_score = scores.get(team_ids[0], 0)
                    game.team_b_score = scores.get(team_ids[1], 0)

        # Update Over/Under props
        PollingService._update_over_under_props(game, game_data)

        # Update Winner/Loser props
        PollingService._update_winner_loser_props(game, game_data, scores)

        # Check if game is completed
        if ESPNClientService.is_game_completed(game_data):
            print(f"Game {game.id} ({game.game_name}) has completed. Triggering auto-grading...")
            game.is_completed = True
            game.is_polling = False

            # Trigger auto-grading
            try:
                # First, auto-set correct answers based on live data
                GradeGameService.auto_grade_props_from_live_data(game)
                # Then grade the game
                GradeGameService.grade_game(game.id)
                print(f"Auto-grading completed for game {game.id}")
            except Exception as e:
                print(f"Error during auto-grading for game {game.id}: {e}")

        # Commit all changes
        db.session.commit()
        return True

    @staticmethod
    def _update_over_under_props(game: Game, game_data: dict) -> None:
        """
        Update current_value for all Over/Under props associated with a game.

        Args:
            game (Game): The game object.
            game_data (dict): Live game data from ESPN.
        """
        for prop in game.over_under_props:
            if not prop.player_name or not prop.stat_type:
                continue  # Skip props without player/stat info

            current_value = ESPNClientService.get_player_stats(
                game_data,
                prop.player_name,
                prop.stat_type
            )

            if current_value is not None:
                prop.current_value = current_value
                print(f"Updated {prop.player_name} {prop.stat_type}: {current_value}")

    @staticmethod
    def _update_winner_loser_props(game: Game, game_data: dict, scores: dict) -> None:
        """
        Update scores and winning_team_id for all Winner/Loser props.

        Args:
            game (Game): The game object.
            game_data (dict): Live game data from ESPN.
            scores (dict): Dictionary of team scores from ESPN.
        """
        for prop in game.winner_loser_props:
            # Try to update using team IDs first
            if prop.team_a_id and prop.team_a_id in scores:
                prop.team_a_score = scores[prop.team_a_id]
            elif game.team_a_score is not None:
                # Fallback: use game-level scores if team IDs not set
                prop.team_a_score = game.team_a_score

            if prop.team_b_id and prop.team_b_id in scores:
                prop.team_b_score = scores[prop.team_b_id]
            elif game.team_b_score is not None:
                # Fallback: use game-level scores if team IDs not set
                prop.team_b_score = game.team_b_score

            # If game is completed, set the winning team
            if ESPNClientService.is_game_completed(game_data):
                winning_team_id = ESPNClientService.get_winning_team_id(game_data)
                if winning_team_id:
                    prop.winning_team_id = winning_team_id
                    print(f"Set winning team for prop {prop.id}: {winning_team_id}")

    @staticmethod
    def poll_all_active_games() -> dict:
        """
        Poll all games that should be actively monitored.

        This is the main method called by the scheduler every 1-3 minutes.
        It queries for active games and polls each one.

        Returns:
            dict: Summary of polling results with counts of:
                  - games_polled: Number of games successfully polled
                  - games_failed: Number of games that failed to poll
                  - games_completed: Number of games that finished this poll
        """
        print(f"[POLLING] Checking for active games at {datetime.now(timezone.utc)}")
        games = PollingService.get_games_to_poll()

        if not games:
            print("[POLLING] No active games to poll at this time")
            return {
                "games_polled": 0,
                "games_failed": 0,
                "games_completed": 0
            }

        print(f"[POLLING] Found {len(games)} game(s) to poll")
        polled_count = 0
        failed_count = 0
        completed_count = 0

        for game in games:
            print(f"[POLLING] Polling game {game.id}: {game.game_name}")
            was_completed = game.is_completed
            success = PollingService.poll_game(game)

            if success:
                polled_count += 1
                # Check if game just completed
                if not was_completed and game.is_completed:
                    completed_count += 1
            else:
                failed_count += 1

        print(f"[POLLING] Polling complete: {polled_count} polled, {failed_count} failed, {completed_count} completed")

        return {
            "games_polled": polled_count,
            "games_failed": failed_count,
            "games_completed": completed_count
        }

    @staticmethod
    def manually_trigger_poll(game_id: int) -> dict:
        """
        Manually trigger a poll for a specific game (useful for testing/debugging).

        Args:
            game_id (int): The ID of the game to poll.

        Returns:
            dict: Result with 'success' boolean and optional 'error' message.

        Raises:
            404: If game is not found.
        """
        game = Game.query.get(game_id)
        if not game:
            return {"success": False, "error": "Game not found"}

        if not game.external_game_id:
            return {"success": False, "error": "Game does not have an external_game_id"}

        success = PollingService.poll_game(game)

        if success:
            return {"success": True, "message": f"Successfully polled game {game_id}"}
        else:
            return {"success": False, "error": "Failed to fetch game data from ESPN"}
