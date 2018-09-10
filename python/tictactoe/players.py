import string
import random

from . import exceptions
from .ai import algorithms


class Player:
    label = None
    _token = None

    def __init__(self, label=None):
        if label is not None:
            self.label = label

    def __str__(self):
        return self.label

    @property
    def token(self):
        return self._token

    @token.setter
    def token(self, token):
        token = token.upper()
        if token not in string.ascii_uppercase:
            raise exceptions.ImproperTokenError()
        self._token = token


class Human(Player):
    label = "Human"


class Computer(Player):
    label = "Computer"

    def __init__(self, label=None, difficulty="Easy", seed=None):
        super().__init__(label=label)
        self.difficulty = difficulty
        self.prng = random.Random(seed)

    def eval(self, board):
        return self._difficulty_func(self, board)

    @property
    def difficulty(self):
        return self._difficulty_label

    @difficulty.setter
    def difficulty(self, token):
        self._difficulty_label = token
        self._difficulty_func = algorithms[token.lower()]
