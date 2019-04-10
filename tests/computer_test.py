import random
import pytest
from tictactoe import patterns, players
from tictactoe.board import Board


def test_computer_finds_winning_move(xo_board, x_computer):
    xo_board[0] = "X"
    xo_board[1] = "X"

    assert x_computer.find_winning_move(xo_board) == 2


def test_computer_fails_to_find_incomplete_pattern(xo_board, x_computer):
    xo_board[0] = "X"
    xo_board[5] = "X"

    assert x_computer.find_winning_move(xo_board) == -1


def test_computer_fails_to_find_occupied_winning_move(xo_board, x_computer):
    xo_board[0] = "X"
    xo_board[1] = "X"
    xo_board[2] = "O"

    assert x_computer.find_winning_move(xo_board) == -1


def test_computer_finds_blocking_move(xo_board, x_computer):
    xo_board[0] = "O"
    xo_board[1] = "O"

    assert x_computer.find_blocking_move(xo_board) == 2


def test_computer_finds_adjacent_corner(xo_board, x_computer):
    xo_board[0] = "X"
    assert x_computer.find_adjacent_corner(xo_board) == 2


def test_computer_fails_to_find_adjacent_corner_if_blocked(xo_board, x_computer):
    xo_board[0] = "X"
    xo_board[1] = "O"
    xo_board[3] = "O"
    assert x_computer.find_adjacent_corner(xo_board) == -1


def test_computer_finds_opposite_corner(xo_board, x_computer):
    xo_board[0] = "X"
    assert x_computer.find_opposite_corner(xo_board) == 8


@pytest.fixture
def hard_computer():
    hard_computer = players.HardComputer(seed=243)
    hard_computer.token = "X"
    return hard_computer


def test_computer_makes_repeatable_guesses():
    computer1 = players.EasyComputer(seed=100)
    computer2 = players.EasyComputer(seed=100)
    board = Board()
    assert computer1.move(board) == computer2.move(board)


def test_hard_computer_chooses_corner_as_first_move(hard_computer):
    board = Board()
    move = hard_computer.move(board)
    assert move in patterns.corners


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
    for args in patterns.winning_patterns:
        args = list(args)
        random.shuffle(args)
        a, b, c = args
        board = Board()
        board[a] = "X"
        board[b] = "X"
        move = hard_computer.move(board)
        assert move == c


def test_hard_computer_blocks_if_cant_win(hard_computer):
    for args in patterns.winning_patterns:
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
    hard_computer = players.HardComputer(seed=seed)
    hard_computer.token = "X"

    board = Board()
    board[2] = "O"
    board[4] = "X"
    board[6] = "O"

    move = hard_computer.move(board)
    assert move in patterns.middles
