import random
import pytest
from tictactoe import ai
from tictactoe.players import Computer
from tictactoe.board import Board


@pytest.fixture
def hard_computer():
    hard_computer = Computer(difficulty="Hard", seed=243)
    hard_computer.token = "X"
    return hard_computer


def test_computer_makes_repeatable_guesses():
    computer1 = Computer(difficulty="Easy", seed=100)
    computer2 = Computer(difficulty="Easy", seed=100)
    board = Board()
    assert computer1.move(board) == computer2.move(board)


def test_hard_computer_chooses_corner_as_first_move(hard_computer):
    board = Board()
    move = hard_computer.move(board)
    assert move in board.corners


def test_hard_computer_chooses_adjacent_corner_as_second_move(hard_computer):
    board = Board()
    board[0] = "X"
    board[1] = "O"
    move = hard_computer.move(board)
    assert move == 6

    board = Board()
    board[0] = "X"
    board[3] = "O"
    move = hard_computer.move(board)
    assert move == 2


def test_hard_computer_chooses_opposite_corner_as_second_move(hard_computer):
    board = Board()
    board[0] = "X"
    board[4] = "O"
    assert hard_computer.move(board) == 8


def test_hard_computer_wins_if_able(hard_computer):
    for args in Board.winning_patterns:
        args = list(args)
        random.shuffle(args)
        a, b, c = args
        board = Board()
        board[a] = "X"
        board[b] = "X"
        move = hard_computer.move(board)
        assert move == c


def test_hard_computer_blocks_if_cant_win(hard_computer):
    for args in Board.winning_patterns:
        args = list(args)
        random.shuffle(args)
        a, b, c = args
        board = Board()
        board[a] = "O"
        board[b] = "O"
        move = hard_computer.move(board)
        assert move == c


@pytest.mark.parametrize("seed", range(10))
def test_hard_computer_response_strategy_picks_mid_spot_turn_three(seed):
    hard_computer = Computer(difficulty="Hard", seed=seed)
    hard_computer.token = "X"

    board = Board()
    board[2] = "O"
    board[4] = "X"
    board[6] = "O"

    move = hard_computer.move(board)
    assert move in board.middles
