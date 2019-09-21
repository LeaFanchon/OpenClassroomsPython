# -*-coding:Utf-8 -*

"""This module contains tests for the class MainSession."""
import unittest
from unittest.mock import MagicMock
from sessions.server_session.server_session import MainSession
from sessions.common_session_tools.interactor import DeafInteractor, DeafInteractorFactory
import test.parameters_for_testing as parameters


class TestMainSession(unittest.TestCase):
    """
    TestCase for the class MainSession.
    Tests the methods called from outside the session:
     - load_maps
     - launch.
    This ensures entire coverage of the MainSession methods.
    """

    def setUp(self):
        """
        Code to execute before performing the tests.
        Create a session with:
          - A mock server interactor.
            Contains all the inputs to come from the server
          - Three mock player interactors.
            Contain all the inputs to come from the players
        """

        # The server will input '1' twice, and '0' to exit the session.
        # When asked which labyrinth to use,
        # the server will answer twice the first labyrinth.
        server_interactor = DeafInteractor(['1', '1', '0'])

        # Two games will be played during the test of the session.

        # For each game:
        # - All three players will only play East 3 times.
        # - The first player will also launch the game with the C command

        # At the end of the first game:
        # - All the players send 'O' to continue playing.

        # At the end of the second game:
        # - All the players send 'N' to stop playing.

        moves = ['E'] * 3
        start = ['C']
        go_on = ['O']
        stop = ['N']

        first_player = start + moves + go_on + start + moves + stop
        second_player = moves + go_on + moves + stop
        third_player = moves + go_on + moves + stop

        players_moves = [first_player, second_player, third_player]
        factory = DeafInteractorFactory(players_moves)

        self.session = MainSession(server_interactor, factory)

    def test_load_maps(self):
        """
        Tests the method load_maps actually loads some maps in the session.
        """
        self.session.load_maps()
        self.assertTrue(len(self.session.maps) > 0)

    def test_launch(self):
        """
        Tests a full session with three players playing two games.
        We use the easy_to_win map from the parameters_for_testing module.
        """

        # Make sure there are no maps loaded in the session.
        self.session.maps = []

        # Create a mock map with the easy_to_win grid.
        # This grid makes it certain that one player
        # will win in less than 3 East steps.
        game_map = MagicMock()
        game_map.grid = [list(row) for row in parameters.easy_to_win]
        game_map.width = 20
        game_map.height = 6
        game_map.max_players = 3

        self.session.maps.append(game_map)
        self.session.launch()

        # Check all players have been disconnected.
        self.assertEqual(len(self.session.connected_players), 0)

        # Check two games have been played.
        self.assertEqual(self.session.games_played, 2)

        # Check that both games involved 3 players.
        for i in range(0, 2):
            self.assertEqual(self.session.players_number[i], 3)

        # Check the session is over.
        self.assertFalse(self.session.play)


if __name__ == '__main__':
    unittest.main()
