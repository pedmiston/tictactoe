from unittest.mock import Mock
import pytest
import game
from game import Game, Board, KeyNotOnBoardError, SpotAlreadySelectedError, SpotTakenByOpponentError


@pytest.fixture
def stdscr():
    _curses = game.curses
    game.curses = Mock()
    stdscr = Mock()
    stdscr.getyx = Mock(return_value=(0,0))
    yield stdscr
    game.curses = _curses


def test_quit_game(stdscr):
    game = Game()
    stdscr.getkey = Mock(return_value="q")
    game(stdscr)



@pytest.fixture
def board():
    return Board()


def test_board_handles_bad_user_input(board):
    for bad_key in ["9", "q"]:
        with pytest.raises(KeyNotOnBoardError):
            board[bad_key]

def test_board_prevents_picking_same_spot_twice(board):
    board[0] = "X"
    with pytest.raises(SpotAlreadySelectedError):
        board[0] = "X"

def test_board_prevents_picking_same_spot_as_opponent(board):
    board[0] = "X"
    with pytest.raises(SpotTakenByOpponentError):
        board[0] = "O"
