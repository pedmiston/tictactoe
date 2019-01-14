import sys
import itertools
import logging
from tictactoe import players, screens, exceptions
from tictactoe.board import Board


logger = logging.getLogger("game")


class Game:
    def __init__(self, log_file=None):
        """Initialize a game with the option to write to a log file.

        Args:
            log_file: Name of log file. If None, no log file is written.
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
        logger.info("Starting a new game")
        screens.configure_curses()

        # Welcome the player and ask for game type
        welcome_screen = screens.WelcomeScreen(stdscr)
        welcome_screen.draw()
        try:
            game_type = welcome_screen.get_game_type()
        except exceptions.PlayerQuitException:
            return self.quit()

        logger.info(f"Setting up a {game_type} game")
        player1, player2 = create_players_from_game_type(game_type)

        # Set player colors
        player1.color_ix = 2
        player2.color_ix = 3

        # Set player tokens
        player1.token = "X"
        player2.token = "O"

        token_screen = screens.TokenScreen(stdscr, player1, player2)
        token_screen.draw()
        token_screen.update_player_tokens()

        if game_has_computer_players(game_type):
            # Set computer player difficulties
            difficulty_screen = screens.DifficultyScreen(stdscr, player1, player2)
            difficulty_screen.draw()
            try:
                difficulty_screen.update_computer_difficulties()
            except exceptions.PlayerQuitException:
                return self.quit()

        # Set player order
        order_screen = screens.OrderScreen(stdscr, player1, player2)
        order_screen.draw()
        try:
            player1, player2 = order_screen.reorder_players()
        except exceptions.PlayerQuitException:
            return self.quit()
        logger.info(f"{player1} is going first")

        # Play the game until it's over or a player quits
        board = Board(tokens=[player1.token, player2.token])
        play_screen = screens.PlayScreen(stdscr, board, player1, player2)
        try:
            play_screen.play()
        except exceptions.PlayerQuitException:
            return self.quit()

        # Ask the player if they want to play again
        end_screen = screens.EndScreen(
            stdscr, board, board_window=play_screen.board_window
        )
        play_again = end_screen.ask_play_again()
        if play_again:
            self(stdscr)  # ???
        else:
            logger.info("Game over")

    def quit(self):
        logger.info("Player quit the game")


def enable_logging(log_file):
    """Configure the module logger to write to a file."""
    handler = logging.FileHandler(log_file, mode="w")
    handler.setLevel(logging.INFO)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


# TODO: Refactor game_type to be an enum type


def create_players_from_game_type(game_type):
    """Create players 1 and 2 based on game type."""
    if game_type == "Human v Computer":
        player1, player2 = players.Human(), players.Computer()
    elif game_type == "Human v Human":
        player1, player2 = players.Human("Player 1"), players.Human("Player 2")
    elif game_type == "Computer v Computer":
        player1, player2 = (
            players.Computer("Computer 1"),
            players.Computer("Computer 2"),
        )
    else:
        raise TicTacToeError(f"unknown game type '{game_type}'")

    return player1, player2


def game_has_computer_players(game_type):
    return game_type != "Human v Human"
