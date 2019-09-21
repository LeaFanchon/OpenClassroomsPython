# -*-coding:Utf-8 -*

"""
Define interactors to communicate with the user.
"""

import select
import socket
import time

import parameters.parameters as parameters


class Interactor:
    """
    Interactor class.
    Used to communicate with either a player or the server.

    To play the game:
    - The ShellInteractor is inherited from Interactor.
      It is used to communicate with the server through the shell
    - The DistantInteractor communicates with each player with a socket.

    To test the functionalities of the game:
    - DeafInteractor simulates the behaviors of the players and the server.
    """

    @staticmethod
    def print(message):
        """
        Send a message.
        """
        pass

    def get(self, prompt):
        """
        Get a message.
        """
        pass

    def select(self, my_turn=True):
        """
        Finds if a message is pending.
        Useful mostly for DistantIterator child class.
        Checks whether the socket contains a message.
        """
        return self

    def connect(self, other_socket):
        """Used in the client session to connect to the server"""
        pass

    def close(self):
        """
        Close the interaction with the interactor.
        Useful mostly for DistantIterator child class.
        Closes the socket connection.
        """
        pass


class ShellInteractor(Interactor):
    """
    Used to communicate with the user through the shell.
    Used for the server interactions.
    """
    @staticmethod
    def print(message):
        """Prints a message to the shell."""
        print(message)

    def get(self, prompt):
        """
        Gets a message entered in the shell.
        The user can exit the session by entering:
        - Q or q
        - 0
        - Ctrl + C
        """
        try:
            message = input(prompt)
            if message.upper() == "Q":
                message = "0"
        except KeyboardInterrupt:
            message = "0"
        return message


class DistantInteractor(Interactor):
    """
    Communicate with a distant user.
    Used for communication between the clients and the server.
    """
    def __init__(self, socket):
        """
        Constructor of DistantInteractor.
        """
        self.socket = socket

    def print(self, message):
        """Sends the message to the socket"""
        try:
            self.socket.send(message.encode() + b'\n')
        except (ConnectionResetError, OSError):
            pass

    def get(self, prompt):
        """Receives message from the socket."""
        try:
            message = b''
            while True:
                c = self.socket.recv(1)
                if c in [b'\n', b'']:
                    break
                if c == b'$':
                    c = b'\n'
                message += c
            message = message.decode()
        except (ConnectionResetError, OSError):
            message = "0"

        return message

    def close(self):
        """
        Close the interaction with the interactor.
        """
        self.socket.close()


class ClientInteractor(DistantInteractor):
    """
    Communicate with a distant user.
    Used by the server session to communicate with the clients.
    """

    def select(self, my_turn):
        """
        Return the interactor if a message is pending.
        Else, returns None.
        """
        result = None
        is_talking, wlist, xlist = select.select([self.socket], [], [], 0.05)
        if is_talking:
            result = self
        return result


class ServerInteractor(DistantInteractor):
    """
    Communicate with a distant server.
    Used by the client sessions to communicate with the server.
    """

    def __init__(self, socket):
        """
        Constructor of DistantInteractor.
        """
        DistantInteractor.__init__(self, socket)
        self.connected = False

    def connect(self):
        """
        Connect the socket to a distant connection.
        """
        # Connect to the server
        while not self.connected:
            try:
                self.socket.connect((parameters.client_host, parameters.port))
            except ConnectionRefusedError:
                time.sleep(5)
            else:
                self.connected = True


class DeafInteractor(Interactor):
    """
    Used to simulate a player during tests.
    - The print method doesn't do anything.
    - The get method returns one after the other the values
      of the parameter 'outputs' given to the constructor.
    Once they've all been returned, we return the empty string.
    """
    def __init__(self, outputs):
        """
        Constructor of DeafInteractor.
        """
        # Which element of outputs is next to be returned by the get method.
        self.next_output = 0

        # Ouputs is a list.
        # It lists all the consecutive outputs returned by the get method.
        self.outputs = outputs

    @staticmethod
    def print(message):
        """Stays mute"""
        pass

    def get(self, prompt):
        """
        Returns the next output.
        If all outputs have already been returned, return the emty string.
        """
        if self.next_output < len(self.outputs):
            result = self.outputs[self.next_output]
            self.next_output += 1
        else:
            result = ''
        return result

    def select(self, my_turn):
        """
        Find if a message is pending.
        The mock player returns something only if it is his/her turn.
        """
        selected = None
        if self.next_output < len(self.outputs) and my_turn:
            selected = self
        return selected


class InteractorFactory:
    def create(self):
        pass

    def close(self):
        pass


class ClientInteractorFactory(InteractorFactory):

    def __init__(self):
        """
        Launch the main connection.
        """
        self.main_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.main_connection.bind((parameters.host, parameters.port))
        self.main_connection.listen(5)

    def create(self):
        """
        Detects the new sockets willing to connect to main_connection.
        Accept the connection requests.
        Returns new interactors for each connection request.
        """
        interactors = []
        requests, wlist, xlist = select.select([self.main_connection], [], [], 0.05)
        for connection in requests:
            client_connection, client_connection_infos = connection.accept()
            interactors.append(ClientInteractor(client_connection))
        return interactors

    def close(self):
        """
        Closes the main connection opened in the constructor of the factory.
        """
        self.main_connection.close()


class DeafInteractorFactory(InteractorFactory):

    def __init__(self, messages_per_interactor):
        """
        Messages is a list of lists.
        It contains, for each interactor to be created,
        the list of everything it will say.
        """
        self.messages_per_interactor = messages_per_interactor

    def create(self):
        """
        Create one interactor for each of the
        sublists of messages_per_interactor.
        """
        interactors = []
        for messages in self.messages_per_interactor:
            interactors.append(DeafInteractor(messages))

        self.messages_per_interactor = []
        return interactors
