from unittest.mock import Mock
import pytest

from tictactoe import board, players, screens


@pytest.fixture
def xo_board():
    return board.Board(tokens=["X", "O"])


@pytest.fixture
def x_computer():
    computer = players.Computer()
    computer.token = "X"
    return computer


@pytest.fixture
def stdscr():
    """A mock of a curses window."""
    stdscr = Mock()
    stdscr.getyx.return_value = (0, 0)

    # mock the curses module
    _curses = screens.curses
    screens.curses = Mock()

    # mock the way curses colors implement the bitwise-OR operator "|="
    screens.curses.color_pair.return_value = _curses.A_NORMAL
    screens.curses.A_STANDOUT = _curses.A_NORMAL

    yield stdscr

    # teardown
    screens.curses = _curses
