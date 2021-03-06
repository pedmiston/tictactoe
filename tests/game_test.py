"""Functional tests of people playing the game."""
from unittest.mock import Mock
import pytest

from tictactoe import app, screens, players, exceptions
from tictactoe.screens import Screen


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


@pytest.fixture
def logging_game(tmpdir):
    """A game that logs to a pytest tmpfile."""
    tmp_log = tmpdir.mkdir("game").join("game.log")

    g = app.Game(log_file=str(tmp_log))
    Screen.choice_delay = 0  # fast mode

    # patch on a method for reading the log
    def read_log():
        return tmp_log.read()

    g.read_log = read_log

    return g


def test_quit_game(stdscr, logging_game):
    stdscr.getkey.return_value = "q"
    logging_game(stdscr)
    assert "Player quit the game" in logging_game.read_log()


def test_play_human_v_human_game(stdscr, logging_game):
    stdscr.getkey.side_effect = [
        "2",  # Human v Human game type
        "x",  # Player 1 token
        "o",  # Player 2 token
        "1",  # Player 1 goes first
        "0",  # Player 1 turn
        "3",  # Player 2 turn
        "1",  # Player 1 turn
        "4",  # Player 2 turn
        "2",  # Player 1 turn
        "\n",  # Player 1 wins screen
        "q",  # Any key to quit
    ]
    logging_game(stdscr)
    assert "Player 1 wins" in logging_game.read_log()
    assert "Game over" in logging_game.read_log()


def test_play_tie_game(stdscr, logging_game):
    stdscr.getkey.side_effect = [
        "2",  # Human v Human game type
        "x",  # Player 1 token
        "o",  # Player 2 token
        "1",  # Player 1 goes first
        "0",  # Player 1 turn
        "1",  # Player 2 turn
        "2",  # Player 1 turn
        "4",  # Player 2 turn
        "3",  # Player 1 turn
        "5",  # Player 2 turn
        "7",  # Player 1 turn
        "6",  # Player 2 turn
        "8",  # Player 1 turn
        "\n",  # Tie screen
        "q",  # Any key to quit
    ]
    logging_game(stdscr)
    assert "Game ended in a tie" in logging_game.read_log()
    assert "Game over" in logging_game.read_log()


def test_set_computer_difficulty(stdscr, logging_game):
    stdscr.getkey.side_effect = [
        "3",  # Computer v Computer game type
        "x",  # Computer 1 token
        "o",  # Computer 2 token
        "1",  # Computer 1 difficulty
        "2",  # Computer 2 difficulty
        "q",  # Quit at the order screen
    ]
    logging_game(stdscr)
    assert "Set difficulty of Computer 1 to Easy" in logging_game.read_log()
    assert "Set difficulty of Computer 2 to Medium" in logging_game.read_log()


def test_switch_order(stdscr, logging_game):
    stdscr.getkey.side_effect = [
        "2",  # Human v Human game type
        "x",  # Player1 token
        "o",  # Player2 token
        "2",  # Player2 goes first
        "4",  # Player2 places token
        "q",  # quit
    ]
    logging_game(stdscr)
    assert "Player 2 is going first" in logging_game.read_log()


@pytest.mark.parametrize("seed1,seed2", zip(range(1, 10), range(11, 20)))
def test_hard_ai_always_ties(stdscr, logging_game, seed1, seed2):
    app.create_players_from_game_type = Mock()
    app.create_players_from_game_type.return_value = (
        players.HardComputer("Computer 1", seed=seed1),
        players.HardComputer("Computer 2", seed=seed2),
    )

    stdscr.getkey.side_effect = [
        "3",  # Computer v Computer game type
        "x",  # Computer 1 token
        "o",  # Computer 2 token
        "3",  # Computer 1 difficulty: hard
        "3",  # Computer 2 difficulty: hard
        "1",  # Computer 1 goes first
        # Play the game
        "\n",  # Tie screen
        "q",  # Any key to quit
    ]
    logging_game(stdscr)
    assert "Game ended in a tie" in logging_game.read_log()
