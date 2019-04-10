import itertools
from collections import namedtuple

from tictactoe import exceptions


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
        for s1, s2, s3 in get_winning_patterns():
            if self.b[s1] == self.b[s2] == self.b[s3]:
                return s1, s2, s3
        return -1, -1, -1

    def is_over(self):
        return any(
            self[s1] == self[s2] == self[s3]
            for s1, s2, s3 in get_winning_patterns()
        )

    def is_tie(self):
        return all(token in self.tokens for token in self.b)

    def available(self):
        return [int(token) for token in self.b if token not in self.tokens]

    def available_corners(self):
        return [s for s in corners if self.b[s] not in self.tokens]

    def available_middles(self):
        return [s for s in middles if self.b[s] not in self.tokens]


def get_winning_patterns():
    winning_patterns = set(
        [
            (0, 1, 2),
            (3, 4, 5),
            (6, 7, 8),
            (0, 3, 6),
            (1, 4, 7),
            (2, 5, 8),
            (0, 4, 8),
            (2, 4, 6),
        ]
    )
    return winning_patterns


def make_partial_patterns(winning_patterns):
    """Create a map of partial patterns to the spaces that complete the patterns.

    >>> partial_patterns[frozenset((0, 2))] == 1
    """
    partial_patterns = {}
    for s1, s2, s3 in winning_patterns:
        partial_patterns[frozenset((s1, s2))] = s3
        partial_patterns[frozenset((s1, s3))] = s2
        partial_patterns[frozenset((s2, s3))] = s1
    return partial_patterns


def make_outer_patterns(winning_patterns):
    """Create a list of outer patterns that don't include the center square."""
    return [pattern for pattern in winning_patterns if 4 not in pattern]


def make_diagonal_patterns(winning_patterns, corners):
    diagonal_patterns = []
    for s1, s2, s3 in winning_patterns:
        if s2 == 4 and all(s in corners for s in [s1, s3]):
            diagonal_patterns.append((s1, s2, s3))
    return diagonal_patterns


corners = [0, 2, 6, 8]
middles = [1, 3, 5, 7]
winning_patterns = get_winning_patterns()
partial_patterns = make_partial_patterns(winning_patterns)
outer_patterns = make_outer_patterns(winning_patterns)
diagonal_patterns = make_diagonal_patterns(winning_patterns, corners)
