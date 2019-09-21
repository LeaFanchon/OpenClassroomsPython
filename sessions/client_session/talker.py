# -*-coding:Utf-8 -*

"""Used for talking to the server"""


class Talker:

    """Used for taking to the server"""

    def __init__(self, client_session):
        self.session = client_session

    def run(self):
        """Keep sending all the input of the user to the server."""
        while self.session.server_interactor.connected:
            to_send = self.session.get("")
            self.session.server_interactor.print(to_send)
