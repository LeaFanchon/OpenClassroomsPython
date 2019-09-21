
# -*-coding:Utf-8 -*

"""This module contains tests for the class Player."""

import unittest
from unittest.mock import MagicMock
from game_logic.player import Player
from sessions.common_session_tools.interactor import DeafInteractor


class TestPlayer(unittest.TestCase):
    """
    TestCase for functions of the 'player' module.
    """

    def setUp(self):
        """
        Before performing the tests on the Player class,
        create a player, a map and a game.
        """

        # Create a mock Map.
        self.game_map = MagicMock()
        self.set_mock_grid_return_value(' ')
        self.game_map.width = 30
        self.game_map.height = 40

        # Create a mock Game object.
        self.game = MagicMock()
        self.game.game_map = self.game_map

        # Create a player that moves East once when asked.
        interactor = DeafInteractor(['E'])
        self.player = Player(interactor)
        self.player.row = 18
        self.player.col = 17
        self.player.identifier = 1
        self.player.game_map = self.game_map
        self.player.game = self.game

    def test_ask_move(self):
        """
        Check that this method correctly detects the fact that
        the player has already played in advance.
        """

        # Simulate the fact the player has already decided in advance.
        self.player.direction = 'E'
        self.player.steps_left = 1

        # Call the method a first time
        self.player.ask_move()

        # Check steps_left has been decremented.
        self.assertEqual(self.player.current_step, 'E')
        self.assertEqual(self.player.steps_left, 0)
        self.assertEqual(self.player.direction, None)

        # Call the method a second time
        self.player.ask_move()

        # Check current_steps is None.
        self.assertEqual(self.player.current_step, None)

    def test_preprocess_move(self):
        """
        Test the following behaviors:
        - If move is just a direction:
                 Store it in current_step
        - If move contains also a number (ex N3):
                 Store the direction in current_step
                 Store the number of steps to take in
                 that direction in steps_left
        - If move is an instruction to create a wall or a door:
                 Store all of it in current_step.
        """

        self.player.current_step = None

        self.player.preprocess_move('E')
        self.assertEqual(self.player.current_step, 'E')

        self.player.preprocess_move('N3')
        self.assertEqual(self.player.current_step, 'N')
        self.assertEqual(self.player.steps_left, 2)

        self.player.preprocess_move('PN')
        self.assertEqual(self.player.current_step, 'PN')

    def test_check_input(self):
        """
        Checks incorrect inputs are detected.
        Valid inputs :
        - A direction, N, E, O or S
        - A request to see the instructions again (I)
        - A request to replace a door with a wall or the opposite.
        """

        self.assertTrue(self.player.check_input('N'))
        self.assertTrue(self.player.check_input('MS'))
        self.assertTrue(self.player.check_input('N5'))

        self.assertFalse(self.player.check_input('NE'))
        self.assertFalse(self.player.check_input('M8'))
        self.assertFalse(self.player.check_input('6'))

    def test_check_move(self):
        """
        Checks if the following behaviors are correctly prevented by the method.
        - The player can't create a door if there is no wall.
        - The player can't create a wall if there is no door.
        - The player can't pass through walls.
        - The player can't pass through other players.
        - The player can't exit the map except through the exit U.
        """

        # The player can't create a door if there is no wall.
        self.player.current_step = 'PS'
        self.set_mock_grid_return_value(' ')
        self.assertFalse(self.player.check_move())

        # The player can't create a wall if there is no door.
        self.player.current_step = 'MS'
        self.assertFalse(self.player.check_move())

        # The player can't pass through walls.
        self.player.current_step = 'S'
        self.set_mock_grid_return_value('O')
        self.assertFalse(self.player.check_move())

        # The player can't exit the map except through the exit U.
        self.set_mock_grid_return_value(' ')
        self.game_map.width = 10
        self.game_map.height = 10
        self.assertFalse(self.player.check_move())
        self.game_map.width = 30
        self.game_map.height = 40

        # Reset player's position and move.
        self.player.row = 18
        self.player.col = 17
        self.player.current_step = 'S'

        # Set the new player's position to make them collide.
        other_player = MagicMock()
        other_player.row = 19
        other_player.col = 17
        self.game.players.values.return_value = [other_player]

        # The player can't pass through other players.
        self.set_mock_grid_return_value(' ')
        self.assertFalse(self.player.check_move())

    def test_perform_move(self):
        """
        Check the method performs the move wanted by the player.
        If the player wanted to create a wall or a door, check if it creates it.
        If the player wanted to move in the labyrinth, check if it moves accordingly.
        """

        # The player is positioned on 18, 17.
        self.player.row = 18
        self.player.col = 17

        # The mock grid will return a wall.
        self.set_mock_grid_return_value('O')

        # Check the command 'PS' opens a door and doesn't make the player move.
        self.player.current_step = 'PS'
        self.player.perform_move()
        self.assertEqual(self.player.row, 18)
        self.assertEqual(self.player.col, 17)

        self.assert_mock_grid_value(19, 17, '.')

        # The mock grid will return an empty space.
        self.set_mock_grid_return_value(' ')

        # Check the command 'N' makes the player move one step north.
        self.player.current_step = 'N'
        self.player.perform_move()
        self.assertEqual(self.player.row, 17)
        self.assertEqual(self.player.col, 17)

    def test_take_one_step(self):
        """
        Check the method takes one step in the given direction.
        """

        # The player is positioned on 18, 17.
        self.player.row = 18
        self.player.col = 17

        row, col = self.player.take_one_step('N')

        self.assertEqual(row, 17)
        self.assertEqual(col, 17)

    def test_has_won(self):
        """
        Check if the function correctly detects the player has won the game.
        """

        # The player has not won.
        self.set_mock_grid_return_value(' ')
        self.assertFalse(self.player.has_won())

        # The player has won.
        self.set_mock_grid_return_value('U')
        self.assertTrue(self.player.has_won())

    def set_mock_grid_return_value(self, value):
        """
        Sets the return value of the mock grid when subscripted twice.
        Ex: sets the value returned by grid[1][2] to the provided parameter.
        """
        self.game_map.grid\
            .__getitem__.return_value\
            .__getitem__.return_value = value

    def assert_mock_grid_value(self, row, col, value):
        """
        Checks that grid[row][col] returns value.
        """
        self.player.game_map.grid\
            .__getitem__.assert_called_with(row)
        self.player.game_map.grid\
            .__getitem__.return_value\
            .__setitem__.assert_called_with(col, value)


if __name__ == '__main__':
    unittest.main()
