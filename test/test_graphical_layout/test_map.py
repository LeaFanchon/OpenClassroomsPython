# -*-coding:Utf-8 -*

"""This module contains tests for the class Map."""
import unittest
import os
import parameters.parameters as parameters
import test.parameters_for_testing as test_parameters
from graphical_layout.map import Map


class TestMap(unittest.TestCase):
    """TestCase for functions of the 'map' module."""

    def setUp(self):
        """Loads the test maps"""

        # Load Test Maps present in dir_test_maps
        self.test_maps = {}

        location = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        dir_maps = os.path.join(location, parameters.dir_test_maps)

        for name_file in os.listdir(dir_maps):

            if name_file.endswith(".txt"):
                map_path = os.path.join(dir_maps, name_file)
                map_name = name_file[:-4].lower()

                with open(map_path, "r") as map_file:
                    self.test_maps[map_name] = map_file.read()

    def test_is_valid(self):
        """Tests if the method is_valid from the function Map correctly identifies invalid maps."""

        for test_map in self.test_maps:

            is_valid, message = Map.is_valid(self.test_maps[test_map].upper())

            if test_map == "correct_map":
                self.assertTrue(is_valid)

            elif test_map == "invalid_character_map":
                self.assertFalse(is_valid)
                self.assertEqual(message, Map.INVALID_CHARS_ERROR)

            elif test_map in ["no_u_map", "several_u_map"]:
                self.assertFalse(is_valid)
                self.assertEqual(message, Map.U_COUNT_ERROR)

            elif test_map == "non_rectangular_map":
                self.assertFalse(is_valid)
                self.assertEqual(message, Map.NON_RECTANGULAR_ERROR)

            elif test_map == "too_small_map":
                self.assertFalse(is_valid)
                self.assertEqual(message, Map.TOO_SMALL_ERROR)

            elif test_map == "too_large_map":
                self.assertFalse(is_valid)
                self.assertEqual(message, Map.TOO_LARGE_ERROR)

    def test_constructor(self):
        """Tests the constructor of the class Map"""

        expected_grid = [list(r) for r in test_parameters.correct_grid]
        map_name = "correct_map"
        my_map = Map(map_name, self.test_maps[map_name])
        self.assertEqual(my_map.name, map_name)
        self.assertEqual(my_map.height, 20)
        self.assertEqual(my_map.width, 20)
        self.assertEqual(my_map.grid, expected_grid)


if __name__ == '__main__':
    unittest.main()
