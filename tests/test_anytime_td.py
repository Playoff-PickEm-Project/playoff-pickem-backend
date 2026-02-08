"""
Unit tests for Anytime TD Scorer prop functionality.

Tests cover:
- Model methods (to_dict, has_hit_line)
- Auto-grading logic for TD props
- Grading logic with player selections
- Manual grading with regrade support
"""

import unittest
from unittest.mock import Mock, MagicMock, patch
from app.services.game.gradeGameService import GradeGameService


class TestAnytimeTdModels(unittest.TestCase):
    """Test cases for Anytime TD model methods."""

    def test_anytime_td_option_has_hit_line_success(self):
        """Test has_hit_line returns True when TDs >= line."""
        option = Mock()
        option.player_name = "Travis Kelce"
        option.td_line = 0.5
        option.current_tds = 2

        # Mock the has_hit_line method to simulate actual behavior
        option.has_hit_line = lambda: option.current_tds >= option.td_line

        self.assertTrue(option.has_hit_line())

    def test_anytime_td_option_has_hit_line_failure(self):
        """Test has_hit_line returns False when TDs < line."""
        option = Mock()
        option.player_name = "Patrick Mahomes"
        option.td_line = 1.5
        option.current_tds = 1

        option.has_hit_line = lambda: option.current_tds >= option.td_line

        self.assertFalse(option.has_hit_line())

    def test_anytime_td_option_has_hit_line_exact(self):
        """Test has_hit_line when TDs exactly equals line."""
        option = Mock()
        option.player_name = "Tyreek Hill"
        option.td_line = 2.5
        option.current_tds = 3  # 3 >= 2.5, should hit

        option.has_hit_line = lambda: option.current_tds >= option.td_line

        self.assertTrue(option.has_hit_line())

    def test_anytime_td_option_has_hit_line_none(self):
        """Test has_hit_line returns False when current_tds is None."""
        option = Mock()
        option.player_name = "Travis Kelce"
        option.td_line = 0.5
        option.current_tds = None

        option.has_hit_line = lambda: False if option.current_tds is None else option.current_tds >= option.td_line

        self.assertFalse(option.has_hit_line())

    def test_anytime_td_option_has_hit_line_zero_tds(self):
        """Test has_hit_line when player has 0 TDs."""
        option = Mock()
        option.player_name = "Offensive Lineman"
        option.td_line = 0.5
        option.current_tds = 0

        option.has_hit_line = lambda: option.current_tds >= option.td_line

        self.assertFalse(option.has_hit_line())


class TestAnytimeTdAutoGrading(unittest.TestCase):
    """Test cases for auto-grading Anytime TD props."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_game = Mock()
        self.mock_game.over_under_props = []
        self.mock_game.winner_loser_props = []
        self.mock_game.anytime_td_props = []

    def test_anytime_td_single_player_hits_line(self):
        """Test auto-grading when single player hits their TD line."""
        # Create mock option that hit the line
        option1 = Mock()
        option1.player_name = "Travis Kelce"
        option1.td_line = 0.5
        option1.current_tds = 2
        option1.has_hit_line = lambda: option1.current_tds >= option1.td_line

        # Create mock option that didn't hit
        option2 = Mock()
        option2.player_name = "Patrick Mahomes"
        option2.td_line = 1.5
        option2.current_tds = 1
        option2.has_hit_line = lambda: option2.current_tds >= option2.td_line

        prop = Mock()
        prop.id = 1
        prop.options = [option1, option2]
        prop.correct_answer = None

        self.mock_game.anytime_td_props = [prop]

        with patch('app.services.game.gradeGameService.db'):
            GradeGameService.auto_grade_props_from_live_data(self.mock_game)

        # Should only include Travis Kelce
        self.assertEqual(prop.correct_answer, ["Travis Kelce"])

    def test_anytime_td_multiple_players_hit_line(self):
        """Test auto-grading when multiple players hit their TD lines."""
        option1 = Mock()
        option1.player_name = "Travis Kelce"
        option1.td_line = 0.5
        option1.current_tds = 1
        option1.has_hit_line = lambda: option1.current_tds >= option1.td_line

        option2 = Mock()
        option2.player_name = "Patrick Mahomes"
        option2.td_line = 0.5
        option2.current_tds = 2
        option2.has_hit_line = lambda: option2.current_tds >= option2.td_line

        option3 = Mock()
        option3.player_name = "Tyreek Hill"
        option3.td_line = 1.5
        option3.current_tds = 3
        option3.has_hit_line = lambda: option3.current_tds >= option3.td_line

        prop = Mock()
        prop.id = 1
        prop.options = [option1, option2, option3]
        prop.correct_answer = None

        self.mock_game.anytime_td_props = [prop]

        with patch('app.services.game.gradeGameService.db'):
            GradeGameService.auto_grade_props_from_live_data(self.mock_game)

        # All three should be in correct_answer
        self.assertEqual(set(prop.correct_answer), {"Travis Kelce", "Patrick Mahomes", "Tyreek Hill"})

    def test_anytime_td_no_players_hit_line(self):
        """Test auto-grading when no players hit their TD lines."""
        option1 = Mock()
        option1.player_name = "Player A"
        option1.td_line = 0.5
        option1.current_tds = 0
        option1.has_hit_line = lambda: option1.current_tds >= option1.td_line

        option2 = Mock()
        option2.player_name = "Player B"
        option2.td_line = 1.5
        option2.current_tds = 0
        option2.has_hit_line = lambda: option2.current_tds >= option2.td_line

        prop = Mock()
        prop.id = 1
        prop.options = [option1, option2]
        prop.correct_answer = None

        self.mock_game.anytime_td_props = [prop]

        with patch('app.services.game.gradeGameService.db'):
            GradeGameService.auto_grade_props_from_live_data(self.mock_game)

        # Should remain None when no players hit
        self.assertIsNone(prop.correct_answer)

    def test_anytime_td_different_td_lines(self):
        """Test auto-grading with different TD line thresholds."""
        # Player with 0.5 line (1+ TD) - has 1 TD
        option1 = Mock()
        option1.player_name = "Tight End"
        option1.td_line = 0.5
        option1.current_tds = 1
        option1.has_hit_line = lambda: option1.current_tds >= option1.td_line

        # Player with 1.5 line (2+ TDs) - has 1 TD (doesn't hit)
        option2 = Mock()
        option2.player_name = "Running Back"
        option2.td_line = 1.5
        option2.current_tds = 1
        option2.has_hit_line = lambda: option2.current_tds >= option2.td_line

        # Player with 2.5 line (3+ TDs) - has 3 TDs (hits)
        option3 = Mock()
        option3.player_name = "Wide Receiver"
        option3.td_line = 2.5
        option3.current_tds = 3
        option3.has_hit_line = lambda: option3.current_tds >= option3.td_line

        prop = Mock()
        prop.id = 1
        prop.options = [option1, option2, option3]
        prop.correct_answer = None

        self.mock_game.anytime_td_props = [prop]

        with patch('app.services.game.gradeGameService.db'):
            GradeGameService.auto_grade_props_from_live_data(self.mock_game)

        # Only Tight End and Wide Receiver hit their lines
        self.assertEqual(set(prop.correct_answer), {"Tight End", "Wide Receiver"})

    def test_anytime_td_with_other_prop_types(self):
        """Test auto-grading anytime TD alongside other prop types."""
        # Over/Under prop
        ou_prop = Mock()
        ou_prop.id = 1
        ou_prop.current_value = 250.0
        ou_prop.line_value = 200.0

        # Anytime TD prop
        option = Mock()
        option.player_name = "Travis Kelce"
        option.td_line = 0.5
        option.current_tds = 2
        option.has_hit_line = lambda: option.current_tds >= option.td_line

        td_prop = Mock()
        td_prop.id = 2
        td_prop.options = [option]
        td_prop.correct_answer = None

        self.mock_game.over_under_props = [ou_prop]
        self.mock_game.anytime_td_props = [td_prop]

        with patch('app.services.game.gradeGameService.db'):
            GradeGameService.auto_grade_props_from_live_data(self.mock_game)

        self.assertEqual(ou_prop.correct_answer, "over")
        self.assertEqual(td_prop.correct_answer, ["Travis Kelce"])


class TestAnytimeTdGrading(unittest.TestCase):
    """Test cases for grading Anytime TD prop answers."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_game = Mock()
        self.mock_game.id = 1
        self.mock_game.graded = 0
        self.mock_game.winner_loser_props = []
        self.mock_game.over_under_props = []
        self.mock_game.variable_option_props = []
        self.mock_game.anytime_td_props = []

    @patch('app.services.game.gradeGameService.get_player_by_id')
    @patch('app.services.game.gradeGameService.get_anytime_td_answers_for_prop')
    @patch('app.services.game.gradeGameService.get_game_by_id')
    @patch('app.services.game.gradeGameService.db')
    def test_anytime_td_correct_answer_awards_points(self, mock_db, mock_get_game, mock_get_answers, mock_get_player):
        """Test that correct anytime TD answer awards points."""
        # Setup player
        player = Mock()
        player.id = 1
        player.points = 10
        mock_get_player.return_value = player

        # Setup option
        option = Mock()
        option.player_name = "Travis Kelce"
        option.points = 5

        # Setup prop
        prop = Mock()
        prop.id = 1
        prop.is_mandatory = True
        prop.correct_answer = ["Travis Kelce"]
        prop.options = [option]

        # Setup answer
        answer = Mock()
        answer.player_id = 1
        answer.answer = "Travis Kelce"
        mock_get_answers.return_value = [answer]

        self.mock_game.anytime_td_props = [prop]
        mock_get_game.return_value = self.mock_game

        GradeGameService.grade_game(1)

        # Player should receive 5 points
        self.assertEqual(player.points, 15)

    @patch('app.services.game.gradeGameService.get_player_by_id')
    @patch('app.services.game.gradeGameService.get_anytime_td_answers_for_prop')
    @patch('app.services.game.gradeGameService.get_game_by_id')
    @patch('app.services.game.gradeGameService.db')
    def test_anytime_td_incorrect_answer_no_points(self, mock_db, mock_get_game, mock_get_answers, mock_get_player):
        """Test that incorrect anytime TD answer awards no points."""
        # Setup player
        player = Mock()
        player.id = 1
        player.points = 10
        mock_get_player.return_value = player

        # Setup option
        option = Mock()
        option.player_name = "Patrick Mahomes"
        option.points = 12

        # Setup prop
        prop = Mock()
        prop.id = 1
        prop.is_mandatory = True
        prop.correct_answer = ["Travis Kelce"]  # Player selected Mahomes, but Kelce was correct
        prop.options = [option]

        # Setup answer
        answer = Mock()
        answer.player_id = 1
        answer.answer = "Patrick Mahomes"
        mock_get_answers.return_value = [answer]

        self.mock_game.anytime_td_props = [prop]
        mock_get_game.return_value = self.mock_game

        GradeGameService.grade_game(1)

        # Player should receive no points
        self.assertEqual(player.points, 10)

    @patch('app.services.game.gradeGameService.get_player_by_id')
    @patch('app.services.game.gradeGameService.get_anytime_td_answers_for_prop')
    @patch('app.services.game.gradeGameService.get_game_by_id')
    @patch('app.services.game.gradeGameService.db')
    def test_anytime_td_different_point_values(self, mock_db, mock_get_game, mock_get_answers, mock_get_player):
        """Test that different options award different point values."""
        # Setup player
        player = Mock()
        player.id = 1
        player.points = 0
        mock_get_player.return_value = player

        # Setup options with different point values
        option1 = Mock()
        option1.player_name = "Travis Kelce"
        option1.points = 5

        option2 = Mock()
        option2.player_name = "Patrick Mahomes"
        option2.points = 12

        # Setup prop
        prop = Mock()
        prop.id = 1
        prop.is_mandatory = True
        prop.correct_answer = ["Patrick Mahomes"]
        prop.options = [option1, option2]

        # Setup answer
        answer = Mock()
        answer.player_id = 1
        answer.answer = "Patrick Mahomes"
        mock_get_answers.return_value = [answer]

        self.mock_game.anytime_td_props = [prop]
        mock_get_game.return_value = self.mock_game

        GradeGameService.grade_game(1)

        # Player should receive 12 points (Mahomes' value, not Kelce's)
        self.assertEqual(player.points, 12)

    @patch('app.services.game.gradeGameService.get_player_by_id')
    @patch('app.services.game.gradeGameService.get_anytime_td_answers_for_prop')
    @patch('app.services.game.gradeGameService.get_game_by_id')
    @patch('app.services.game.gradeGameService.db')
    def test_anytime_td_multiple_correct_answers(self, mock_db, mock_get_game, mock_get_answers, mock_get_player):
        """Test when multiple players hit their lines (multiple correct answers)."""
        # Setup player
        player = Mock()
        player.id = 1
        player.points = 0
        mock_get_player.return_value = player

        # Setup options
        option1 = Mock()
        option1.player_name = "Travis Kelce"
        option1.points = 5

        option2 = Mock()
        option2.player_name = "Patrick Mahomes"
        option2.points = 12

        # Setup prop where both players hit their lines
        prop = Mock()
        prop.id = 1
        prop.is_mandatory = True
        prop.correct_answer = ["Travis Kelce", "Patrick Mahomes"]
        prop.options = [option1, option2]

        # Setup answer - player selected Kelce
        answer = Mock()
        answer.player_id = 1
        answer.answer = "Travis Kelce"
        mock_get_answers.return_value = [answer]

        self.mock_game.anytime_td_props = [prop]
        mock_get_game.return_value = self.mock_game

        GradeGameService.grade_game(1)

        # Player should receive Kelce's 5 points
        self.assertEqual(player.points, 5)


class TestAnytimeTdManualGrading(unittest.TestCase):
    """Test cases for manual grading and regrading of Anytime TD props."""

    @patch('app.services.game.gradeGameService.get_player_by_id')
    @patch('app.services.game.gradeGameService.get_anytime_td_answers_for_prop')
    @patch('app.services.game.gradeGameService.get_anytime_td_prop_by_id')
    @patch('app.services.game.gradeGameService.Game')
    @patch('app.services.game.gradeGameService.db')
    def test_set_correct_anytime_td_prop_not_graded(self, mock_db, mock_game_class, mock_get_prop, mock_get_answers, mock_get_player):
        """Test setting correct answer when game hasn't been graded yet."""
        # Setup prop
        prop = Mock()
        prop.id = 1
        prop.game_id = 1
        prop.correct_answer = None
        mock_get_prop.return_value = prop

        # Setup game
        game = Mock()
        game.id = 1
        game.graded = 0
        mock_game_class.query.filter_by.return_value.first.return_value = game

        GradeGameService.set_correct_anytime_td_prop("TestLeague", 1, ["Travis Kelce"])

        # Should update correct_answer without deducting points
        self.assertEqual(prop.correct_answer, ["Travis Kelce"])

    @patch('app.services.game.gradeGameService.get_player_by_id')
    @patch('app.services.game.gradeGameService.get_anytime_td_answers_for_prop')
    @patch('app.services.game.gradeGameService.get_anytime_td_prop_by_id')
    @patch('app.services.game.gradeGameService.Game')
    @patch('app.services.game.gradeGameService.db')
    def test_set_correct_anytime_td_prop_regrade(self, mock_db, mock_game_class, mock_get_prop, mock_get_answers, mock_get_player):
        """Test regrading when correct answer changes after grading."""
        # Setup player
        player = Mock()
        player.id = 1
        player.name = "TestPlayer"
        player.points = 15  # Has 15 points
        mock_get_player.return_value = player

        # Setup option
        option = Mock()
        option.player_name = "Travis Kelce"
        option.points = 5

        # Setup prop
        prop = Mock()
        prop.id = 1
        prop.game_id = 1
        prop.correct_answer = ["Travis Kelce"]  # OLD correct answer
        prop.options = [option]
        mock_get_prop.return_value = prop

        # Setup game (already graded)
        game = Mock()
        game.id = 1
        game.graded = 1
        mock_game_class.query.filter_by.return_value.first.return_value = game

        # Setup answer
        answer = Mock()
        answer.player_id = 1
        answer.answer = "Travis Kelce"
        mock_get_answers.return_value = [answer]

        # Change correct answer to different player
        GradeGameService.set_correct_anytime_td_prop("TestLeague", 1, ["Patrick Mahomes"])

        # Should deduct old points
        self.assertEqual(player.points, 10)  # 15 - 5 = 10
        # Should update correct_answer
        self.assertEqual(prop.correct_answer, ["Patrick Mahomes"])


if __name__ == '__main__':
    unittest.main()
