# -*-coding:Utf-8 -*

"""
This module contains the class MainSession.
MainSession is the class used to implement the server in the roboc game.
"""
import os

import parameters.parameters as parameters
from graphical_layout.map import Map
from game_logic.game import Game
from game_logic.player import Player
from sessions.common_session_tools.session import Session
from sessions.common_session_tools.singleton import decorator_singleton


@decorator_singleton
class MainSession(Session):
    """
    Class MainSession.
    A MainSession is a Singleton object.
    It manages everything:
        - From the moment the file server.py is launched
        - Up until the moment no more clients want to continue playing.
    """

    def __init__(self, interactor, player_interactor_factory):
        """
        Generates a server session.

        - interactor is used to interact with the server
          Example:
            When playing: ShellInteractor
                          Print to the shell and get inputs from the shell
            When testing: DeafInteractor
                          Create a mock server with simulated inputs

        - player_interactor_class is the type of interactor
          that will be used to communicate with the players.
          Example:
            When playing: DistantInteractor
                          Interact through sockets with the players
            When testing: DeafInteractor
                          Create mock players with simulated inputs.

        - player_interactor_parameters:
          Example:
            When playing: player_interactor_parameters is None.
            When testing: => List of lists of lists
                          => Contains all the messages that will be sent
                             by each player during each game
                             of the whole session.
        """

        Session.__init__(self, interactor)

        # Keep track of the number of games played during the session.
        self.games_played = 0

        # Keep track of the number of players in each game that was played.
        self.players_number = {}

        # Interactor class used to interact with the players
        self.player_interactor_factory = player_interactor_factory

        # Attributes of the Session
        self.maps = []
        self.current_game = None
        self.play = True

        # Server connection
        self.main_connection = None

        # Client connections (one per client)
        self.connected_players = []

    def launch(self):
        """
        Launch the session.
        A session is a loop doing the following steps.
        Until no clients are connected:
        - Have the server choose a map for the next game
        - Wait for new clients.
        - When one of the clients enters the C command, launch a game.
        - After the game, remove the clients that want to stop playing.
        - If no client is left, close the main connection and exit the loop.
        """

        while self.play:

            # Choose a game
            self.choose_game()
            if not self.play:
                break

            # Start the server connection and wait for the clients to connect
            self.wait_for_clients()
            if not self.play:
                break

            # Add the currently connected players to the game.
            for player in self.connected_players:
                self.current_game.add_player(player)

            # Play the game
            self.current_game.play()

            # Remove the players that left the game.
            for player in self.connected_players:
                if player.has_left:
                    self.connected_players.remove(player)

            clients_number = len(self.connected_players)
            self.players_number[self.games_played] = clients_number
            self.games_played += 1

            # Once the game is finished, decide if a new game is launched
            self.continue_or_stop()

    def load_maps(self):
        """
        Loads maps present in dir_maps.
        """

        for name_file in os.listdir(parameters.dir_maps):
            if name_file.endswith(".txt"):
                map_path = os.path.join(parameters.dir_maps, name_file)
                map_name = name_file[:-4].lower()
                with open(map_path, "r") as map_file:
                    try:
                        self.maps.append(Map(map_name, map_file.read()))
                    except ValueError as error_creating_map:
                        self.print(error_creating_map)

    def choose_game(self):
        """
        Prompts the user to choose between the possible maps.
        """
        self.current_game = None

        for player in self.connected_players:
            player.send("En attente du choix d'un labyrinthe côté serveur.")

        # Valid inputs are the maps big enough for all connected users to play.
        rg = range(1, len(self.maps) + 1)
        player_nb = len(self.connected_players)
        maps_max = [m.max_players for m in self.maps]

        valid_inputs = [str(n) for n in rg if maps_max[n - 1] >= player_nb]

        if len(self.maps) != 0:
            self.print_maps()

            # Ask the server to choose a maps.
            prompt = "Veuillez saisir le labyrinthe de votre choix: "
            map_number = ""
            while map_number not in valid_inputs + ['0']:
                map_number = self.get(prompt).upper()

                if map_number not in valid_inputs + ['0']:
                    choices = ", ".join(valid_inputs)
                    message = "Saisies autorisées: {}.".format(choices)
                    self.print(message)

            if map_number == '0':
                # The user wants to close the session.
                self.close()
            else:
                current_map = self.maps[int(map_number) - 1]
                message = "Labyrinthe choisi: {}.\n".format(int(map_number))
                self.print(message)
                self.current_game = Game(current_map, self.interactor)
        else:
            self.print("Aucune carte n'est disponible.\n")

    def wait_for_clients(self):
        """
        This method is called just after a map was chosen.
         - It creates a server socket if needed
         - It waits for new clients to connect to the server
         - It terminates when a user has entered the command 'c'.
        """

        # Check if there is room for more players
        wait_for_c = True
        still_room_left = self.max_not_reached(verbose=True)

        # Wait for new clients to connect by listening to main_connection.
        while wait_for_c and self.play:

            candidates = self.player_interactor_factory.create()

            for candidate in candidates:
                if still_room_left:
                    self.add_player(candidate)
                    # Check if there is still room for newcomers
                    still_room_left = self.max_not_reached(verbose=False)
                else:
                    candidate.print("0")
                    candidate.close()

            # Listen to the connected clients.
            # When a client enters c, the game starts.
            players_talking = []
            for player in self.connected_players:
                selected = player.select(True)
                if selected is not None:
                    players_talking.append(selected)

            # Read messages received from clients
            for player in players_talking:
                received_message = player.recv()
                if received_message == "0":

                    # The player wants to exit the session.
                    self.remove_player(player)
                    nb = len(self.connected_players)
                    self.print("Il y a {} joueurs connecté(s).".format(nb))
                    if nb == 0:
                        message = self.get("Souhaitez-vous mettre fin à cette session? O/N ")
                        while message.upper() not in ["N", "O", "0"]:
                            message = self.get("Les seules saisies autorisées sont O et N.")
                        if message.upper() in ["O", "0"]:
                            self.close()
                        else:
                            self.print("En attente de connexion des joueurs.\n")

                elif received_message.upper() == "C":
                    wait_for_c = False
                else:
                    message = "Les seules saisies autorisées " \
                              "sont c ou C pour commencer le jeu."
                    player.send(message)

    def max_not_reached(self, verbose):
        """
        Returns True if the current_game can still have more players.
                False if the max number of players has been reached.
        """
        max_number = self.current_game.game_map.max_players
        still_room_left = len(self.connected_players) < max_number
        if still_room_left:
            if verbose:
                self.print("En attente de connexion des joueurs.\n")

                # If clients are already connected,
                # give them instructions to start the game.
                for player in self.connected_players:
                    player.send("En attente de nouveaux joueurs.")
                    mes = "Lorsque tout le monde est connecté," \
                          " saisissez c ou C pour lancer le jeu."
                    player.send(mes)
        else:
            # If clients are already connected,
            # give them instructions to start the game.
            for player in self.connected_players:
                mes = "Nombre maximal de joueurs atteint pour la carte choisie."
                player.send(mes)
                player.send("Saisissez c ou C pour lancer le jeu.")

        return still_room_left

    def add_player(self, player):
        """
        Add a new player to the session.
        """
        # Create a player
        new_player = Player(player)

        # Add it to the session and current game
        self.connected_players.append(new_player)

        # Greet the new client and send instructions.
        new_player.send("Bienvenue dans le jeu Roboc.")
        new_player.send("Saisissez c ou C pour lancer le jeu.")
        nb = len(self.connected_players)
        self.print("Il y a {} joueurs connecté(s).".format(nb))

    def remove_player(self, player):
        """Retirer le joueur de la liste et le déconnecter"""
        if not player.has_left:
            player.send("Au revoir!")
            player.send("0")
            player.close()
        self.connected_players.remove(player)

    def continue_or_stop(self):
        """
        Check if the clients want to start a new game.
        """
        players = self.connected_players

        # Check if the users want to continue playing
        for player in players:
            player.send("Souhaitez-vous continuer à jouer ? O/N ")

        pending_answers = len(players)

        while pending_answers > 0:
            players_talking = []

            for player in players:
                selected = player.select(True)
                if selected is not None:
                    players_talking.append(selected)

            # Read messages received from clients
            for player in players_talking:
                received_message = player.recv()

                if received_message.upper() not in ["O", "N", "0"]:
                    player.send("Les seules saisies autorisées sont O ou N.")
                else:
                    pending_answers -= 1
                    if received_message.upper() in ["N", "0"]:
                        self.remove_player(player)

        if len(self.connected_players) == 0:
            self.print("Il n'y a plus aucun joueur connecté.\n")
            message = self.get("Souhaitez-vous mettre fin à cette session? O/N ")
            while message.upper() not in ["N", "O", "0"]:
                message = self.get("Les seules saisies autorisées sont O et N.")
            if message.upper() in ["O", "0"]:
                self.close()

    def print_maps(self):
        """
        Prints currently loaded maps.
        """
        if len(self.maps) == 0:
            self.print("\nAucun labyrinthe chargé.")
        else:
            self.print("\nLabyrinthes existants :")
            for i, m in enumerate(self.maps):
                message = " - {0} : Labyrinthe {1}".format(i + 1, m)
                self.print(message)

    def close(self):
        """Close the connections with the players and the main connection."""
        for player in self.connected_players:
            self.remove_player(player)
        self.play = False
        self.print("Fermeture de la connexion.")
        self.player_interactor_factory.close()
