# -*-coding:Utf-8 -*

"""
Execute this file to launch the server side of the game of roboc.
"""

from sessions.server_session.server_session import MainSession
from sessions.common_session_tools.interactor import ShellInteractor, ClientInteractorFactory

session = MainSession(ShellInteractor(), ClientInteractorFactory())
session.load_maps()
session.launch()

input('Appuyez sur une touche pour continuer...')
