import unittest

from art_budget import lod_chain, texture_memory


class ArtBudgetTests(unittest.TestCase):
    def test_single_texture_level(self):
        result = texture_memory(2, 2, bits_per_pixel=8, mip_levels=1)
        self.assertEqual(result["total_bytes"], 4)
        self.assertEqual(result["bytes_by_level"], [4])

    def test_full_mip_chain(self):
        result = texture_memory(4, 4, bits_per_pixel=8)
        self.assertEqual(result["bytes_by_level"], [16, 4, 1])
        self.assertEqual(result["total_bytes"], 21)

    def test_layers(self):
        result = texture_memory(2, 2, bits_per_pixel=8, mip_levels=1, layers=6)
        self.assertEqual(result["total_bytes"], 24)

    def test_lod_chain(self):
        result = lod_chain(10000, [1, 0.5, 0.25])
        self.assertEqual(result["triangles_by_lod"], [10000, 5000, 2500])

    def test_invalid_input(self):
        with self.assertRaises(ValueError):
            texture_memory(0, 4, 8)
        with self.assertRaises(ValueError):
            lod_chain(100, [0])


if __name__ == "__main__":
    unittest.main()
