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
    """Mock a curses terminal application."""
    _curses = game.curses
    game.curses = Mock()
    stdscr = Mock()
    stdscr.getyx = Mock(return_value=(0, 0))
    yield stdscr
    game.curses = _curses


def test_quit_game(stdscr, tmpdir):
    tmp_game_log = tmpdir.mkdir('game').join('game.log')
    game = Game(log_file=str(tmp_game_log))
    stdscr.getkey = Mock(return_value="q")
    game(stdscr)
    assert "player quit the game" in tmp_game_log.read()


def test_play_human_v_human_game(stdscr):
    game = Game()
    stdscr.getkey.side_effect = [
        "2",  # Human v Human game type
        "x",  # Human1 token
        "o",  # Human2 token
        "1",  # Human1 goes first
        "0",  # Human1 turn
        "3",  # Human2 turn
        "1",  # Human1 turn
        "4",  # Human2 turn
        "2",  # Human1 wins
    ]
    game(stdscr)
    assert game.board.is_over()


def test_switch_order(stdscr, tmpdir):
    tmp_game_log = tmpdir.mkdir('game').join('game.log')
    game = Game(log_file=str(tmp_game_log))
    stdscr.getkey.side_effect = [
        "2",  # Human v Human game type
        "x",  # Player1 token
        "o",  # Player2 token
        "2",  # Player2 goes first
        "4",  # Player2 places token
        "q",  # quit
    ]
    game(stdscr)
    assert "Player2 is going first" in tmp_game_log.read()
    assert game.board[4] == "O"


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
