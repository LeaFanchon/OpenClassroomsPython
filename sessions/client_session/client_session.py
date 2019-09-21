# -*-coding:Utf-8 -*

"""
This module contains the class ClientSession.
ClientSession is the class used to implement the client in the roboc game.
"""

import socket
from threading import RLock

from sessions.client_session.listener import Listener
from sessions.client_session.talker import Talker

from sessions.common_session_tools.session import Session
from sessions.common_session_tools.singleton import decorator_singleton
from sessions.common_session_tools.interactor import ServerInteractor


@decorator_singleton
class ClientSession(Session):

    def __init__(self, interactor):
        """
        Constructor of a ClientSession.
        ClientSession is a Singleton.
        - Creates a connection with the server
        - Connects with the server
        """
        # Create the session with the interactor used to communicate with the user
        Session.__init__(self, interactor)

        self.lock = RLock()

        # server_interactor: used to communicate with the server
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_interactor = ServerInteractor(server_socket)
        self.print("En attente du serveur.")
        self.server_interactor.connect()
        self.connected = True
        self.print("Vous êtes connecté au serveur.")

    def launch(self):
        """
        Launches a ClientSession.
        - Launches a Listener thread to get the messages arriving from the server.
        - Launches simultaneously a Talker thread to send messages to the server.
        - Runs until both threads are closed.
        """

        listener = Listener(self)
        listener.daemon = True
        listener.start()

        talker = Talker(self)
        talker.run()

        self.print("Fermeture de la connexion.")
        self.server_interactor.close()

    def print(self, message):
        """Print a message to screen with a lock."""
        with self.lock:
            Session.print(self, message)
