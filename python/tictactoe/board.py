import string
import random

from . import exceptions
from .ai import algorithms


class Board:
    corners = ["0", "2", "6", "8"]
    middle = ["1", "3", "5", "7"]

    winning_patterns = [
        (0, 1, 2),
        (3, 4, 5),
        (6, 7, 8),
        (0, 3, 6),
        (1, 4, 7),
        (2, 5, 8),
        (0, 4, 8),
        (2, 4, 6),
    ]

    def __init__(self, tokens=None):
        self.tokens = tokens or ["X", "O"]
        self._board = ["0", "1", "2", "3", "4", "5", "6", "7", "8"]
        self.token_sequence = []

    def __getitem__(self, key):
        """Returns the token at a particular square."""
        try:
            token = self._board[int(key)]
        except (ValueError, IndexError):
            raise exceptions.KeyNotOnBoardError()
        else:
            return token

    def __setitem__(self, key, value):
        """Places a token on the board.

        >>> board[4] = "X"  # attempts to place "X" in square 4
        """
        prev = self[key]
        if prev == value:
            raise exceptions.SpotAlreadySelectedError()
        elif prev in self.tokens:
            raise exceptions.SpotTakenByOpponentError()
        self._board[int(key)] = value
        self.token_sequence.append(str(key))

    def three_in_a_row(self, *args):
        return (
            args[0] == args[1] == args[2] == self.tokens[0]
            or args[0] == args[1] == args[2] == self.tokens[1]
        )

    def is_over(self):
        b = self._board
        return (
            self.three_in_a_row(b[0], b[1], b[2]) == 1
            or self.three_in_a_row(b[3], b[4], b[5]) == 1
            or self.three_in_a_row(b[6], b[7], b[8]) == 1
            or self.three_in_a_row(b[0], b[3], b[6]) == 1
            or self.three_in_a_row(b[1], b[4], b[7]) == 1
            or self.three_in_a_row(b[2], b[5], b[8]) == 1
            or self.three_in_a_row(b[0], b[4], b[8]) == 1
            or self.three_in_a_row(b[2], b[4], b[6]) == 1
        )

    def find_three_in_a_row(self):
        for a, b, c in self.winning_patterns:
            if self.three_in_a_row(self._board[a], self._board[b], self._board[c]) == 1:
                return a, b, c
        return -1, -1, -1

    def find_two_in_a_row(self, token=None, blocking_token=None):
        if blocking_token is not None:
            _tokens = self.tokens.copy()
            _tokens.remove(blocking_token)
            token = _tokens[0]

        for a, b, c in self.winning_patterns:
            if (
                self._board[a] == self._board[b]
                and self._board[c] == str(c)
                and (token is None or token == self._board[a])
            ):
                return c
            elif (
                self._board[b] == self._board[c]
                and self._board[a] == str(a)
                and (token is None or token == self._board[b])
            ):
                return a
            elif (
                self._board[a] == self._board[c]
                and self._board[b] == str(b)
                and (token is None or token == self._board[a])
            ):
                return b

        return -1

    def is_tie(self):
        return len([s for s in self._board if s in self.tokens]) == 9

    @property
    def available(self):
        return [s for s in self._board if s not in self.tokens]

    def available_corners(self):
        return [s for s in self.corners if self[s] not in self.tokens]

    @property
    def turn(self):
        return len([s for s in self._board if s in self.tokens])

    def get_last_token_location(self):
        return self.token_sequence[-1]
