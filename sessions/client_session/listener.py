# -*-coding:Utf-8 -*

"""Thread used for listening to the server"""

from threading import Thread


class Listener(Thread):

    """Thread used for listening to the server"""

    def __init__(self, client_session):
        Thread.__init__(self)
        self.session = client_session

    def run(self):
        """Keep listening to messages from the server."""
        while self.session.server_interactor.connected:
            received = self.session.server_interactor.get("")

            if received not in ["0", ""]:
                # A message has been received
                self.session.print(received)

            elif received == "0":
                # The server has closed the connection.
                self.session.print('\nLe serveur a mis fin à la connexion.')
                self.session.server_interactor.close()
                self.session.server_interactor.connected = False
