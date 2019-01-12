import string
import random
from tictactoe import ai, exceptions


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
        self.prng = random.Random(seed)
        self.difficulty = difficulty

    def move(self, board):
        return self.difficulty_func(self, board)

    @property
    def difficulty(self):
        return self.difficulty_label

    @difficulty.setter
    def difficulty(self, label):
        """Set a player difficulty by selecting a function in the ai module."""
        self.difficulty_label = label
        self.difficulty_func = getattr(ai, label.lower())
