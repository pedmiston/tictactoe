import sys
import curses
import random
import time
import string
import logging

logger = logging.getLogger("game")


class Game:
    def __init__(self, log_file="game.log"):
        """Initialize the game with the option to write to a log file.

        Args:
            log_file: Name of log file. If log_file is None, no log is written"""
        if log_file is not None:
            handler = logging.FileHandler(log_file, mode="w")
            handler.setLevel(logging.INFO)
            logger.addHandler(handler)
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
        logger.info("welcome the player and ask for game type")
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
            raise TicTacToeError(f"unknown game type for key '{key}': {game_type}")

        # Set default player tokens
        player1.token = "X"
        player2.token = "O"

        # Modify player settings
        logger.info("editing player settings")
        settings_screen = SettingsScreen(stdscr, player1, player2)
        settings_screen.draw()
        while True:
            try:
                settings_screen.edit_player1()
                settings_screen.edit_player2()
            except PlayerQuitException:
                logger.info("player quit the game")
                return
            else:
                break

        # Set player order
        order_screen = OrderScreen(stdscr, player1, player2)
        order_screen.draw()
        try:
            player1, player2 = order_screen.get_player_order()
        except PlayerQuitException:
            logger.info("player quit the game")
            return
        else:
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
    """A Screen is a curses application window.

    TicTacToe screens (e.g. WelcomeScreen) inherit from this parent class.
    """
    prompt_y = 0  # number of rows from the top of the screens
                  # where to put the prompt text

    def __init__(self, stdscr):
        """Initialize the screen as a wrapper around a curses window."""
        self.s = stdscr

    def get_key(self, prompt=None, keys=None, yx=None, default=None):
        """Get a key press from the user.

        Args:
            prompt: The text describing the accepted key presses.
            keys: A list of keys to accept. If None, accept any key.
            yx: A tuple of (y, x) screen coordinates of where to echo the key press.
            default: A key to use as default. If a default key is provided and
                ENTER is pressed, the default key will be returned.

        Returns:
            key: A string of the key pressed by the user.
        """
        if prompt:
            self.s.addstr(self.prompt_y, 0, prompt)
        yx = yx or self.s.getyx()
        if default is not None:
            self.s.addstr(yx[0], yx[1], default)
        while True:
            key = self.s.getkey(*yx)
            # The enter key is "\n" when using getkey() or the constant curses.KEY_ENTER when using getch()
            if key == "\n" and default is not None:
                key = default
                break
            elif keys is None or key in keys:
                break
        return key


class WelcomeScreen(Screen):
    """The WelcomeScreen welcomes the player and ask for game type."""

    game_types = {
        "1": "Human v Computer",
        "2": "Human v Human",
        "3": "Computer v Computer",
    }

    def draw(self):
        self.s.clear()
        self.s.addstr(0, 0, "Let's play Tic Tac Toe!")
        self.s.addstr(2, 0, "Which type of game would you like to play?")
        for i, game_type in self.game_types.items():
            row = 2 + int(i)
            self.s.addstr(row, 0, f"({i}) {game_type}")
        self.s.refresh()

        # set prompt_y 2 lines below current window cursor
        self.prompt_y = self.s.getyx()[0] + 2

    def get_game_type(self):
        choices = ["1", "2", "3", "q"]
        prompt = "Enter [1-3] or Q to quit: "
        curses.echo()
        key = self.get_key(prompt=prompt,
                           keys=choices,
                           default=choices[0])
        curses.noecho()
        if key == "q":
            raise PlayerQuitException()
        elif key not in self.game_types:
            raise TicTacToeError(f"unknown key '{key}' not in game types: {self.game_types}")
        else:
            return self.game_types[key]


class SettingsScreen(Screen):
    """A SettingsScreen has a main win and two subwins for player1 and player2."""

    def __init__(self, stdscr, player1, player2):
        start_y = 2
        nlines = 2
        buffer = 1
        ncols = 80

        self.prompt_y = start_y + ((buffer + nlines) * 2)
        self.error_y = self.prompt_y + 1

        def make_player_settings_window(player, start_y):
            """Make a HumanSettingsWindow or a ComputerSettingsWindow."""
            window = stdscr.subwin(nlines, ncols, start_y, 0)
            if isinstance(player, Human):
                player_settings_window = HumanSettingsWindow(
                    window, player
                )
            elif isinstance(player, Computer):
                player_settings_window = ComputerSettingsWindow(
                    window, player
                )
            else:
                raise TicTacToeError(f"unknown player type '{type(player)}'")
            return player_settings_window


        self.wplayer1 = make_player_settings_window(
            player1, start_y=start_y
        )
        self.wplayer2 = make_player_settings_window(
            player2, start_y=start_y + nlines + buffer
        )

        super().__init__(stdscr)


    def draw(self):
        self.s.clear()
        self.s.addstr(0, 0, "Edit player settings")
        self.wplayer1.draw()
        self.wplayer2.draw()
        self.s.refresh()

    def edit_player1(self):
        while True:
            try:
                self.wplayer1.get_settings()
            except ImproperTokenError:
                self.s.addstr(self.error_y, 0, "You can't use that as a token.")
            else:
                break

            self.s.refresh()

        logger.info(f"{self.wplayer1.player} selected token '{self.wplayer1.player.token}'")

    def edit_player2(self):
        while True:
            try:
                self.wplayer2.get_settings(opponent_token=self.wplayer1.player.token)
            except ImproperTokenError:
                self.s.addstr(self.error_y, 0, "You can't use that as a token.")
            except DuplicateTokenError:
                self.s.addstr(
                    self.error_y, 0, "You must use a different token from player 1."
                )
            else:
                break

            self.s.refresh()

        logger.info(f"{self.wplayer2.player} selected token '{self.wplayer2.player.token}'")


class HumanSettingsWindow(Screen):
    token_yx = (0, 0)

    def __init__(self, stdscr, player):
        self.player = player
        super().__init__(stdscr)

    def draw(self):
        self.s.addstr(0, 0, f"{self.player} token: ")
        self.token_yx = self.s.getyx()
        self.s.addstr(self.player.token)

    def get_settings(self, opponent_token=None):
        self.get_token(opponent_token=opponent_token)

    def get_token(self, opponent_token=None):
        key = self.get_key(yx=self.token_yx)
        if key == "q":
            raise PlayerQuitException()
        elif opponent_token is not None and key.upper() == opponent_token:
            raise DuplicateTokenError()

        self.player.token = key  # may raise ImproperTokenError

        self.s.addstr(self.token_yx[0], self.token_yx[1], self.player.token)
        self.s.refresh()

class ComputerSettingsWindow(Screen):
    difficulties = {"1": "Easy", "2": "Medium", "3": "Hard"}

    def __init__(self, stdscr, player):
        self.player = player
        super().__init__(stdscr)

    def draw(self):
        self.s.addstr(0, 0, f"{self.player} token: ")
        self.token_yx = self.s.getyx()
        self.s.addstr(self.player.token)
        self.s.addstr(1, 0, "Difficulty: ")
        self.s.addstr("Easy", curses.A_BOLD)
        self.s.addstr(" | Medium | Hard")
        self.s.refresh()

    def get_settings(self, opponent_token=None):
        self.get_token(opponent_token=opponent_token)
        self.get_difficulty()

    def get_token(self, opponent_token=None):
        key = self.get_key(yx=self.token_yx)
        if key == "q":
            raise PlayerQuitException()
        elif opponent_token is not None and key.upper() == opponent_token:
            raise DuplicateTokenError()

        self.player.token = key  # may raise ImproperTokenError

        self.s.addstr(self.token_yx[0], self.token_yx[1], self.player.token)
        self.s.refresh()

    def get_difficulty(self):
        keys = ["1", "2", "3", "q"]
        key = self.get_key(keys=keys)
        self.player.difficulty = self.difficulties[key]


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

        self.prompt_y = 6

    def get_player_order(self):
        prompt = "Enter [1-3] or Q to quit: "
        keys = ["1", "2", "3", "q"]
        key = self.get_key(prompt=prompt, keys=keys, default=keys[0])
        if key == "q":
            raise PlayerQuitException()
        elif key == "1":
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
        token = token.upper()
        if token not in string.ascii_uppercase:
            raise ImproperTokenError()
        self._token = token


class Human(Player):
    label = "Human"


class Computer(Player):
    label = "Computer"

    def eval(self, board):
        return self._difficulty_func(board)

    @property
    def difficulty(self):
        return self._difficulty_label

    @difficulty.setter
    def difficulty(self, token):
        self._difficulty_label = token
        self._difficulty_func = getattr(self, f"difficulty_func_{token.lower()}")
        self.label = f"{self.label} ({self._difficulty_label})"

    def difficulty_func_easy(self, board):
        available_spaces = board.get_available_spaces()
        return random.choice(available_spaces)

    def difficulty_func_medium(self, board):
        raise NotImplementedError()

    def difficulty_func_hard(self, board):
        raise NotImplementedError()


class TicTacToeError(Exception):
    pass


class PlayerQuitException(TicTacToeError):
    pass


class RepeatSettingsException(TicTacToeError):
    pass


class KeyNotOnBoardError(TicTacToeError):
    pass


class SpotAlreadySelectedError(TicTacToeError):
    pass


class SpotTakenByOpponentError(TicTacToeError):
    pass


class ImproperTokenError(TicTacToeError):
    pass


class DuplicateTokenError(TicTacToeError):
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
