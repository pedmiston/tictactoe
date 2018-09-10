import sys

import itertools
import logging

# curses is in the python standard library, but it may not be available
# on Windows because it depends on the GNU program ncurses.
import curses


from . import screens
from . import exceptions
from .board import Board
from .players import Human, Computer


logger = logging.getLogger("game")


class Game:
    def __init__(self, log_file=None):
        """Initialize a game with the option to write to a custom log file.

        Args:
            log_file: Name of log file. If log_file is None, no log is written.
        """
        if log_file:
            enable_logging(log_file)

    def __call__(self, stdscr):
        """Run the game as a terminal application in a curses window.

        This is the main event loop for the game.

        Args:
            stdscr: A curses window

        Example:
            >>> import curses
            >>> game = Game()
            >>> curses.wrapper(game)
        """
        configure_curses()

        # Welcome the player and ask for game type
        logger.info("Starting a new game")
        welcome_screen = screens.WelcomeScreen(stdscr)
        welcome_screen.draw()
        try:
            game_type = welcome_screen.get_game_type()
        except exceptions.PlayerQuitException:
            return self.quit()

        logger.info(f"Setting up a {game_type} game")
        player1, player2 = create_players_from_game_type(game_type)

        # Set player tokens
        token_screen = screens.TokenScreen(stdscr, player1, player2)
        token_screen.draw()
        token_screen.update_player_tokens()

        # Set computer player difficulties
        difficulty_screen = screens.DifficultyScreen(stdscr, player1, player2)
        if (
            not difficulty_screen.skip
        ):  # skip difficulty screen if neither player is a computer
            difficulty_screen.draw()
            difficulty_screen.update_computer_difficulties()

        # Set player order
        order_screen = screens.OrderScreen(stdscr, player1, player2)
        order_screen.draw()
        try:
            player1, player2 = order_screen.get_player_order()
        except exceptions.PlayerQuitException:
            return self.quit()
        logger.info(f"{player1} is going first")

        # Play the game until it's over or a player quits
        play_screen = screens.PlayScreen(stdscr, player1, player2)
        try:
            play_screen.play()
        except exceptions.PlayerQuitException:
            return self.quit()

        logger.info("Game over")

    def quit(self):
        logger.info("Player quit the game")


def enable_logging(log_file):
    handler = logging.FileHandler(log_file, mode="w")
    handler.setLevel(logging.INFO)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


def configure_curses():
    if curses.has_colors():
        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.curs_set(0)  # make cursor invisible


def create_players_from_game_type(game_type):
    # Create players 1 and 2 based on game type
    if game_type == "Human v Computer":
        player1, player2 = Human(), Computer()
    elif game_type == "Human v Human":
        player1, player2 = Human("Player 1"), Human("Player 2")
    elif game_type == "Computer v Computer":
        player1, player2 = Computer("Computer 1"), Computer("Computer 2")
    else:
        raise TicTacToeError(f"unknown game type for key '{key}': {game_type}")

    # Set default player tokens
    player1.token = "X"
    player2.token = "O"

    return player1, player2
