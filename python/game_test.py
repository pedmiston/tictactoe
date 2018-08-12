from unittest.mock import Mock
import pytest
import game
from game import (
    Game,
    Board,
    Player,
    KeyNotOnBoardError,
    SpotAlreadySelectedError,
    SpotTakenByOpponentError,
    ImproperTokenError,
)


# Functional tests: Simulate playing the game ----


@pytest.fixture
def stdscr():
    _curses = game.curses
    game.curses = Mock()
    stdscr = Mock()
    stdscr.getyx = Mock(return_value=(0, 0))
    yield stdscr
    game.curses = _curses


def test_quit_game(stdscr):
    game = Game()
    stdscr.getkey = Mock(return_value="q")
    game(stdscr)


def test_play_human_v_human_game(stdscr):
    game = Game()
    stdscr.getkey.side_effect = [
        "2",  # Select (2) Human v Human
        "x",  # Select X for Human1 token
        "o",  # Select O for Human2 token
        "0",  # Human1 turn
        "3",  # Human2 turn
        "1",  # Human1 turn
        "4",  # Human2 turn
        "2",  # Human1 wins
    ]
    game(stdscr)
    assert game.board.is_over()


# Board tests ----


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


# Player tests ----


def test_player_cannot_set_improper_token():
    player = Player()
    for improper_token in ["[", "1"]:
        with pytest.raises(ImproperTokenError):
            player.token = improper_token
