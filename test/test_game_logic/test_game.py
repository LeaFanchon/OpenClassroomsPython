# -*-coding:Utf-8 -*

"""This module contains tests for the class Game."""
import unittest
from unittest.mock import MagicMock

import test.parameters_for_testing as parameters
from game_logic.game import Game
from sessions.common_session_tools.interactor import DeafInteractor


class TestGame(unittest.TestCase):
    """
    TestCase for functions of the 'game' module.
    We call the two methods called from outside the class:
    - play
    - add_player
    This ensures entire coverage of the Game methods.
    """

    def setUp(self):
        """
        Before performing the tests on the Game class:
         - create a player, a map and a game.
        """

        # Create a mock Map.
        self.game_map = MagicMock()
        self.game_map.grid = [list(row) for row in parameters.test_grid]
        self.game_map.width = 8
        self.game_map.height = 3

        # Create a Game object with:
        # - The mock map created above
        # - A server user that anwers '1' once, then ''.
        self.game = Game(self.game_map, DeafInteractor(['1']))

    def test_available_positions(self):
        """
        Check that the game has correctly found 6 available positions
        in the test_grid.
        """
        # The method has already been called in the constructor of Game.
        # There is no need to call it again.
        self.assertEqual(len(self.game.available_positions), 6)

    def test_add_player(self):
        """
        Test if the method add_player from the Game class:
         - Adds a player to the game
         - Chooses an available position for this player.
        """

        # Add a mock player to the game.
        player = MagicMock()
        self.game.add_player(player)

        # Check the number of players of the game has been incremented
        self.assertEqual(self.game.player_number, 1)

        # Check that the number of available positions has been decremented.
        self.assertEqual(len(self.game.available_positions), 5)

        # Check that the mock player's parameters have been correctly updated.
        self.assertTrue(player.game is self.game)
        self.assertTrue(player.game_map is self.game_map)

    def test_play(self):
        """
        Tests one run of the game with two players.
        """

        # Add two mock players to the game.
        # Both of them only play 'E' all the time.

        # The game should be won by the first player.
        # For each mock player:
        #   - The two first calls of has_won return False.
        #   - The third call returns True.

        for i in range(0, 2):
            player = MagicMock()
            player.recv.return_value = 'E'
            player.has_left = False

            # has_won returns twice False, and True the third time.
            player.has_won.side_effect = [False, False, True]
            player.check_input.return_value = True
            self.game.add_player(player)

        # The game should thus be won by the first player on the 5th round:
        # Round 1: player1.has_won = False
        # Round 2: player2.has_won = False
        # Round 3: player1.has_won = False
        # Round 4: player2.has_won = False
        # Round 5: player1.has_won = True => wins game

        # We play the game.
        self.game.play()

        # We check that the game is over.
        self.assertTrue(self.game.finished)

        # We check that player one has won the game.
        self.assertEqual(self.game.winner, self.game.players[0])

        # We check there were 5 rounds in the game
        self.assertEqual(self.game.how_many_rounds, 5)


if __name__ == '__main__':
    unittest.main()
