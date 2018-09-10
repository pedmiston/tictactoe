import random
import pytest
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
    assert computer1.eval(board) == computer2.eval(board)


def test_hard_computer_chooses_corner_as_first_move(hard_computer):
    board = Board()
    move = hard_computer.eval(board)
    assert move in board.corners


@pytest.mark.skip
def test_hard_computer_chooses_adjacent_corner_as_second_move(hard_computer):
    board = Board()
    board[0] = "X"
    board[1] = "O"
    move = hard_computer.eval(board)
    assert move == "6"

    board = Board()
    board[0] = "X"
    board[3] = "O"
    move = hard_computer.eval(board)
    assert move == "2"


def test_hard_computer_wins_if_able(hard_computer):
    for args in Board.winning_patterns:
        args = list(args)
        random.shuffle(args)
        a, b, c = args
        board = Board()
        board[a] = "X"
        board[b] = "X"
        move = hard_computer.eval(board)
        assert move == c


def test_hard_computer_blocks_if_cant_win(hard_computer):
    for args in Board.winning_patterns:
        args = list(args)
        random.shuffle(args)
        a, b, c = args
        board = Board()
        board[a] = "O"
        board[b] = "O"
        move = hard_computer.eval(board)
        assert move == c
