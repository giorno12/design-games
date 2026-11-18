import math
import unittest

from design_math import (
    damping,
    drop_probability,
    effective_hp,
    expected_dps,
    pity_distribution,
    time_to_kill,
)


class DesignMathTests(unittest.TestCase):
    def test_expected_dps(self):
        result = expected_dps(100, 0.5, accuracy=0.8, crit_chance=0.25, crit_multiplier=2)
        self.assertEqual(result["expected_damage_on_hit"], 125)
        self.assertEqual(result["expected_damage_per_attack"], 100)
        self.assertEqual(result["expected_dps"], 200)

    def test_effective_hp(self):
        result = effective_hp(1000, armor=100, armor_k=100)
        self.assertEqual(result["damage_multiplier"], 0.5)
        self.assertEqual(result["effective_hp"], 2000)

    def test_time_to_kill(self):
        self.assertEqual(time_to_kill(1000, 200)["time_to_kill_seconds"], 5)

    def test_drop_probability(self):
        result = drop_probability(0.5, 3, confidence=0.95)
        self.assertEqual(result["at_least_once_probability"], 0.875)
        self.assertEqual(result["expected_attempts"], 2)
        self.assertEqual(result["attempts_for_confidence"], 5)
        self.assertIsNone(drop_probability(0, 3)["expected_attempts"])

    def test_pity_distribution(self):
        result = pity_distribution(0.1, hard_pity=5, soft_start=3, soft_step=0.2)
        self.assertEqual(result["probabilities_by_pull"], [0.1, 0.1, 0.30000000000000004, 0.5, 1.0])
        self.assertTrue(math.isclose(sum(result["success_mass_by_pull"]), 1.0))
        self.assertEqual(result["p99_pulls"], 5)
        self.assertGreater(result["expected_pulls"], 0)

    def test_damping_is_frame_rate_independent(self):
        one_step = damping(0.1, 0.1)["retention"]
        two_steps = damping(0.1, 0.05)["retention"] ** 2
        self.assertTrue(math.isclose(one_step, two_steps))
        self.assertEqual(one_step, 0.5)

    def test_invalid_inputs(self):
        with self.assertRaises(ValueError):
            expected_dps(100, 0)
        with self.assertRaises(ValueError):
            drop_probability(1.1, 2)
        with self.assertRaises(ValueError):
            pity_distribution(0.1, 5, 6, 0.2)


if __name__ == "__main__":
    unittest.main()
