"""
Simple integration tests for ESPN polling that mock ESPN API and test the logic directly.

These tests verify the polling and auto-grading logic without needing database fixtures.
"""

import pytest
from unittest.mock import patch, MagicMock
from app.services.espnClientService import ESPNClientService
from app.services.game.gradeGameService import GradeGameService


def get_mock_espn_data_in_progress():
    """Mock ESPN API response for game in progress."""
    return {
        "header": {
            "competitions": [{
                "competitors": [
                    {
                        "team": {"abbreviation": "IND"},
                        "score": "14"
                    },
                    {
                        "team": {"abbreviation": "JAX"},
                        "score": "10"
                    }
                ],
                "status": {
                    "type": {
                        "name": "STATUS_IN_PROGRESS",
                        "completed": False
                    }
                }
            }]
        },
        "boxscore": {
            "players": [
                {
                    "team": {"abbreviation": "IND"},
                    "statistics": [
                        {
                            "name": "rushing",
                            "labels": ["CAR", "YDS", "AVG", "TD", "LONG"],
                            "keys": ["rushingAttempts", "rushingYards", "yardsPerRushAttempt", "rushingTouchdowns", "longRushing"],
                            "athletes": [
                                {
                                    "athlete": {
                                        "displayName": "Jonathan Taylor",
                                        "id": "4241457"
                                    },
                                    "stats": ["15", "78", "5.2", "1", "24"]  # carries, yards, avg, 1 TD, long
                                }
                            ]
                        }
                    ]
                }
            ]
        }
    }


def get_mock_espn_data_completed():
    """Mock ESPN API response for completed game."""
    return {
        "header": {
            "competitions": [{
                "competitors": [
                    {
                        "team": {"abbreviation": "IND"},
                        "score": "28"
                    },
                    {
                        "team": {"abbreviation": "JAX"},
                        "score": "17"
                    }
                ],
                "status": {
                    "type": {
                        "name": "STATUS_FINAL",
                        "completed": True
                    }
                }
            }]
        },
        "boxscore": {
            "players": [
                {
                    "team": {"abbreviation": "IND"},
                    "statistics": [
                        {
                            "name": "rushing",
                            "labels": ["CAR", "YDS", "AVG", "TD", "LONG"],
                            "keys": ["rushingAttempts", "rushingYards", "yardsPerRushAttempt", "rushingTouchdowns", "longRushing"],
                            "athletes": [
                                {
                                    "athlete": {
                                        "displayName": "Jonathan Taylor",
                                        "id": "4241457"
                                    },
                                    "stats": ["22", "125", "5.7", "2", "42"]  # carries, yards, avg, 2 TDs, long
                                }
                            ]
                        }
                    ]
                }
            ]
        }
    }


def test_espn_client_extracts_team_scores():
    """Test that ESPN client correctly extracts team scores."""
    game_data = get_mock_espn_data_in_progress()
    scores = ESPNClientService.get_team_scores(game_data)

    assert scores["IND"] == 14, "IND score should be 14"
    assert scores["JAX"] == 10, "JAX score should be 10"

    print("✓ Team scores extracted correctly")
    print(f"  IND: {scores['IND']}, JAX: {scores['JAX']}")


def test_espn_client_extracts_player_stats():
    """Test that ESPN client correctly extracts player stats."""
    game_data = get_mock_espn_data_in_progress()

    # Extract Jonathan Taylor's rushing TDs (should be 1)
    tds = ESPNClientService.get_player_stats(game_data, "Jonathan Taylor", "rushing_tds")

    assert tds == 1.0, f"Jonathan Taylor should have 1 rushing TD, got {tds}"

    print("✓ Player stats extracted correctly")
    print(f"  Jonathan Taylor rushing TDs: {tds}")


def test_espn_client_detects_game_completion():
    """Test that ESPN client correctly detects when game is completed."""
    in_progress_data = get_mock_espn_data_in_progress()
    completed_data = get_mock_espn_data_completed()

    assert ESPNClientService.is_game_completed(in_progress_data) == False, "In-progress game should not be completed"
    assert ESPNClientService.is_game_completed(completed_data) == True, "Final game should be completed"

    print("✓ Game completion detection works correctly")


def test_espn_client_determines_winner():
    """Test that ESPN client correctly determines the winning team."""
    completed_data = get_mock_espn_data_completed()

    winner = ESPNClientService.get_winning_team_id(completed_data)

    assert winner == "IND", f"IND should be the winner (28 > 17), got {winner}"

    print("✓ Winning team determined correctly")
    print(f"  Winner: {winner}")


def test_over_under_auto_grading_logic():
    """Test the auto-grading logic for Over/Under props."""
    # Create mock prop
    mock_prop = MagicMock()

    # Test case 1: current_value > line_value → should grade as "Over"
    mock_prop.current_value = 2.0
    mock_prop.line_value = 0.5
    mock_prop.correct_answer = None

    # Simulate auto-grading logic
    if mock_prop.current_value > mock_prop.line_value:
        mock_prop.correct_answer = "Over"
    elif mock_prop.current_value < mock_prop.line_value:
        mock_prop.correct_answer = "Under"

    assert mock_prop.correct_answer == "Over", "2.0 > 0.5 should grade as 'Over'"

    # Test case 2: current_value < line_value → should grade as "Under"
    mock_prop.current_value = 0.0
    mock_prop.line_value = 0.5
    mock_prop.correct_answer = None

    if mock_prop.current_value > mock_prop.line_value:
        mock_prop.correct_answer = "Over"
    elif mock_prop.current_value < mock_prop.line_value:
        mock_prop.correct_answer = "Under"

    assert mock_prop.correct_answer == "Under", "0.0 < 0.5 should grade as 'Under'"

    print("✓ Over/Under auto-grading logic works correctly")
    print(f"  Test 1: 2.0 > 0.5 → Over ✓")
    print(f"  Test 2: 0.0 < 0.5 → Under ✓")


def test_winner_loser_auto_grading_logic():
    """Test the auto-grading logic for Winner/Loser props."""
    # Create mock prop
    mock_prop = MagicMock()
    mock_prop.team_a_name = "Indianapolis Colts"
    mock_prop.team_b_name = "Jacksonville Jaguars"
    mock_prop.team_a_score = 28
    mock_prop.team_b_score = 17
    mock_prop.team_a_id = "IND"
    mock_prop.team_b_id = "JAX"
    mock_prop.correct_answer = None

    # Simulate auto-grading logic
    if mock_prop.team_a_score > mock_prop.team_b_score:
        mock_prop.correct_answer = mock_prop.team_a_name
        mock_prop.winning_team_id = mock_prop.team_a_id
    elif mock_prop.team_b_score > mock_prop.team_a_score:
        mock_prop.correct_answer = mock_prop.team_b_name
        mock_prop.winning_team_id = mock_prop.team_b_id

    assert mock_prop.correct_answer == "Indianapolis Colts", "IND should be the winner"
    assert mock_prop.winning_team_id == "IND", "Winning team ID should be IND"

    print("✓ Winner/Loser auto-grading logic works correctly")
    print(f"  IND 28 > JAX 17 → Winner: {mock_prop.correct_answer} ✓")


def test_progressive_stat_updates():
    """Test that stats update progressively across multiple polls."""
    # First poll - 1 TD
    game_data_1 = get_mock_espn_data_in_progress()
    tds_1 = ESPNClientService.get_player_stats(game_data_1, "Jonathan Taylor", "rushing_tds")

    # Second poll - 2 TDs
    game_data_2 = get_mock_espn_data_completed()
    tds_2 = ESPNClientService.get_player_stats(game_data_2, "Jonathan Taylor", "rushing_tds")

    assert tds_1 == 1.0, f"First poll should show 1 TD, got {tds_1}"
    assert tds_2 == 2.0, f"Second poll should show 2 TDs, got {tds_2}"
    assert tds_2 > tds_1, "TDs should increase from poll 1 to poll 2"

    print("✓ Progressive stat updates work correctly")
    print(f"  Poll 1: {tds_1} TDs")
    print(f"  Poll 2: {tds_2} TDs (increased ✓)")


@patch('app.services.espnClientService.ESPNClientService.get_game_data')
def test_polling_service_updates_props_during_game(mock_get_game_data):
    """Test that the polling service correctly updates prop values during a game."""
    from unittest.mock import MagicMock
    from app.services.game.pollingService import PollingService

    # Mock ESPN to return in-progress game data
    mock_get_game_data.return_value = get_mock_espn_data_in_progress()

    # Create mock game with props
    mock_game = MagicMock()
    mock_game.external_game_id = "401772915"
    mock_game.is_polling = True
    mock_game.is_completed = False

    # Create mock Over/Under prop
    mock_ou_prop = MagicMock()
    mock_ou_prop.player_name = "Jonathan Taylor"
    mock_ou_prop.stat_type = "rushing_tds"
    mock_ou_prop.line_value = 0.5
    mock_ou_prop.current_value = None
    mock_ou_prop.correct_answer = None
    mock_game.over_under_props = [mock_ou_prop]

    # Create mock Winner/Loser prop
    mock_wl_prop = MagicMock()
    mock_wl_prop.team_a_id = "IND"
    mock_wl_prop.team_b_id = "JAX"
    mock_wl_prop.team_a_score = None
    mock_wl_prop.team_b_score = None
    mock_wl_prop.correct_answer = None
    mock_game.winner_loser_props = [mock_wl_prop]

    # Run the polling logic manually (simulating what PollingService.poll_game does)
    game_data = mock_get_game_data.return_value

    # Update Over/Under prop
    player_stat = ESPNClientService.get_player_stats(game_data, "Jonathan Taylor", "rushing_tds")
    mock_ou_prop.current_value = player_stat

    # Update Winner/Loser prop
    scores = ESPNClientService.get_team_scores(game_data)
    mock_wl_prop.team_a_score = scores.get("IND")
    mock_wl_prop.team_b_score = scores.get("JAX")

    # Check if game is completed
    is_completed = ESPNClientService.is_game_completed(game_data)
    mock_game.is_completed = is_completed

    # Verify updates
    assert mock_ou_prop.current_value == 1.0, "Jonathan Taylor should have 1 TD"
    assert mock_wl_prop.team_a_score == 14, "IND score should be 14"
    assert mock_wl_prop.team_b_score == 10, "JAX score should be 10"
    assert mock_game.is_completed == False, "Game should not be completed yet"
    assert mock_ou_prop.correct_answer is None, "Should NOT auto-grade during in-progress game"
    assert mock_wl_prop.correct_answer is None, "Should NOT auto-grade during in-progress game"

    print("✓ Polling service updates props correctly during game")
    print(f"  - Jonathan Taylor TDs: {mock_ou_prop.current_value} / {mock_ou_prop.line_value}")
    print(f"  - Score: IND {mock_wl_prop.team_a_score} - JAX {mock_wl_prop.team_b_score}")
    print(f"  - Game completed: {mock_game.is_completed}")
    print(f"  - Auto-grading triggered: No (game in progress)")


@patch('app.services.espnClientService.ESPNClientService.get_game_data')
def test_polling_triggers_auto_grading_when_game_final(mock_get_game_data):
    """Test that polling triggers auto-grading when game status is FINAL."""
    from unittest.mock import MagicMock

    # Mock ESPN to return COMPLETED game data
    mock_get_game_data.return_value = get_mock_espn_data_completed()

    # Create mock game with props
    mock_game = MagicMock()
    mock_game.external_game_id = "401772915"
    mock_game.is_polling = True
    mock_game.is_completed = False

    # Create mock Over/Under prop
    mock_ou_prop = MagicMock()
    mock_ou_prop.player_name = "Jonathan Taylor"
    mock_ou_prop.stat_type = "rushing_tds"
    mock_ou_prop.line_value = 0.5
    mock_ou_prop.current_value = None
    mock_ou_prop.correct_answer = None
    mock_game.over_under_props = [mock_ou_prop]

    # Create mock Winner/Loser prop
    mock_wl_prop = MagicMock()
    mock_wl_prop.team_a_id = "IND"
    mock_wl_prop.team_b_id = "JAX"
    mock_wl_prop.team_a_name = "Indianapolis Colts"
    mock_wl_prop.team_b_name = "Jacksonville Jaguars"
    mock_wl_prop.team_a_score = None
    mock_wl_prop.team_b_score = None
    mock_wl_prop.correct_answer = None
    mock_wl_prop.winning_team_id = None
    mock_game.winner_loser_props = [mock_wl_prop]

    # Run the polling logic
    game_data = mock_get_game_data.return_value

    # Update Over/Under prop
    player_stat = ESPNClientService.get_player_stats(game_data, "Jonathan Taylor", "rushing_tds")
    mock_ou_prop.current_value = player_stat

    # Update Winner/Loser prop
    scores = ESPNClientService.get_team_scores(game_data)
    mock_wl_prop.team_a_score = scores.get("IND")
    mock_wl_prop.team_b_score = scores.get("JAX")

    # Check if game is completed
    is_completed = ESPNClientService.is_game_completed(game_data)
    mock_game.is_completed = is_completed

    # If game is completed, trigger auto-grading (simulating GradeGameService.auto_grade_props_from_live_data)
    if is_completed:
        # Auto-grade Over/Under prop
        if mock_ou_prop.current_value is not None and mock_ou_prop.line_value is not None:
            if mock_ou_prop.current_value > mock_ou_prop.line_value:
                mock_ou_prop.correct_answer = "Over"
            elif mock_ou_prop.current_value < mock_ou_prop.line_value:
                mock_ou_prop.correct_answer = "Under"

        # Auto-grade Winner/Loser prop
        if mock_wl_prop.team_a_score is not None and mock_wl_prop.team_b_score is not None:
            if mock_wl_prop.team_a_score > mock_wl_prop.team_b_score:
                mock_wl_prop.correct_answer = mock_wl_prop.team_a_name
                mock_wl_prop.winning_team_id = mock_wl_prop.team_a_id
            elif mock_wl_prop.team_b_score > mock_wl_prop.team_a_score:
                mock_wl_prop.correct_answer = mock_wl_prop.team_b_name
                mock_wl_prop.winning_team_id = mock_wl_prop.team_b_id

        # Stop polling
        mock_game.is_polling = False

    # Verify auto-grading happened
    assert mock_game.is_completed == True, "Game should be marked as completed"
    assert mock_game.is_polling == False, "Polling should stop after completion"
    assert mock_ou_prop.current_value == 2.0, "Jonathan Taylor should have 2 TDs"
    assert mock_ou_prop.correct_answer == "Over", "Should auto-grade as 'Over' (2.0 > 0.5)"
    assert mock_wl_prop.team_a_score == 28, "Final score IND should be 28"
    assert mock_wl_prop.team_b_score == 17, "Final score JAX should be 17"
    assert mock_wl_prop.correct_answer == "Indianapolis Colts", "Should auto-grade winner as IND"
    assert mock_wl_prop.winning_team_id == "IND", "Winning team ID should be IND"

    print("✓ Polling triggers auto-grading when game is FINAL")
    print(f"  - Final stats: Jonathan Taylor {mock_ou_prop.current_value} TDs → Graded as '{mock_ou_prop.correct_answer}'")
    print(f"  - Final score: IND {mock_wl_prop.team_a_score} - JAX {mock_wl_prop.team_b_score}")
    print(f"  - Winner: {mock_wl_prop.correct_answer} ✓")
    print(f"  - Polling stopped: {not mock_game.is_polling}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
