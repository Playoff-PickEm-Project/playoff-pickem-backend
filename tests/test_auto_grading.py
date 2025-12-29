"""
Unit tests for auto-grading logic.

Tests the auto_grade_props_from_live_data function with various scenarios
to ensure correct answers are set properly for both over/under and winner/loser props.
"""

import unittest
from unittest.mock import Mock, MagicMock, patch
from app.services.game.gradeGameService import GradeGameService


class TestAutoGrading(unittest.TestCase):
    """Test cases for auto-grading functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_game = Mock()
        self.mock_game.over_under_props = []
        self.mock_game.winner_loser_props = []

    def test_over_under_over_case(self):
        """Test over/under prop when current > line (should be 'over')."""
        prop = Mock()
        prop.id = 1
        prop.current_value = 150.0
        prop.line_value = 100.0
        prop.correct_answer = None

        self.mock_game.over_under_props = [prop]

        with patch('app.services.game.gradeGameService.db'):
            GradeGameService.auto_grade_props_from_live_data(self.mock_game)

        self.assertEqual(prop.correct_answer, "over")

    def test_over_under_under_case(self):
        """Test over/under prop when current < line (should be 'under')."""
        prop = Mock()
        prop.id = 1
        prop.current_value = 50.0
        prop.line_value = 100.0
        prop.correct_answer = None

        self.mock_game.over_under_props = [prop]

        with patch('app.services.game.gradeGameService.db'):
            GradeGameService.auto_grade_props_from_live_data(self.mock_game)

        self.assertEqual(prop.correct_answer, "under")

    def test_over_under_exact_match(self):
        """Test over/under prop when current == line (should be None/push)."""
        prop = Mock()
        prop.id = 1
        prop.current_value = 100.0
        prop.line_value = 100.0
        prop.correct_answer = None

        self.mock_game.over_under_props = [prop]

        with patch('app.services.game.gradeGameService.db'):
            GradeGameService.auto_grade_props_from_live_data(self.mock_game)

        # Should remain None for a push
        self.assertIsNone(prop.correct_answer)

    def test_over_under_missing_data(self):
        """Test over/under prop when data is missing (should skip)."""
        prop = Mock()
        prop.id = 1
        prop.current_value = None
        prop.line_value = 100.0
        prop.correct_answer = None

        self.mock_game.over_under_props = [prop]

        with patch('app.services.game.gradeGameService.db'):
            GradeGameService.auto_grade_props_from_live_data(self.mock_game)

        # Should remain None when data is missing
        self.assertIsNone(prop.correct_answer)

    def test_winner_loser_team_a_wins(self):
        """Test winner/loser prop when team A wins."""
        prop = Mock()
        prop.id = 1
        prop.team_a_name = "Jacksonville Jaguars"
        prop.team_b_name = "Indianapolis Colts"
        prop.team_a_score = 23
        prop.team_b_score = 17
        prop.correct_answer = None

        self.mock_game.winner_loser_props = [prop]

        with patch('app.services.game.gradeGameService.db'):
            GradeGameService.auto_grade_props_from_live_data(self.mock_game)

        self.assertEqual(prop.correct_answer, "Jacksonville Jaguars")

    def test_winner_loser_team_b_wins(self):
        """Test winner/loser prop when team B wins."""
        prop = Mock()
        prop.id = 1
        prop.team_a_name = "Green Bay Packers"
        prop.team_b_name = "Baltimore Ravens"
        prop.team_a_score = 24
        prop.team_b_score = 41
        prop.correct_answer = None

        self.mock_game.winner_loser_props = [prop]

        with patch('app.services.game.gradeGameService.db'):
            GradeGameService.auto_grade_props_from_live_data(self.mock_game)

        self.assertEqual(prop.correct_answer, "Baltimore Ravens")

    def test_winner_loser_tie(self):
        """Test winner/loser prop when game is tied (should be None)."""
        prop = Mock()
        prop.id = 1
        prop.team_a_name = "Team A"
        prop.team_b_name = "Team B"
        prop.team_a_score = 20
        prop.team_b_score = 20
        prop.correct_answer = None

        self.mock_game.winner_loser_props = [prop]

        with patch('app.services.game.gradeGameService.db'):
            GradeGameService.auto_grade_props_from_live_data(self.mock_game)

        # Should remain None for a tie
        self.assertIsNone(prop.correct_answer)

    def test_winner_loser_missing_scores(self):
        """Test winner/loser prop when scores are missing (should skip)."""
        prop = Mock()
        prop.id = 1
        prop.team_a_name = "Team A"
        prop.team_b_name = "Team B"
        prop.team_a_score = None
        prop.team_b_score = 20
        prop.correct_answer = None

        self.mock_game.winner_loser_props = [prop]

        with patch('app.services.game.gradeGameService.db'):
            GradeGameService.auto_grade_props_from_live_data(self.mock_game)

        # Should remain None when data is missing
        self.assertIsNone(prop.correct_answer)

    def test_winner_loser_different_team_orders(self):
        """Test winner/loser with teams in different orders."""
        # Test case 1: Favorite is team_a
        prop1 = Mock()
        prop1.id = 1
        prop1.team_a_name = "Kansas City Chiefs"
        prop1.team_b_name = "Las Vegas Raiders"
        prop1.team_a_score = 31
        prop1.team_b_score = 17

        # Test case 2: Favorite is team_b
        prop2 = Mock()
        prop2.id = 2
        prop2.team_a_name = "Detroit Lions"
        prop2.team_b_name = "San Francisco 49ers"
        prop2.team_a_score = 21
        prop2.team_b_score = 34

        self.mock_game.winner_loser_props = [prop1, prop2]

        with patch('app.services.game.gradeGameService.db'):
            GradeGameService.auto_grade_props_from_live_data(self.mock_game)

        # Should use team_a_name when team A wins
        self.assertEqual(prop1.correct_answer, "Kansas City Chiefs")
        # Should use team_b_name when team B wins
        self.assertEqual(prop2.correct_answer, "San Francisco 49ers")

    def test_multiple_props_same_game(self):
        """Test auto-grading multiple props in the same game."""
        # Over/under prop 1 - over
        ou_prop1 = Mock()
        ou_prop1.id = 1
        ou_prop1.current_value = 250.0
        ou_prop1.line_value = 200.0

        # Over/under prop 2 - under
        ou_prop2 = Mock()
        ou_prop2.id = 2
        ou_prop2.current_value = 45.0
        ou_prop2.line_value = 60.5

        # Winner/loser prop
        wl_prop = Mock()
        wl_prop.id = 3
        wl_prop.team_a_name = "Home Team"
        wl_prop.team_b_name = "Away Team"
        wl_prop.team_a_score = 28
        wl_prop.team_b_score = 24

        self.mock_game.over_under_props = [ou_prop1, ou_prop2]
        self.mock_game.winner_loser_props = [wl_prop]

        with patch('app.services.game.gradeGameService.db'):
            GradeGameService.auto_grade_props_from_live_data(self.mock_game)

        self.assertEqual(ou_prop1.correct_answer, "over")
        self.assertEqual(ou_prop2.correct_answer, "under")
        self.assertEqual(wl_prop.correct_answer, "Home Team")

    def test_case_sensitivity(self):
        """Test that correct answers use lowercase for over/under."""
        prop = Mock()
        prop.id = 1
        prop.current_value = 100.5
        prop.line_value = 100.0

        self.mock_game.over_under_props = [prop]

        with patch('app.services.game.gradeGameService.db'):
            GradeGameService.auto_grade_props_from_live_data(self.mock_game)

        # Should be lowercase "over", not "Over"
        self.assertEqual(prop.correct_answer, "over")
        self.assertNotEqual(prop.correct_answer, "Over")

    def test_high_scoring_game(self):
        """Test with high scoring game to ensure no integer overflow issues."""
        prop = Mock()
        prop.id = 1
        prop.team_a_name = "High Scoring Team"
        prop.team_b_name = "Also High Scoring"
        prop.team_a_score = 52
        prop.team_b_score = 48

        self.mock_game.winner_loser_props = [prop]

        with patch('app.services.game.gradeGameService.db'):
            GradeGameService.auto_grade_props_from_live_data(self.mock_game)

        self.assertEqual(prop.correct_answer, "High Scoring Team")

    def test_low_scoring_game(self):
        """Test with low scoring game (defensive battle)."""
        prop = Mock()
        prop.id = 1
        prop.team_a_name = "Defense Team A"
        prop.team_b_name = "Defense Team B"
        prop.team_a_score = 3
        prop.team_b_score = 6

        self.mock_game.winner_loser_props = [prop]

        with patch('app.services.game.gradeGameService.db'):
            GradeGameService.auto_grade_props_from_live_data(self.mock_game)

        self.assertEqual(prop.correct_answer, "Defense Team B")

    def test_blowout_game(self):
        """Test with blowout game (large score differential)."""
        prop = Mock()
        prop.id = 1
        prop.team_a_name = "Dominant Team"
        prop.team_b_name = "Struggling Team"
        prop.team_a_score = 45
        prop.team_b_score = 3

        self.mock_game.winner_loser_props = [prop]

        with patch('app.services.game.gradeGameService.db'):
            GradeGameService.auto_grade_props_from_live_data(self.mock_game)

        self.assertEqual(prop.correct_answer, "Dominant Team")


if __name__ == '__main__':
    unittest.main()
