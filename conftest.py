import pytest

from tictactoe import board, players


@pytest.fixture
def xo_board():
    return board.Board(tokens=["X", "O"])


@pytest.fixture
def x_computer():
    computer = players.Computer()
    computer.token = "X"
    return computer