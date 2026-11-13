import unittest

import numpy as np

from possession_features import alignment_evidence, central_velocity, safe_cosine


class GeometryTests(unittest.TestCase):
    def test_central_velocity_edges_are_nan(self):
        x = np.array([[0.0], [1.0], [2.0], [3.0]])
        v = central_velocity(x, fps=25)
        self.assertTrue(np.isnan(v[0, 0]))
        self.assertTrue(np.isnan(v[-1, 0]))
        self.assertAlmostEqual(v[1, 0], 25.0)
        self.assertAlmostEqual(v[2, 0], 25.0)

    def test_safe_cosine_parallel_orthogonal_and_zero(self):
        self.assertAlmostEqual(safe_cosine([1], [0], [2], [0])[0], 1.0)
        self.assertAlmostEqual(safe_cosine([1], [0], [0], [2])[0], 0.0)
        self.assertEqual(safe_cosine([0], [0], [1], [0])[0], 0.0)
        self.assertEqual(safe_cosine([np.nan], [0], [1], [0])[0], 0.0)

    def test_alignment_prefers_player_running_with_ball(self):
        n = 5
        # Two anonymous slots per team.  Home moves +x with the ball; away
        # moves -x.  The nearest-player velocities should carry opposite signs.
        px = np.zeros((n, 4))
        py = np.zeros((n, 4))
        px[:, 0] = np.arange(n) * 0.1
        px[:, 1] = np.arange(n) * 0.1
        px[:, 2] = 10.0 - np.arange(n) * 0.1
        px[:, 3] = 10.0 - np.arange(n) * 0.1
        bx = 1.0 + np.arange(n) * 0.1
        by = np.full(n, 1.0)
        out = alignment_evidence(px, py, bx, by, np.array([0, 0, 1, 1]), fps=25)
        self.assertGreater(out["diff"][2], 0.5)
        self.assertAlmostEqual(out["cos_home"][2], 1.0, places=3)
        self.assertAlmostEqual(out["cos_away"][2], -1.0, places=3)

    def test_alignment_reverses_for_interception_direction(self):
        n = 5
        px = np.zeros((n, 4))
        py = np.zeros((n, 4))
        px[:, 0] = np.arange(n) * 0.1
        px[:, 1] = np.arange(n) * 0.1
        px[:, 2] = 10.0 - np.arange(n) * 0.1
        px[:, 3] = 10.0 - np.arange(n) * 0.1
        bx = 2.0 - np.arange(n) * 0.1
        by = np.full(n, 1.0)
        out = alignment_evidence(px, py, bx, by, np.array([0, 0, 1, 1]), fps=25)
        self.assertLess(out["diff"][2], -0.5)

    def test_missing_ball_is_neutral(self):
        n = 4
        px = np.zeros((n, 2))
        py = np.zeros((n, 2))
        bx = np.full(n, np.nan)
        by = np.full(n, np.nan)
        out = alignment_evidence(px, py, bx, by, np.array([0, 1]), fps=25)
        np.testing.assert_array_equal(out["diff"], np.zeros(n))

    def test_stationary_ball_is_neutral(self):
        n = 4
        px = np.zeros((n, 2))
        py = np.zeros((n, 2))
        bx = np.ones(n)
        by = np.ones(n)
        out = alignment_evidence(px, py, bx, by, np.array([0, 1]), fps=25)
        np.testing.assert_array_equal(out["diff"], np.zeros(n))

    def test_no_visible_players_is_neutral(self):
        n = 3
        px = np.full((n, 2), np.nan)
        py = np.full((n, 2), np.nan)
        bx = np.arange(n, dtype=float)
        by = np.zeros(n)
        out = alignment_evidence(px, py, bx, by, np.array([0, 1]), fps=25)
        np.testing.assert_array_equal(out["diff"], np.zeros(n))


if __name__ == "__main__":
    unittest.main()
