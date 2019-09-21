# -*-coding:Utf-8 -*

"""
This module contains the decorator decorator_sngleton.
It is used by the classes MainSession and ClientSession to make them singletons.
"""


def decorator_singleton(session):
    """
    Decorator to make session a singleton.
    """
    instance = None

    def new_constructor(*args, **kwargs):
        nonlocal instance
        if instance is None:
            instance = session(*args, **kwargs)
        return instance
    return new_constructor
