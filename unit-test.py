import unittest
import pandas as pd
from prediction_algorithm import app, preprocess_dataframe, calculate_cumulative_points, calculate_cumulative_goals, calculate_form

class DeepFootTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()

    def tearDown(self):
        pass

    def test_home_page(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome to DeepFoot', response.data)


    def test_calculate_cumulative_points(self):
        input_df = pd.DataFrame({
            'homeTeamid': [1, 2, 1],
            'awayTeamid': [2, 1, 2],
            'matchWinner': ['HOME_TEAM', 'DRAW', 'AWAY_TEAM'],
            'matchday': [1, 2, 3]
        })
        expected_output = pd.DataFrame({
            'homeTeamid': [1, 2, 1],
            'awayTeamid': [2, 1, 2],
            'matchWinner': ['HOME_TEAM', 'DRAW', 'AWAY_TEAM'],
            'matchday': [1, 2, 3],
            'homePoints': [0.0, 0.0, 3.0],
            'awayPoints': [0, 0, 0]
        })
        expected_output['awayPoints'] = expected_output['awayPoints'].astype('int32')
        pd.testing.assert_frame_equal(calculate_cumulative_points(input_df), expected_output)

    def test_calculate_cumulative_goals(self):
        input_df = pd.DataFrame({
            'homeTeamid': [1, 2, 1],
            'awayTeamid': [2, 1, 2],
            'homeGoals': [2, 1, 0],
            'awayGoals': [1, 1, 3],
            'matchWinner': ['HOME_TEAM', 'DRAW', 'AWAY_TEAM'],
            'matchday': [1, 2, 3]
        })
        expected_output = pd.DataFrame({
            'homeTeamid': [1, 2, 1],
            'awayTeamid': [2, 1, 2],
            'homeGoals': [2, 1, 0],
            'awayGoals': [1, 1, 3],
            'matchWinner': ['HOME_TEAM', 'DRAW', 'AWAY_TEAM'],
            'matchday': [1, 2, 3],
            'homeTeamHomeGoals': [2.0, 1.0, 2.0],
            'awayTeamAwayGoals': [1.0, 1.0, 4.0]
        })
        pd.testing.assert_frame_equal(calculate_cumulative_goals(input_df), expected_output)

    def test_calculate_form(self):
        input_df = pd.DataFrame({
            'homeTeamid': [1, 2, 1, 2],
            'awayTeamid': [2, 1, 2, 1],
            'matchWinner': ['HOME_TEAM', 'DRAW', 'AWAY_TEAM', 'HOME_TEAM'],
            'matchday': [1, 2, 3, 4]
        })
        expected_output = pd.DataFrame({
            'homeTeamid': [1, 2, 1, 2],
            'awayTeamid': [2, 1, 2, 1],
            'matchWinner': ['HOME_TEAM', 'DRAW', 'AWAY_TEAM', 'HOME_TEAM'],
            'matchday': [1, 2, 3, 4],
            'homeTeamForm': [0, 0, 3, 4],
            'awayTeamForm': [0, 3, 0, 4]
        })
        pd.testing.assert_frame_equal(calculate_form(input_df), expected_output)

if __name__ == '__main__':
    unittest.main()