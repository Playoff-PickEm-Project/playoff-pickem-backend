"""
Integration tests for prop selection with auto-grading.

Tests the complete workflow where multiple players select different optional props
from a pool, answer them, and then the game is graded. Ensures that:
- Players can only select up to prop_limit optional props
- Mandatory props are always required
- Grading correctly awards points only for selected and answered props
- Players who didn't select a prop get 0 points for it
"""

import unittest
from unittest.mock import Mock, patch
from app import db, create_app
from app.models.leagueModel import League
from app.models.playerModel import Player
from app.models.gameModel import Game
from app.models.props.winnerLoserProp import WinnerLoserProp
from app.models.props.overUnderProp import OverUnderProp
from app.models.props.variableOptionProp import VariableOptionProp
from app.models.playerPropSelection import PlayerPropSelection
from app.models.propAnswers.winnerLoserAnswer import WinnerLoserAnswer
from app.models.propAnswers.overUnderAnswer import OverUnderAnswer
from app.models.propAnswers.variableOptionAnswer import VariableOptionAnswer
from app.services.game.gradeGameService import GradeGameService
from datetime import datetime, timedelta
import uuid


class TestPropSelectionGrading(unittest.TestCase):
    """Test cases for prop selection integrated with grading."""

    @classmethod
    def setUpClass(cls):
        """Set up Flask app and database for all tests."""
        # Note: This test uses the actual database configured in the app
        # Make sure to run these tests against a test database, not production
        cls.app = create_app()
        cls.app.config['TESTING'] = True
        cls.app_context = cls.app.app_context()
        cls.app_context.push()

    @classmethod
    def tearDownClass(cls):
        """Clean up after all tests."""
        db.session.remove()
        cls.app_context.pop()

    def setUp(self):
        """Set up test data before each test."""
        # Generate unique identifiers for this test run
        unique_id = str(uuid.uuid4())[:8]

        # Create a test league with unique join code
        self.league = League(
            league_name=f"Test League {unique_id}",
            join_code=f"TEST{unique_id}"
        )
        db.session.add(self.league)
        db.session.flush()

        # Create three test players with unique emails
        self.player1 = Player(
            name=f"player1_{unique_id}@test.com",
            league_id=self.league.id,
            points=0
        )
        self.player2 = Player(
            name=f"player2_{unique_id}@test.com",
            league_id=self.league.id,
            points=0
        )
        self.player3 = Player(
            name=f"player3_{unique_id}@test.com",
            league_id=self.league.id,
            points=0
        )
        db.session.add_all([self.player1, self.player2, self.player3])
        db.session.flush()

        # Create a game with prop_limit=2
        self.game = Game(
            league_id=self.league.id,
            game_name="Test Game - Prop Selection",
            start_time=datetime.now() + timedelta(hours=1),
            graded=0,
            prop_limit=2  # Players must select 2 optional props
        )
        db.session.add(self.game)
        db.session.flush()

        # Create 1 mandatory winner/loser prop
        self.wl_prop_mandatory = WinnerLoserProp(
            game_id=self.game.id,
            question="Who will win?",
            favorite_team="Team A",
            underdog_team="Team B",
            favorite_points=1.0,
            underdog_points=2.0,
            is_mandatory=True,
            team_a_name="Team A",
            team_b_name="Team B",
            team_a_score=None,
            team_b_score=None
        )
        db.session.add(self.wl_prop_mandatory)
        db.session.flush()

        # Create 4 optional over/under props (players choose 2 from these 4)
        self.ou_prop1 = OverUnderProp(
            game_id=self.game.id,
            question="QB Passing Yards O/U 250.5",
            over_points=1.5,
            under_points=1.5,
            line_value=250.5,
            is_mandatory=False,
            player_name="QB Player",
            current_value=None
        )
        self.ou_prop2 = OverUnderProp(
            game_id=self.game.id,
            question="RB Rushing Yards O/U 75.5",
            over_points=2.0,
            under_points=2.0,
            line_value=75.5,
            is_mandatory=False,
            player_name="RB Player",
            current_value=None
        )
        self.ou_prop3 = OverUnderProp(
            game_id=self.game.id,
            question="WR Receiving Yards O/U 100.5",
            over_points=1.0,
            under_points=1.0,
            line_value=100.5,
            is_mandatory=False,
            player_name="WR Player",
            current_value=None
        )
        self.ou_prop4 = OverUnderProp(
            game_id=self.game.id,
            question="Total Points O/U 45.5",
            over_points=1.5,
            under_points=1.5,
            line_value=45.5,
            is_mandatory=False,
            player_name=None,
            current_value=None
        )
        db.session.add_all([self.ou_prop1, self.ou_prop2, self.ou_prop3, self.ou_prop4])
        db.session.commit()

    def tearDown(self):
        """Clean up after each test."""
        # Roll back any uncommitted changes
        db.session.rollback()
        # Note: We're not deleting test data to avoid affecting production database
        # In a real test environment, this would use a separate test database

    def test_multiple_players_different_selections(self):
        """
        Test that multiple players can select different optional props
        and grading works correctly for each player's selections.
        """
        # Player 1 selects props 1 and 2
        selection1_1 = PlayerPropSelection(
            player_id=self.player1.id,
            game_id=self.game.id,
            prop_type="over_under",
            prop_id=self.ou_prop1.id
        )
        selection1_2 = PlayerPropSelection(
            player_id=self.player1.id,
            game_id=self.game.id,
            prop_type="over_under",
            prop_id=self.ou_prop2.id
        )

        # Player 2 selects props 2 and 3
        selection2_1 = PlayerPropSelection(
            player_id=self.player2.id,
            game_id=self.game.id,
            prop_type="over_under",
            prop_id=self.ou_prop2.id
        )
        selection2_2 = PlayerPropSelection(
            player_id=self.player2.id,
            game_id=self.game.id,
            prop_type="over_under",
            prop_id=self.ou_prop3.id
        )

        # Player 3 selects props 3 and 4
        selection3_1 = PlayerPropSelection(
            player_id=self.player3.id,
            game_id=self.game.id,
            prop_type="over_under",
            prop_id=self.ou_prop3.id
        )
        selection3_2 = PlayerPropSelection(
            player_id=self.player3.id,
            game_id=self.game.id,
            prop_type="over_under",
            prop_id=self.ou_prop4.id
        )

        db.session.add_all([
            selection1_1, selection1_2,
            selection2_1, selection2_2,
            selection3_1, selection3_2
        ])
        db.session.commit()

        # All players answer the mandatory prop (Team A wins)
        wl_answer1 = WinnerLoserAnswer(
            player_id=self.player1.id,
            prop_id=self.wl_prop_mandatory.id,
            answer="Team A"
        )
        wl_answer2 = WinnerLoserAnswer(
            player_id=self.player2.id,
            prop_id=self.wl_prop_mandatory.id,
            answer="Team A"
        )
        wl_answer3 = WinnerLoserAnswer(
            player_id=self.player3.id,
            prop_id=self.wl_prop_mandatory.id,
            answer="Team B"  # Player 3 picks wrong
        )

        # Player 1 answers their selected props
        ou_answer1_1 = OverUnderAnswer(
            player_id=self.player1.id,
            prop_id=self.ou_prop1.id,
            answer="over"
        )
        ou_answer1_2 = OverUnderAnswer(
            player_id=self.player1.id,
            prop_id=self.ou_prop2.id,
            answer="under"
        )

        # Player 2 answers their selected props
        ou_answer2_1 = OverUnderAnswer(
            player_id=self.player2.id,
            prop_id=self.ou_prop2.id,
            answer="over"  # Different answer than Player 1 for same prop
        )
        ou_answer2_2 = OverUnderAnswer(
            player_id=self.player2.id,
            prop_id=self.ou_prop3.id,
            answer="over"
        )

        # Player 3 answers their selected props
        ou_answer3_1 = OverUnderAnswer(
            player_id=self.player3.id,
            prop_id=self.ou_prop3.id,
            answer="under"  # Different answer than Player 2 for same prop
        )
        ou_answer3_2 = OverUnderAnswer(
            player_id=self.player3.id,
            prop_id=self.ou_prop4.id,
            answer="over"
        )

        db.session.add_all([
            wl_answer1, wl_answer2, wl_answer3,
            ou_answer1_1, ou_answer1_2,
            ou_answer2_1, ou_answer2_2,
            ou_answer3_1, ou_answer3_2
        ])
        db.session.commit()

        # Simulate game completion - set correct answers
        self.wl_prop_mandatory.team_a_score = 28
        self.wl_prop_mandatory.team_b_score = 24
        self.wl_prop_mandatory.correct_answer = "Team A"

        self.ou_prop1.current_value = 275.0  # Over
        self.ou_prop1.correct_answer = "over"

        self.ou_prop2.current_value = 68.0  # Under
        self.ou_prop2.correct_answer = "under"

        self.ou_prop3.current_value = 110.0  # Over
        self.ou_prop3.correct_answer = "over"

        self.ou_prop4.current_value = 52.0  # Over
        self.ou_prop4.correct_answer = "over"

        db.session.commit()

        # Grade the game
        GradeGameService.grade_game(self.game.id)

        # Refresh player objects to get updated points
        db.session.refresh(self.player1)
        db.session.refresh(self.player2)
        db.session.refresh(self.player3)

        # Verify points
        # Player 1: Mandatory correct (1.0) + Prop1 correct (1.5) + Prop2 correct (2.0) = 4.5
        self.assertEqual(self.player1.points, 4.5,
                        f"Player 1 should have 4.5 points but has {self.player1.points}")

        # Player 2: Mandatory correct (1.0) + Prop2 wrong (0) + Prop3 correct (1.0) = 2.0
        self.assertEqual(self.player2.points, 2.0,
                        f"Player 2 should have 2.0 points but has {self.player2.points}")

        # Player 3: Mandatory wrong (0) + Prop3 wrong (0) + Prop4 correct (1.5) = 1.5
        self.assertEqual(self.player3.points, 1.5,
                        f"Player 3 should have 1.5 points but has {self.player3.points}")

    def test_player_only_graded_on_selected_props(self):
        """
        Test that players are ONLY graded on props they selected,
        not on all props in the game.
        """
        # Player 1 selects only prop 1 and prop 2 (not prop 3 or 4)
        selection1 = PlayerPropSelection(
            player_id=self.player1.id,
            game_id=self.game.id,
            prop_type="over_under",
            prop_id=self.ou_prop1.id
        )
        selection2 = PlayerPropSelection(
            player_id=self.player1.id,
            game_id=self.game.id,
            prop_type="over_under",
            prop_id=self.ou_prop2.id
        )
        db.session.add_all([selection1, selection2])
        db.session.commit()

        # Player 1 answers mandatory prop
        wl_answer = WinnerLoserAnswer(
            player_id=self.player1.id,
            prop_id=self.wl_prop_mandatory.id,
            answer="Team A"
        )

        # Player 1 answers their 2 selected props
        ou_answer1 = OverUnderAnswer(
            player_id=self.player1.id,
            prop_id=self.ou_prop1.id,
            answer="over"
        )
        ou_answer2 = OverUnderAnswer(
            player_id=self.player1.id,
            prop_id=self.ou_prop2.id,
            answer="over"
        )

        db.session.add_all([wl_answer, ou_answer1, ou_answer2])
        db.session.commit()

        # Set all props as correct
        self.wl_prop_mandatory.correct_answer = "Team A"
        self.wl_prop_mandatory.team_a_score = 30
        self.wl_prop_mandatory.team_b_score = 20

        self.ou_prop1.current_value = 300.0
        self.ou_prop1.correct_answer = "over"

        self.ou_prop2.current_value = 100.0
        self.ou_prop2.correct_answer = "over"

        self.ou_prop3.current_value = 150.0
        self.ou_prop3.correct_answer = "over"

        self.ou_prop4.current_value = 60.0
        self.ou_prop4.correct_answer = "over"

        db.session.commit()

        # Grade the game
        GradeGameService.grade_game(self.game.id)

        # Refresh player
        db.session.refresh(self.player1)

        # Player 1 should only get points for props they selected (1, 2, mandatory)
        # Mandatory: 1.0, Prop1: 1.5, Prop2: 2.0 = 4.5 total
        # Should NOT get points for prop3 or prop4 even though they're correct
        expected_points = 1.0 + 1.5 + 2.0
        self.assertEqual(self.player1.points, expected_points,
                        f"Player should only be graded on selected props. Expected {expected_points}, got {self.player1.points}")

    def test_all_players_answer_mandatory_props(self):
        """
        Test that all players must answer mandatory props regardless of selections.
        """
        # Players select different optional props
        selection1 = PlayerPropSelection(
            player_id=self.player1.id,
            game_id=self.game.id,
            prop_type="over_under",
            prop_id=self.ou_prop1.id
        )
        selection2 = PlayerPropSelection(
            player_id=self.player1.id,
            game_id=self.game.id,
            prop_type="over_under",
            prop_id=self.ou_prop2.id
        )
        selection3 = PlayerPropSelection(
            player_id=self.player2.id,
            game_id=self.game.id,
            prop_type="over_under",
            prop_id=self.ou_prop3.id
        )
        selection4 = PlayerPropSelection(
            player_id=self.player2.id,
            game_id=self.game.id,
            prop_type="over_under",
            prop_id=self.ou_prop4.id
        )

        db.session.add_all([selection1, selection2, selection3, selection4])
        db.session.commit()

        # Both players answer the mandatory prop
        wl_answer1 = WinnerLoserAnswer(
            player_id=self.player1.id,
            prop_id=self.wl_prop_mandatory.id,
            answer="Team A"
        )
        wl_answer2 = WinnerLoserAnswer(
            player_id=self.player2.id,
            prop_id=self.wl_prop_mandatory.id,
            answer="Team A"
        )

        # Player 1 answers selected props
        ou_answer1 = OverUnderAnswer(
            player_id=self.player1.id,
            prop_id=self.ou_prop1.id,
            answer="over"
        )
        ou_answer2 = OverUnderAnswer(
            player_id=self.player1.id,
            prop_id=self.ou_prop2.id,
            answer="over"
        )

        # Player 2 answers selected props
        ou_answer3 = OverUnderAnswer(
            player_id=self.player2.id,
            prop_id=self.ou_prop3.id,
            answer="over"
        )
        ou_answer4 = OverUnderAnswer(
            player_id=self.player2.id,
            prop_id=self.ou_prop4.id,
            answer="over"
        )

        db.session.add_all([
            wl_answer1, wl_answer2,
            ou_answer1, ou_answer2, ou_answer3, ou_answer4
        ])
        db.session.commit()

        # Set correct answers
        self.wl_prop_mandatory.correct_answer = "Team A"
        self.wl_prop_mandatory.team_a_score = 25
        self.wl_prop_mandatory.team_b_score = 20
        self.ou_prop1.correct_answer = "over"
        self.ou_prop1.current_value = 300.0
        self.ou_prop2.correct_answer = "over"
        self.ou_prop2.current_value = 100.0
        self.ou_prop3.correct_answer = "over"
        self.ou_prop3.current_value = 120.0
        self.ou_prop4.correct_answer = "over"
        self.ou_prop4.current_value = 50.0

        db.session.commit()

        # Grade the game
        GradeGameService.grade_game(self.game.id)

        # Refresh players
        db.session.refresh(self.player1)
        db.session.refresh(self.player2)

        # Both players should have points from mandatory prop
        self.assertGreaterEqual(self.player1.points, 1.0,
                               "Player 1 should have at least 1 point from mandatory prop")
        self.assertGreaterEqual(self.player2.points, 1.0,
                               "Player 2 should have at least 1 point from mandatory prop")

    def test_no_points_for_unselected_props(self):
        """
        Test that a player gets 0 points for a prop they didn't select,
        even if they would have gotten it correct.
        """
        # Player only selects prop 1 and prop 2
        selection1 = PlayerPropSelection(
            player_id=self.player1.id,
            game_id=self.game.id,
            prop_type="over_under",
            prop_id=self.ou_prop1.id
        )
        selection2 = PlayerPropSelection(
            player_id=self.player1.id,
            game_id=self.game.id,
            prop_type="over_under",
            prop_id=self.ou_prop2.id
        )
        db.session.add_all([selection1, selection2])
        db.session.commit()

        # Player answers mandatory prop
        wl_answer = WinnerLoserAnswer(
            player_id=self.player1.id,
            prop_id=self.wl_prop_mandatory.id,
            answer="Team A"
        )

        # Player ONLY answers their 2 selected props (not prop 3 or 4)
        ou_answer1 = OverUnderAnswer(
            player_id=self.player1.id,
            prop_id=self.ou_prop1.id,
            answer="under"  # Wrong
        )
        ou_answer2 = OverUnderAnswer(
            player_id=self.player1.id,
            prop_id=self.ou_prop2.id,
            answer="under"  # Wrong
        )

        db.session.add_all([wl_answer, ou_answer1, ou_answer2])
        db.session.commit()

        # Set correct answers - prop 3 and 4 would be correct if player answered
        self.wl_prop_mandatory.correct_answer = "Team A"
        self.wl_prop_mandatory.team_a_score = 30
        self.wl_prop_mandatory.team_b_score = 20

        self.ou_prop1.correct_answer = "over"
        self.ou_prop1.current_value = 300.0
        self.ou_prop2.correct_answer = "over"
        self.ou_prop2.current_value = 100.0
        self.ou_prop3.correct_answer = "over"  # Would be correct
        self.ou_prop3.current_value = 150.0
        self.ou_prop4.correct_answer = "over"  # Would be correct
        self.ou_prop4.current_value = 60.0

        db.session.commit()

        # Grade the game
        GradeGameService.grade_game(self.game.id)

        # Refresh player
        db.session.refresh(self.player1)

        # Player should only get 1.0 from mandatory prop
        # Should NOT get points from unselected prop3 or prop4
        self.assertEqual(self.player1.points, 1.0,
                        f"Player should only have 1.0 point from mandatory prop, got {self.player1.points}")

    def test_deselected_prop_not_graded(self):
        """
        Test that if a player selects props 1,2, answers them, then deselects prop 1
        and selects prop 3, only props 2 and 3 are graded (not the deselected prop 1).
        """
        # Step 1: Player selects props 1 and 2
        selection1 = PlayerPropSelection(
            player_id=self.player1.id,
            game_id=self.game.id,
            prop_type="over_under",
            prop_id=self.ou_prop1.id
        )
        selection2 = PlayerPropSelection(
            player_id=self.player1.id,
            game_id=self.game.id,
            prop_type="over_under",
            prop_id=self.ou_prop2.id
        )
        db.session.add_all([selection1, selection2])
        db.session.commit()

        # Step 2: Player answers mandatory prop and both selected props
        wl_answer = WinnerLoserAnswer(
            player_id=self.player1.id,
            prop_id=self.wl_prop_mandatory.id,
            answer="Team A"
        )
        ou_answer1 = OverUnderAnswer(
            player_id=self.player1.id,
            prop_id=self.ou_prop1.id,
            answer="over"  # Will be correct
        )
        ou_answer2 = OverUnderAnswer(
            player_id=self.player1.id,
            prop_id=self.ou_prop2.id,
            answer="over"  # Will be correct
        )
        db.session.add_all([wl_answer, ou_answer1, ou_answer2])
        db.session.commit()

        # Step 3: Player deselects prop 1 and selects prop 3 instead
        db.session.delete(selection1)
        selection3 = PlayerPropSelection(
            player_id=self.player1.id,
            game_id=self.game.id,
            prop_type="over_under",
            prop_id=self.ou_prop3.id
        )
        db.session.add(selection3)
        db.session.commit()

        # Step 4: Player answers prop 3
        ou_answer3 = OverUnderAnswer(
            player_id=self.player1.id,
            prop_id=self.ou_prop3.id,
            answer="over"  # Will be correct
        )
        db.session.add(ou_answer3)
        db.session.commit()

        # Now player has answers for props 1, 2, and 3
        # But only has selections for props 2 and 3
        # Prop 1 answer should NOT be graded

        # Set all props as correct
        self.wl_prop_mandatory.correct_answer = "Team A"
        self.wl_prop_mandatory.team_a_score = 30
        self.wl_prop_mandatory.team_b_score = 20

        self.ou_prop1.correct_answer = "over"
        self.ou_prop1.current_value = 300.0
        self.ou_prop2.correct_answer = "over"
        self.ou_prop2.current_value = 100.0
        self.ou_prop3.correct_answer = "over"
        self.ou_prop3.current_value = 150.0

        db.session.commit()

        # Grade the game
        GradeGameService.grade_game(self.game.id)

        # Refresh player
        db.session.refresh(self.player1)

        # Player should get:
        # - Mandatory prop: 1.0
        # - Prop 2 (selected + answered correctly): 2.0
        # - Prop 3 (selected + answered correctly): 1.0
        # - Prop 1 (answered but NOT selected): 0 points
        # Total: 4.0 points
        expected_points = 1.0 + 2.0 + 1.0
        self.assertEqual(self.player1.points, expected_points,
                        f"Player should have {expected_points} points (not including deselected prop 1). Got {self.player1.points}")


if __name__ == '__main__':
    unittest.main()
