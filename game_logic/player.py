# -*-coding:Utf-8 -*

"""
Module containing the class Player.
"""


class Player:

    def __init__(self, interactor):
        """
        Constructor of the player.
        :param game: current game the player is playing
        :param interactor: used to communicate with the player
        :param position: initial position of the player on the map
        :param identifier: identifier of the player in this game
        :param game_map: map used for the game
        """
        self.row = None
        self.col = None
        self.direction = None
        self.steps_left = 0
        self.identifier = None
        self.current_step = None
        self.game_map = None
        self.game = None
        self.interactor = interactor
        self.has_left = False

    def greet(self):
        """
        Greet the player and tell him/her his/her identifier.
        Make him / her ready for the new game.
        """
        self.direction = None
        self.steps_left = 0
        self.current_step = None
        self.send("Dans cette partie, vous êtes Joueur {}".format(self.identifier))

    def ask_move(self):
        """
        Inform the player that it is his/her turn and ask for his/her next move.
        """
        self.current_step = None
        self.send("C'est à votre tour de jouer, Joueur {}.".format(self.identifier))

        # Finish a previous move of several steps if possible.
        if self.direction is not None:
            message = "Vous avez déjà pris la décision d'aller dans la direction {}.".format(self.direction)
            self.send(message)
            self.current_step = self.direction
            self.steps_left -= 1
            if self.steps_left == 0:
                self.direction = None

        # Else, ask the player for the next move.
        else:
            self.send("Où allez-vous?")

    def preprocess_move(self, move):
        """
        Once the player has entered a valid input 'move', preprocess it the following way:
        - If the player has just entered a direction:
                 Store it in current_step
        - If the player has also entered a number (ex N3):
                 Store the direction in current_step
                 Store the number of steps to take in that direction in steps_left
        - If the player has entered an instruction to create a wall or a door:
                 Store all of it in current_step.
        """
        self.current_step = move
        if len(move) > 1:
            try:
                # If the player entered a move of several steps, store them for later.
                if int(move[1:]) > 1:
                    self.direction = move[0]
                    self.steps_left = int(move[1:]) - 1
                    self.current_step = move[0]
                else:
                    self.current_step = move[0]
            except ValueError:
                # The player wants to transform a door into a wall or the opposite.
                pass

    @staticmethod
    def check_input(step):
        """
        Checks if the input entered by the user is valid.
        The input can be :
        - A direction, N, E, O or S
        - A request to see the instructions again (I)
        - A request to replace a door with a wall or the opposite.
        """
        valid = False
        if len(step) == 1:
            if step.upper() in ['I', 'Q', 'N', 'E', 'S', 'O']:
                valid = True
        elif len(step) > 1:
            if step[0].upper() in ['N', 'E', 'S', 'O']:
                try:
                    int(step[1:])
                except ValueError:
                    pass
                else:
                    if int(step[1:]) > 0:
                        valid = True
            elif len(step) == 2 \
                    and step[0].upper() in ['M', 'P'] \
                    and step[1].upper() in ['N', 'E', 'S', 'O']:
                valid = True

        return valid

    def check_move(self):
        """
        Checks if the move of the player can be performed.
        - The player can't create a door if there is no wall.
        - The player can't create a wall if there is no door.
        - The player can't pass through walls.
        - The player can't pass through other players.
        - The player can't exit the map except through the exit U.
        """

        valid = True

        if len(self.current_step) == 2:
            # If step is two characters long, it is an instruction to create a door or a wall.
            command = self.current_step[0]
            direction = self.current_step[1]
        else:
            # If step is just one character long, it means it is a move on the grid
            command = ""
            direction = self.current_step

        new_row, new_col = self.take_one_step(direction)

        width = self.game.game_map.width
        height = self.game.game_map.height

        message = ''

        if new_row < 0 or new_col < 0 or new_row > height - 1 or new_col > width - 1:
            # The player wants to go outside the map: get him/her back inside.
            message = "Attention, vous ne pouvez pas sortir par ici! La sortie est: U."
            valid = False

        elif command == 'P' and self.game_map.grid[new_row][new_col] != 'O':
            # The player wants to create a door in a wall, but there is no wall
            message = "Il n'y a pas de mur ici pour créer une porte!"
            valid = False

        elif command == 'M' and self.game_map.grid[new_row][new_col] != '.':
            # The player wants to transform a door into a wall, but there is no door.
            message = "Il n'y a pas de porte à murer ici!"
            valid = False

        elif command == '' and self.game_map.grid[new_row][new_col] == 'O':
            # The player attempts to pass through a wall
            message = "Attention, vous avez heurté un mur!"
            valid = False

        elif command == '':
            # Check if the player attempts to pass through another player
            for other_player in [p for p in self.game.players.values() if p is not self]:
                if new_row == other_player.row and new_col == other_player.col:
                    message = "Attention, vous avez heurté un autre joueur!"
                    valid = False
                    break

        if not valid:
            self.send(message)

        return valid

    def perform_move(self):
        """
        Perform the move wanted by the player.
        If the player wanted to create a wall or a door, create it.
        If the player wanted to move in the labyrinth, move accordingly.
        """

        step = self.current_step

        # If step is two characters long, it is an instruction to create a door or a wall.
        # If step is just one character long, it means it is a move on the grid

        if len(step) == 2:
            # The player wants to create a door or a wall.
            new_row, new_col = self.take_one_step(step[1])
            if step[0] == 'P':
                # We want to create a door in a wall
                self.game_map.grid[new_row][new_col] = '.'

            elif step[0] == 'M':
                # We want to transform a door into a wall
                self.game_map.grid[new_row][new_col] = 'O'

        else:
            # The player wants to move on the grid.
            # Move the position of the player in the map according to his/her choice.
            self.row, self.col = self.take_one_step(step)

    def take_one_step(self, direction):
        """
        Take one step in the given direction.
        """
        row = self.row
        col = self.col

        if direction == 'N':
            row -= 1
        elif direction == 'S':
            row += 1
        elif direction == 'E':
            col += 1
        elif direction == 'O':
            col -= 1
        return row, col

    def has_won(self):
        """
        Check whether the player has won the game.
        """
        won = False
        if self.game_map.grid[self.row][self.col] == 'U':
            won = True
            self.send("Félicitations ! Vous avez gagné.")
        return won

    def send(self, message):
        """
        Send a message to the player.
        """
        if not self.has_left:
            self.interactor.print(message)

    def recv(self):
        """
        Send a message to the player.
        """
        message = ""
        if not self.has_left:
            message = self.interactor.get("")
        return message

    def select(self, my_turn):
        """
        Check if the player has sent a message.
        my_turn is True if it is the player's turn to play.
        """
        result = None
        if not self.has_left and self.interactor.select(my_turn) is not None:
            result = self
        return result

    def close(self):
        """
        Closes the interaction with the player.
        """
        self.has_left = True
        self.interactor.close()
