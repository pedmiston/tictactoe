import sys
import curses
import random
import time
import string
import logging
import logging.config


logging.config.dictConfig(
    {
        "version": 1,
        "disable_existing_loggers": True,
        "handlers": {
            "game.log": {
                "level": "INFO",
                "class": "logging.FileHandler",
                "filename": "game.log",
                "mode": "w",
            }
        },
        "loggers": {"game": {"handlers": ["game.log"], "level": "NOTSET"}},
    }
)
logger = logging.getLogger("game")


class Game:
    def __init__(self, keep_game_log=False, log_file=None):
        if log_file:
            handler = logging.FileHandler(log_file)
            handler.setLevel(logging.INFO)
            logger.removeHandler(logger.handlers[0])
            logger.addHandler(handler)

        if keep_game_log or log_file:
            logger.setLevel(logging.INFO)

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
        # Draw welcome screen and ask for game type
        welcome_screen = WelcomeScreen(stdscr)
        welcome_screen.draw()
        try:
            game_type = welcome_screen.get_game_type()
        except PlayerQuitException:
            logger.info("player quit the game")
            return
        else:
            logger.info(f"player selected {game_type}")

        # Create players 1 and 2 based on game type
        if game_type == "Human v Computer":
            player1, player2 = Human(), Computer()
        elif game_type == "Human v Human":
            player1, player2 = Human("Player1"), Human("Player2")
        elif game_type == "Computer v Computer":
            player1, player2 = Computer("Computer1"), Computer("Computer2")
        else:
            raise TicTacToeError(f"unknown game type '({key}) {game_type}'")

        player1.token = 'x'
        player2.token = 'o'

        # Modify player settings
        settings_screen = SettingsScreen(stdscr, player1, player2)
        settings_screen.draw()
        settings_screen.edit_player1()
        settings_screen.edit_player2()

        # Set player order
        order_screen = OrderScreen(stdscr, player1, player2)
        order_screen.draw()
        player1, player2 = order_screen.get_player_order()
        logger.info(f"{player1} is going first")

        # Play the game until it's over or a player quits
        board = Board(tokens=[player1.token, player2.token])
        play_screen = PlayScreen(stdscr, board)
        try:
            while not board.is_over() and not board.is_tie():
                play_screen.show_player_move(player1)
                if not board.is_over() and not board.is_tie():
                    play_screen.show_player_move(player2)
        except PlayerQuitException:
            logger.info("player quit the game")
        else:
            logger.info("game over")


class Screen:
    """A Screen is a curses application window."""
    def __init__(self, stdscr):
        self.s = stdscr

    def get_key(self, keys=None, yx=None, default=None):
        """Get a key press from the user.

        Args:
            keys: A list of keys to accept. If None, accept any key.
            yx: A tuple of (y, x) screen coordinates to echo the key press.
            default: A key to use as default. If ENTER is pressed, the default
                will be used.
        """
        curses.echo()
        yx = yx or self.s.getyx()
        if default is not None:
            self.s.addstr(yx[0], yx[1], default)
        while True:
            key = self.s.getkey(*yx)
            if key == "\n" and default is not None:
                key = default
                break
            elif keys is None or key in keys:
                break
        curses.noecho()
        return key


class WelcomeScreen(Screen):
    """The WelcomeScreen welcomes the player and ask for game type."""
    game_types = {"1": "Human v Computer", "2": "Human v Human", "3": "Computer v Computer"}

    def draw(self):
        self.s.clear()
        self.s.addstr(0, 0, "Let's play Tic Tac Toe!")
        self.s.addstr(2, 0, "Which type of game would you like to play?")
        for i, game_type in self.game_types.items():
            row = 2 + int(i)
            self.s.addstr(row, 0, f"({i}) {game_type}")
        self.s.refresh()

    def get_game_type(self):
        choices = ["1", "2", "3", "q"]
        self.s.addstr(7, 0, "Enter [1-3] or Q to quit: ")
        key = self.get_key(choices, default=choices[0])
        if key == "q":
            raise PlayerQuitException()
        return self.game_types[key]


class SettingsScreen(Screen):
    def __init__(self, stdscr, player1, player2):
        start_y = 1
        nlines = 1
        ncols = 40
        self.player1, self.player2 = player1, player2
        self.player1_window = PlayerSettingsWindow(stdscr.subwin(nlines, ncols, start_y, 0), player1)
        self.player2_window = PlayerSettingsWindow(stdscr.subwin(nlines, ncols, start_y+nlines, 0), player2)
        super().__init__(stdscr)

    def draw(self):
        self.s.clear()
        self.s.addstr(0, 0, "Edit player settings")
        self.player1_window.draw()
        self.player2_window.draw()
        self.s.refresh()

    def edit_player1(self):
        while True:
            try:
                self.player1_window.get_token()
            except ImproperTokenError:
                self.s.addstr(5, 0, "You can't use that as a token.")
            else:
                break

        logger.info(f"{self.player1} selected token '{self.player1.token}'")

    def edit_player2(self):
        while True:
            try:
                self.player2_window.get_token(opponent_token=self.player1.token)
            except ImproperTokenError:
                self.s.addstr(5, 0, "You can't use that as a token.")
            except DuplicateTokenError:
                self.s.addstr(
                    5, 0, "You must use a different token from player 1."
                )
            else:
                break

        logger.info(f"{self.player2} selected token '{self.player2.token}'")


class PlayerSettingsWindow(Screen):
    def __init__(self, stdscr, player):
        self.player = player
        super().__init__(stdscr)

    def draw(self):
        self.s.addstr(0, 0, f"{self.player} token: ")
        self.token_yx = self.s.getyx()
        self.s.addstr(self.player.token)

    def get_token(self, opponent_token=None):
        key = self.get_key(yx=self.token_yx)
        if opponent_token is not None and key.upper() == opponent_token:
            raise DuplicateTokenError()

        self.player.token = key
        self.s.addstr(
            self.token_yx[0], self.token_yx[1], self.player.token
        )


class OrderScreen(Screen):
    """The OrderScreen asks which player will go first."""
    player1, player2 = None, None
    def __init__(self, stdscr, player1, player2):
        self.player1 = player1
        self.player2 = player2
        super().__init__(stdscr)

    def draw(self):
        self.s.clear()
        self.s.addstr(0, 0, "Who goes first?")
        self.s.addstr(2, 0, f"(1) {self.player1}")
        self.s.addstr(3, 0, f"(2) {self.player2}")
        self.s.addstr(4, 0, f"(3) Flip a coin")
        self.s.refresh()

    def get_player_order(self):
        choices = ["1", "2", "3"]
        self.s.addstr(6, 0, "Enter [1-3]: ")
        key = self.get_key(["1", "2", "3"], default=choices[0])
        if key == "1":
            pass
        elif key == "2" or (key == "3" and random.random() >= 0.5):
            self.player1, self.player2 = self.player2, self.player1
        else:
            raise TicTacToeError()

        return self.player1, self.player2


class PlayScreen(Screen):
    """A PlayScreen is for playing Tic Tac Toe."""
    def __init__(self, stdscr, board):
        self.board = board
        super().__init__(stdscr)

    def show_player_move(self, player):
        if isinstance(player, Human):
            self.show_human_move(player)
        elif isinstance(player, Computer):
            self.show_computer_move(player)
        else:
            # smells!
            raise TicTacToeException()

    def show_human_move(self, human_player):
        self.s.clear()
        self.s.refresh()
        self.s.addstr(0, 0, str(self.board))
        self.s.addstr(6, 0, "Enter [1-9] or Q to quit: ")
        input_yx = self.s.getyx()
        error_message_y = self.s.getyx()[0] + 1
        while True:
            key = self.get_key(yx=input_yx)
            if key == "q":
                raise PlayerQuitException()
            try:
                self.board[key] = human_player.token
            except KeyNotOnBoardError:
                error_message = "That key was not one of your options."
            except SpotAlreadySelectedError:
                error_message = "You've already placed a token in that square!"
            except SpotTakenByOpponentError:
                error_message = "Your opponent has already claimed that square."
            else:
                logger.info(f"{human_player} placed a token on {key}")
                break
            self.s.addstr(error_message_y, 0, error_message)

    def show_computer_move(self, computer_player):
        """Animate the Computer's move."""
        self.s.clear()
        self.s.refresh()
        self.s.addstr(0, 0, str(self.board))
        self.s.addstr(6, 0, f"{computer_player}'s turn...")
        move = computer_player.eval(self.board)
        self.board[move] = computer_player.token
        logger.info(f"{computer_player} placed a token on {move}")
        self.s.refresh()
        time.sleep(1)
        self.s.addstr(0, 0, str(self.board))


class Board:
    def __init__(self, tokens=None):
        self.tokens = tokens or ["X", "O"]
        self._board = ["0", "1", "2", "3", "4", "5", "6", "7", "8"]

    def __str__(self):
        return (
            " %s | %s | %s \n===+===+===\n %s | %s | %s \n===+===+===\n %s | %s | %s \n"
            % (
                self._board[0],
                self._board[1],
                self._board[2],
                self._board[3],
                self._board[4],
                self._board[5],
                self._board[6],
                self._board[7],
                self._board[8],
            )
        )

    def __getitem__(self, key):
        """Returns the token at a particular square."""
        try:
            token = self._board[int(key)]
        except (ValueError, IndexError):
            raise KeyNotOnBoardError()
        else:
            return token

    def __setitem__(self, key, value):
        """Places a token on the board.

        >>> board[4] = "X"  # attempts to place "X" in square 4
        """
        prev = self[key]
        if prev == value:
            raise SpotAlreadySelectedError()
        elif prev in self.tokens:
            raise SpotTakenByOpponentError()
        self._board[int(key)] = value

    def three_in_a_row(self, *args):
        return (
            args[0] == args[1] == args[2] == self.tokens[0]
            or args[0] == args[1] == args[2] == self.tokens[1]
        )

    def is_over(self):
        b = self._board
        return (
            self.three_in_a_row(b[0], b[1], b[2]) == 1
            or self.three_in_a_row(b[3], b[4], b[5]) == 1
            or self.three_in_a_row(b[6], b[7], b[8]) == 1
            or self.three_in_a_row(b[0], b[3], b[6]) == 1
            or self.three_in_a_row(b[1], b[4], b[7]) == 1
            or self.three_in_a_row(b[2], b[5], b[8]) == 1
            or self.three_in_a_row(b[0], b[4], b[8]) == 1
            or self.three_in_a_row(b[2], b[4], b[6]) == 1
        )

    def is_tie(self):
        return len([s for s in self._board if s in self.tokens]) == 9

    def get_available_spaces(self):
        return [s for s in self._board if s not in self.tokens]


class Player:
    label = None
    _token = None

    def __init__(self, label=None):
        if label is not None:
            self.label = label

    def __str__(self):
        return self.label

    @property
    def token(self):
        return self._token

    @token.setter
    def token(self, token):
        if token not in string.ascii_lowercase:
            raise ImproperTokenError()
        self._token = token.upper()


class Human(Player):
    label = "Human"


class Computer(Player):
    label = "Computer"

    def eval(self, board):
        available_spaces = board.get_available_spaces()
        return random.choice(available_spaces)


class TicTacToeError(Exception):
    pass


class PlayerQuitException(TicTacToeError):
    pass


class KeyNotOnBoardError(TicTacToeError):
    pass


class SpotAlreadySelectedError(TicTacToeError):
    pass


class SpotTakenByOpponentError(TicTacToeError):
    pass


class ImproperTokenError(TicTacToeError):
    pass


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--logging", action="store_true", help="write game log")
    args = parser.parse_args()
    if args.logging:
        logger.setLevel(logging.DEBUG)

    game = Game()
    curses.wrapper(game)
