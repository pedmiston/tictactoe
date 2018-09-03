import string
import random

from . import exceptions


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

    @property
    def turn(self):
        return len([s for s in self._board if s in self.tokens])

    def get_last_token_location(self):
        return self.token_sequence[-1]


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
        return self._difficulty_func(board)

    @property
    def difficulty(self):
        return self._difficulty_label

    @difficulty.setter
    def difficulty(self, token):
        self._difficulty_label = token
        self._difficulty_func = getattr(self, f"difficulty_func_{token.lower()}")

    def difficulty_func_easy(self, board):
        return self.prng.choice(board.available)

    def difficulty_func_medium(self, board):
        # are there two of mine in a row? -> win
        # are there two of my opponents in a row? -> block

        if board.turn == 0:
            move = "4"
        else:
            move = self.prng.choice(board.available)
        return move

    def difficulty_func_hard(self, board):
        winning_move = board.find_two_in_a_row(token=self.token)
        if winning_move != -1:
            return winning_move

        blocking_move = board.find_two_in_a_row(blocking_token=self.token)
        if blocking_move != -1:
            return blocking_move

        if board.turn == 0:
            move = self.choose_corner(board)
        elif board.turn == 1:
            prev_move = board.get_last_token_location()
            if prev_move == "4":
                move = self.choose_corner(board)
            else:
                move = "4"
        elif board.turn == 2:
            # first move was corner
            move = self.choose_adjacent_corner(board)
        else:
            move = self.prng.choice(board.available)
        return move

    def choose_corner(self, board):
        return self.prng.choice([s for s in board.available if s in board.corners])

    def choose_adjacent_corner(self, board):
        prev_corner = [s for s in board.corners if board[s] == self.token][0]
        for a, b, c in board.winning_patterns:
            if str(a) == prev_corner and board[b] == str(b) and board[c] == str(c):
                return str(c)
            elif str(c) == prev_corner and board[b] == str(b) and board[a] == str(a):
                return str(a)
        return -1
