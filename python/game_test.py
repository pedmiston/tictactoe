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
    DuplicateTokenError,
    HumanSettingsWindow,
)


# Functional tests: Simulate playing the game ----


@pytest.fixture
def stdscr():
    """A mock of a curses window."""
    stdscr = Mock()
    stdscr.getyx.return_value = (0, 0)
    stdscr.subwin().getyx.return_value = (0, 0)

    # mock the curses module and put it back when done
    _curses = game.curses
    game.curses = Mock()
    yield stdscr
    game.curses = _curses


@pytest.fixture
def logging_game(tmpdir):
    """A game that logs to a pytest tmpfile."""
    tmp_log = tmpdir.mkdir("game").join("game.log")
    game = Game(log_file=str(tmp_log))

    def read_log():
        return tmp_log.read()

    game.read_log = read_log

    return game


def test_quit_game(stdscr, logging_game):
    stdscr.getkey = Mock(return_value="q")
    logging_game(stdscr)
    assert "player quit the game" in logging_game.read_log()


def test_play_human_v_human_game(stdscr, logging_game):
    stdscr.getkey.side_effect = [
        "2",  # Human v Human game type
        # Human1 token
        # Human2 token
        "1",  # Human1 goes first
        "0",  # Human1 turn
        "3",  # Human2 turn
        "1",  # Human1 turn
        "4",  # Human2 turn
        "2",  # Human1 wins
    ]
    stdscr.subwin().getkey.side_effect = ["x", "o"]  # Human1 token  # Human2 token
    logging_game(stdscr)
    assert "game over" in logging_game.read_log()


def test_switch_order(stdscr, logging_game):
    stdscr.getkey.side_effect = [
        "2",  # Human v Human game type
        # Player1 token
        # Player2 token
        "2",  # Player2 goes first
        "4",  # Player2 places token
        "q",  # quit
    ]
    stdscr.subwin().getkey.side_effect = ["x", "o"]  # Player1 token  # Player2 token
    logging_game(stdscr)
    assert "Player2 is going first" in logging_game.read_log()


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


def test_player_tokens_get_capitalized():
    player = Player()
    player.token = "x"
    assert player.token == "X"


def test_player_tokens_can_be_capitalized():
    player = Player()
    player.token = "X"
    assert player.token == "X"


def test_player2_cannot_set_duplicate_token(stdscr):
    token = "X"
    player = Player()
    stdscr.getkey.return_value = token
    player_window = HumanSettingsWindow(stdscr, player)
    with pytest.raises(DuplicateTokenError):
        player_window.get_token(opponent_token=token)
