import string
import random
from tictactoe import exceptions, patterns


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

    def __init__(self, label=None, seed=None):
        super().__init__(label=label)
        self.prng = random.Random(seed)

    def move(self, board):
        raise NotImplementedError()

    def find_winning_move(self, board, token=None):
        token = token or self.token
        for (s1, s2), s3 in patterns.partial_patterns.items():
            if board[s1] == board[s2] == token and board[s3] not in board.tokens:
                return s3
        return -1

    def find_blocking_move(self, board):
        opponent_token = (set(board.tokens) - set(self.token)).pop()
        return self.find_winning_move(board, token=opponent_token)

    def find_adjacent_corner(self, board):
        for s1, s2, s3 in patterns.outer_patterns:
            if board[s1] == self.token and board[s2] == str(s2):
                return s3
            if board[s3] == self.token and board[s2] == str(s2):
                return s1
        return -1

    def find_opposite_corner(self, board):
        for s1, s2, s3 in patterns.diagonal_patterns:
            if board[s1] == self.token:
                return s3
            if board[s3] == self.token:
                return s1
        return -1


class EasyComputer(Computer):
    difficulty = "Easy"

    def move(self, board):
        """Choose one of the available spaces at random."""
        return self.prng.choice(board.available())


class MediumComputer(Computer):
    difficulty = "Medium"

    def move(self, board):
        """Win or block if able, otherwise pick center or at random."""
        winning_move = self.find_winning_move(board)
        if winning_move != -1:
            return winning_move

        blocking_move = self.find_blocking_move(board)
        if blocking_move != -1:
            return blocking_move

        if board[4] == "4":  # center square is open
            return 4
        else:
            return self.prng.choice(board.available())


class HardComputer(Computer):
    difficulty = "Hard"

    def move(self, board):
        """Optimally select positions on a board."""
        # If you can win, win.
        winning_move = self.find_winning_move(board)
        if winning_move != -1:
            return winning_move

        # If you need to block, block.
        blocking_move = self.find_blocking_move(board)
        if blocking_move != -1:
            return blocking_move

        turn = len(board.moves)
        if not turn % 2:
            # Implement the optimal first turn strategy
            move = self._optimal_first_turn_strategy(board, turn)
        else:
            # Implement the best response strategy
            move = self._optimal_response_strategy(board, turn)

        return move

    def _optimal_first_turn_strategy(self, board, turn):
        assert not turn % 2, f"turn {turn} is not a first turn strategy"
        if turn == 0:
            # select a corner at random
            return self.prng.choice(board.available_corners())
        elif turn == 2:
            if board[4] != "4":
                # other player picked center, go opposite corner
                return self.find_opposite_corner(board)
            else:
                # pick adjacent corner
                return self.find_adjacent_corner(board)
        elif turn == 4:
            # was blocked and player did not take middle
            return 4
        else:
            # game is a tie
            return self.prng.choice(board.available())

    def _optimal_response_strategy(self, board, turn):
        assert turn % 2, f"turn {turn} is not a response strategy"
        if turn == 1:
            if board[4] == "4":  # take the center if it's open
                return 4
            else:
                return self.prng.choice(board.available_corners())
        elif turn == 3:
            opponent_move_1, opponent_move_2 = (
                board.moves[0].space,
                board.moves[2].space,
            )
            if (
                opponent_move_1 in patterns.corners
                and opponent_move_2 in patterns.corners
            ):
                return self.prng.choice(board.available_middles())

        return self.prng.choice(board.available())
