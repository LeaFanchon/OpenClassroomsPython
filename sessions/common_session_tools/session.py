# -*-coding:Utf-8 -*

"""
This module contains the class Session.
MainSession and ClientSession inherit from Session.
"""


class Session:

    def __init__(self, interactor):
        """
        Constructor of a session.
        """
        # Used to interact with the session
        self.interactor = interactor

    def launch(self):
        """
        Launches the session.
        """
        pass

    def print(self, message):
        """
        Use the Interactor to print the message.
        """
        self.interactor.print(message)

    def get(self, prompt):
        """
        Use the Interactor to get a message.
        """
        return self.interactor.get(prompt)
