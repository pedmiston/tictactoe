import itertools
from collections import namedtuple

from tictactoe import exceptions, patterns


# A Move is a space occupied by a token
Move = namedtuple("Move", ["space", "token"])


class Board:
    def __init__(self, tokens=None):
        """Initialize a board as a list of spaces and save player tokens."""
        # fmt: off
        self.b = [
            "0", "1", "2",
            "3", "4", "5",
            "6", "7", "8",
        ]
        # fmt: on
        self.tokens = tokens or ["X", "O"]
        self.moves = []  # record of moves

    def __getitem__(self, key):
        """Return the token on the board by its index."""
        try:
            token = self.b[int(key)]
        except (ValueError, IndexError) as err:
            raise exceptions.KeyNotOnBoardError(err)
        else:
            return token

    def __setitem__(self, key, token):
        """Place a token on the board.

        >>> board[4] = "X"  # attempts to place token "X" in space 4
        """
        prev = self[key]
        if prev == token:
            raise exceptions.SpotAlreadySelectedError()
        elif prev in self.tokens:
            raise exceptions.SpotTakenByOpponentError()
        else:
            self.b[int(key)] = token
            self.moves.append(Move(key, token))

    def find_winning_pattern(self):
        for s1, s2, s3 in patterns.winning_patterns:
            if self.b[s1] == self.b[s2] == self.b[s3]:
                return s1, s2, s3
        return -1, -1, -1

    def is_over(self):
        return any(
            self[s1] == self[s2] == self[s3] for s1, s2, s3 in patterns.winning_patterns
        )

    def is_tie(self):
        return all(token in self.tokens for token in self.b)

    def available(self):
        return [int(token) for token in self.b if token not in self.tokens]

    def available_corners(self):
        return [s for s in patterns.corners if self.b[s] not in self.tokens]

    def available_middles(self):
        return [s for s in patterns.middles if self.b[s] not in self.tokens]
