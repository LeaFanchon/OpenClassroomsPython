# -*-coding:Utf-8 -*

"""
Execute this file to join a game of roboc.
"""

from sessions.client_session.client_session import ClientSession
from sessions.common_session_tools.interactor import ShellInteractor

session = ClientSession(ShellInteractor())
session.launch()

input('Appuyez sur une touche pour continuer...')
