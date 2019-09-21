# -*-coding:Utf-8 -*

"""This module contains the class Map."""
import parameters.parameters as parameters


class Map:

    """A map (or labyrinth)"""

    # List of reasons that make a map invalid
    INVALID_CHARS_ERROR = "La carte {} contient des caractères invalides."
    U_COUNT_ERROR = "La carte {} ne peut contenir qu'un seul caractère 'U'."
    NON_RECTANGULAR_ERROR = "La carte {} n'est pas rectangulaire."
    TOO_SMALL_ERROR = "La carte {} est trop petite."
    TOO_LARGE_ERROR = "La carte {} est trop volumineuse."

    def __init__(self, name, content):
        """
        Constructor of a Map.
        Construction fails if:
        - "ccntent" contains only valid items for a map,
        - The map has only one exit,
        - The map is rectangular,
        - The map is neither too small nor to big.

        :param name: Name of the map
        :param content: String to be converted into a usable map.
        """
        self.name = name

        is_valid, message = self.is_valid(content.upper())
        if not is_valid:
            raise ValueError(message.format(self.name))

        # Remove "X"s in the map if there are some.
        # The initial position of the players is now computed at random.
        content = content.replace('X', ' ')

        # The map is loaded as a list of lists
        self.grid = [list(row) for row in content.split('\n')]

        # Maps are rectangular. We store their width and height.
        self.width = len(self.grid[0])
        self.height = len(self.grid)

        # Initial positions of players are computed at random.
        # They are chosen among the blank spots of the map.
        # It is impossible to have more players than there are blanks.
        # It is also impossible for now to have more than 9 players,
        # because each player is represented on the map with an integer.
        self.max_players = min(9, content.count(' '))

    def __repr__(self):
        return self.name

    @staticmethod
    def is_valid(content):
        """
        Check if content is a valid map, meaning:
        - "ccntent" contains only valid items for a map,
        - The map has only one exit,
        - The map is rectangular,
        - The map is neither too small nor to big.
        :param content: String to be converted into a usable map.
        """
        # Check if there are invalid characters
        invalid_characters = [c for c in content if c not in parameters.valid_map_items]
        if len(invalid_characters) > 0:
            return False, Map.INVALID_CHARS_ERROR

        count_u = content.count('U')
        if count_u != 1:
            return False, Map.U_COUNT_ERROR

        # Check if the map is a rectangle
        row_lengths = set([len(row) for row in content.split('\n')])
        if len(row_lengths) != 1:
            return False, Map.NON_RECTANGULAR_ERROR

        grid = [list(row) for row in content.split('\n')]
        row_length = len(grid[0])
        col_length = len(grid)

        # Check if the map reaches minimum length requirements
        if row_length < parameters.map_min_size or col_length < parameters.map_min_size:
            return False, Map.TOO_SMALL_ERROR

        # Check if the map exceeds maximum length requirements
        if row_length > parameters.map_max_size or col_length > parameters.map_max_size:
            return False, Map.TOO_LARGE_ERROR

        return True, ""
