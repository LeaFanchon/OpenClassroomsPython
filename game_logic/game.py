# -*-coding:Utf-8 -*


import random
from copy import deepcopy


class Game:
    """
    One game is one attempt to escape a labyrinth.
    """

    def __init__(self, game_map, interactor):
        """
        Constructor of Game.
        """

        # Used to interact with the server
        self.interactor = interactor

        # The map (or labyrinth) the players have to escape from.
        self.game_map = game_map

        # The status of the game : ongoing or finished.
        self.finished = False

        # Store the winner
        self.winner = None

        # Stores the sockets used to communicate with each player
        self.players = {}

        # Stores all available positions for new players
        self.available_positions = []
        self.find_available_positions()

        # The number of players
        self.player_number = 0

        # The number of players that left the game during the game.
        self.gone_players_number = 0

        # Whose turn it is to play among the players
        self.turn = 0

        # Store how many turns were played.
        self.how_many_rounds = 0

    def find_available_positions(self):
        """
        Find available positions for new players to come.
        """
        for i in range(0, self.game_map.height - 1):
            for j in range(0, self.game_map.width - 1):
                if self.game_map.grid[i][j] == " ":
                    self.available_positions.append((i, j))

    def add_player(self, player):
        """
        Add players to the game before it has started.
        Computes their initial position at random
        """

        # Compute its initial position at random
        position_choice = random.randint(0, len(self.available_positions)-1)
        position = self.available_positions[position_choice]
        player.row = position[0]
        player.col = position[1]

        # Compute identifier of the new player
        player.identifier = self.player_number + 1

        # Tells the player in which game it plays.
        player.game = self
        player.game_map = self.game_map

        # Add the given player to the game
        self.players[self.player_number] = player

        # This position is not available anymore
        self.available_positions.remove(position)

        # Increment the number of players
        self.player_number += 1

    def launch(self):
        """
        Called at the beginning of the game.
        - Greets all the players and makes them ready for the new game,
        - Sends them the instructions and the current state of the game,
        - Ask for the first move of the first player.
        """
        for player in self.players.values():
            player.greet()

        self.send_all('La partie commence! '
                      'Vous devez vous échapper du labyrinthe...')
        self.send_all(self.get_instructions())
        self.send_all(self.get_current_state())

        player = self.players[self.turn]

        # Skip a line in the client
        self.send_all("$", server=False)

        # Inform the other players it is the turn of player.
        message = "\nC'est au tour du Joueur {}.".format(player.identifier)
        self.send_all(message, server=True, except_player=player)

        # Tell the first player it is his / her turn to play.
        player.ask_move()

    def play(self):
        """
        Play one entire game.
        - Launch the game.
        - Then ask each player for his/her next move.
        - Perform the move if it is valid
        - Continue until one of the players has won the game.
        """

        self.launch()

        # Game loop. Each iteration of the loop is one move from a player.
        while not self.finished:

            # Listen to the connected clients.
            # For now, we only pay attention to the client whose turn it is to play.
            player = self.players[self.turn]

            while player.current_step is None:
                self.wait_for_current_step()

            if self.player_number == self.gone_players_number:
                # Everyone has left the game
                self.finished = True
                break

            if not player.has_left:
                if player.check_move():
                    player.perform_move()

                # Increment the number of rounds played
                self.how_many_rounds += 1

                # Check if the player has won
                self.finished = player.has_won()

            self.next_turn()

    def wait_for_current_step(self):
        """
        Scan all the messages received from the players.
        Continue until the player whose turn it is to play
        has sent a valid input.

        If the future, the messages received here from the
        other players could be used to implement a chat.
        """
        player = self.players[self.turn]

        players_talking = []
        for p in self.players.values():
            selected = p.select(p is player)
            if selected is not None:
                players_talking.append(selected)

        # Read messages received from clients
        for p in players_talking:
            received_message = p.recv()

            if received_message == '0':
                # A player has left the game.
                message = "Le Joueur {} a quitté la partie.".format(p.identifier)
                self.send_all(message, server=True, except_player=p)
                p.send("Vous avez quitté la partie. Au revoir!")
                p.send("0")
                p.close()
                self.gone_players_number += 1
                player.current_step = "0"

            if p is not player:
                # For now, we just answer the player that
                # it is not his/her turn to play.
                # In the future, we could send the message
                # to another player and make a chat.
                p.send("Ce n'est pas encore à votre tour de jouer.")

            elif not p.has_left:
                # Get the input from the player whose turn it is to play.
                move = received_message.upper()
                if not player.check_input(move):
                    player.send("Saisie incorrecte. "
                                "Pour revoir les instructions, saisissez I.")
                elif move == "I":
                    player.send(self.get_instructions())
                else:
                    player.preprocess_move(move)

    def next_turn(self):
        """
        Once the player whose turn it is has made a move,
        go on to the next turn.
        """
        player = self.players[self.turn]
        identifier = player.identifier
        step = player.current_step

        if self.finished:
            self.winner = player
            message = "Le Joueur {} a gagné la partie.".format(identifier)
            self.send_all(message, server=True)
        else:
            if not player.has_left:
                message = "Le Joueur {0} a joué {1}.".format(identifier, step)
                self.send_all(message, server=True)

                self.send_all(self.get_current_state())

            next_player = None
            while next_player is None or next_player.has_left:
                self.turn += 1
                self.turn = self.turn % self.player_number
                next_player = self.players[self.turn]

            next_id = next_player.identifier

            # Skip a line in the client
            self.send_all("$", server=False)

            # Inform the other players it is the turn of next_player.
            message = "\nC'est au tour du Joueur {}.".format(next_id)
            self.send_all(message, server=True, except_player=next_player)

            # Tell the next player it is his / her turn to play.
            next_player.ask_move()

    def send_all(self, message, server=False, except_player=None):
        """
        Send message to every player in the game.
        If server is True, print the message to the server console.
        If except_player is not None, don't send the message to him/her.
        """
        recipients = list(self.players.values())
        if except_player is not None:
            recipients.remove(except_player)
        for player in recipients:
            player.send(message)
        if server:
            self.interactor.print(message)

    @staticmethod
    def get_instructions():
        """
        Returns the instructions to play the game.
        """
        instructions = """\nLes commandes à votre disposition sont les suivantes:
            - Les 4 directions : N (Nord), S (Sud), E (Est) et O (Ouest);
            - Une direction suivie d'un nombre n > 0, pour avancer de n cases;
            - M et une direction, pour murer une porte;
            - P et une direction, pour Ouvrir une porte dans un mur.
            - Pour revoir ces instructions, saisissez I. 
            - Pour quitter, saisissez Ctrl + C ou Q.\n
            """
        return instructions

    def get_current_state(self):
        """
        Returns a byte string containing the current state
        of the game with the positions of each player.
        Each player is represented on the map by his / her identifier.
        """
        shown_grid = deepcopy(self.game_map.grid)

        # Position each player on the map
        for player in self.players.values():
            shown_grid[player.row][player.col] = str(player.identifier)

        result = ''.join([c for row in shown_grid for c in row + ["\n"]])
        return '\n'+result
