import sys
import curses
import random
import time
import string
import logging

logger = logging.getLogger("game")


class Game:
    def __init__(self, log_file="game.log"):
        """Initialize the game with the option to write to a custom log file.

        Args:
            log_file: Name of log file. If log_file is None, no log is written.
        """
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
        if curses.has_colors():
            curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)

        # Welcome the player and ask for game type
        logger.info("Starting a new game")
        welcome_screen = WelcomeScreen(stdscr)
        welcome_screen.draw()
        try:
            game_type = welcome_screen.get_game_type()
        except PlayerQuitException:
            return self.quit()
        logger.info(f"Setting up a {game_type} game")

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
        logger.info("Editing player settings")
        settings_screen = SettingsScreen(stdscr, player1, player2)
        settings_screen.draw()

        # Edit player 1 settings
        settings_screen.get_player1_token()
        logger.info(f"Set token for {player1} to {player1.token}.")
        if isinstance(player1, Computer):
            settings_screen.get_player1_difficulty()
            logger.info(f"Set difficulty of {player1} to {player1.difficulty}.")

        # Edit player 2 settings
        settings_screen.get_player2_token()
        logger.info(f"Set token for {player2} to {player2.token}.")
        if isinstance(player2, Computer):
            settings_screen.get_player2_difficulty()
            logger.info(f"Set difficulty of {player2} to {player2.difficulty}.")

        # Set player order
        order_screen = OrderScreen(stdscr, player1, player2)
        order_screen.draw()
        try:
            player1, player2 = order_screen.get_player_order()
        except PlayerQuitException:
            return self.quit()
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
            return self.quit()
        else:
            logger.info("game over")

    def quit(self):
        logger.info("Player quit the game")



class Screen:
    """A Screen is a curses application window.

    TicTacToe screens (e.g. WelcomeScreen) inherit from this parent class.
    """
    prompt_y = 0

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
        self.draw_game_type(highlight="1")
        self.s.refresh()

        # set prompt_y 2 lines below current window cursor
        self.prompt_y = self.s.getyx()[0] + 2

    def draw_game_type(self, highlight):
        for i, game_type in self.game_types.items():
            row = 2 + int(i)
            if i == highlight:
                self.s.addstr(row, 0, f"({i}) {game_type}", curses.A_STANDOUT)
            else:
                self.s.addstr(row, 0, f"({i}) {game_type}", curses.A_DIM)

    def get_game_type(self):
        choices = ["1", "2", "3", "q"]
        prompt = "Enter [1-3] or Q to quit: "
        curses.echo()
        key = self.get_key(prompt=prompt, keys=choices, default=choices[0])
        curses.noecho()
        if key == "q":
            raise PlayerQuitException()
        elif key not in self.game_types:
            raise TicTacToeError(
                f"unknown key '{key}' not in game types: {self.game_types}"
            )
        else:
            # highlight selected game type
            self.draw_game_type(highlight=key)
            self.s.refresh()
            time.sleep(0.5)
            return self.game_types[key]


class SettingsScreen(Screen):
    """A SettingsScreen has a main screen and two windows for player1 and player2."""
    nlines = 5  # size of window
    ncols = 40  #
    window1_start_y = 1
    window2_start_y = window1_start_y + nlines
    prompt_y = window2_start_y + nlines
    error_y = prompt_y + 1

    def __init__(self, stdscr, player1, player2):
        super().__init__(stdscr)
        self.window1 = self.make_player_settings_window(
            player1, start_y=self.window1_start_y
        )
        self.window2 = self.make_player_settings_window(
            player2, start_y=self.window2_start_y
        )

    def make_player_settings_window(self, player, start_y):
        """Make a HumanSettingsWindow or a ComputerSettingsWindow."""
        window = self.s.subwin(self.nlines, self.ncols, start_y, 0)
        if isinstance(player, Human):
            player_settings_window = HumanSettingsWindow(window, player)
        elif isinstance(player, Computer):
            player_settings_window = ComputerSettingsWindow(window, player)
        else:
            raise TicTacToeError(f"unknown player class '{type(player)}'")
        return player_settings_window

    def draw(self):
        self.s.clear()
        self.s.addstr(0, 0, "Edit player settings")
        self.window1.draw()
        self.window2.draw()
        self.s.refresh()

    def get_player1_token(self):
        self.get_player_token(self.window1)

    def get_player2_token(self):
        self.get_player_token(self.window2, opponent_token=self.window1.player.token)

    def get_player_token(self, window, opponent_token=None):
        prompt = f"Enter a letter [A-Z] to use as a token."
        self.draw_prompt(prompt)
        while True:
            error_msg = ""
            try:
                window.get_token(opponent_token=opponent_token)
            except ImproperTokenError:
                error_msg = "You can't use that as a token."
            except DuplicateTokenError:
                error_msg = "You must use a different token than the other player."
            else:
                break
            self.draw_error_message(error_msg)
        self.s.touchline(self.prompt_y, 2)
        self.s.refresh()

    def get_player1_difficulty(self):
        self.get_player_difficulty(self.window1)

    def get_player2_difficulty(self):
        self.get_player_difficulty(self.window2)

    def get_player_difficulty(self, window):
        if not isinstance(window.player, Computer):
            raise TicTacToeError(f"can only set difficulty for computer players, not players of type {type(window.player)}")
        self.draw_prompt("Enter [1=Easy 2=Medium 3=Hard] to set the difficulty.")
        window.get_difficulty()
        self.s.touchline(self.prompt_y, 2)
        self.s.refresh()

    def draw_prompt(self, msg):
        self.s.addstr(self.prompt_y, 0, msg)
        self.s.refresh()

    def draw_error_message(self, msg):
        self.s.touchline(self.error_y, 1)
        self.s.addstr(self.error_y, 0, msg, curses.color_pair(1))
        self.s.refresh()

class PlayerSettingsWindow(Screen):
    """Base class for HumanSettingsWindow and ComputerSettingsWindow."""

    token_yx = (0, 0)

    def __init__(self, window, player):
        self.player = player
        super().__init__(window)

    def draw(self):
        self.s.box()
        self.s.addstr(1, 1, f"{self.player}", curses.A_BOLD)
        self.s.addstr(2, 1, "Token: ")
        self.token_yx = self.s.getyx()
        self.s.addstr(self.player.token)
        self.s.refresh()

    def get_token(self, opponent_token=None):
        key = self.get_key(yx=self.token_yx, default=self.player.token)
        if opponent_token is not None and key.upper() == opponent_token:
            raise DuplicateTokenError()

        self.player.token = key  # may raise ImproperTokenError

        # "echo" the capitalized token to the screen
        self.s.addstr(self.token_yx[0], self.token_yx[1], self.player.token)
        self.s.refresh()


class HumanSettingsWindow(PlayerSettingsWindow):
    pass


class ComputerSettingsWindow(PlayerSettingsWindow):
    difficulties = {"1": "Easy", "2": "Medium", "3": "Hard"}

    def draw(self):
        self.s.box()
        self.s.addstr(1, 1, f"{self.player} settings:")
        self.s.addstr(2, 1, "Token: ")
        self.token_yx = self.s.getyx()
        self.s.addstr(self.player.token)
        self.draw_difficulty(highlight="1")
        self.s.refresh()

    def get_difficulty(self):
        keys = ["1", "2", "3"]
        key = self.get_key(keys=keys)
        self.draw_difficulty(highlight=key)
        self.s.refresh()
        time.sleep(0.5)
        self.player.difficulty = self.difficulties[key]

    def draw_difficulty(self, highlight):
        self.s.addstr(3, 1, "Difficulty: ")
        keys = sorted(self.difficulties.keys())
        for key in keys:
            if key == highlight:
                attr = curses.A_STANDOUT
            else:
                attr = curses.A_DIM
            self.s.addstr(self.difficulties[key], attr)
            if key != keys[-1]:
                self.s.addstr(" | ")


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
        self.s.addstr(2, 0, f"(1) {self.player1}", curses.A_STANDOUT)
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
        elif key == "1":  # player1 goes first
            pass
        elif key == "2":  # player2 goes first
            self.player1, self.player2 = self.player2, self.player1
        elif key == "3":
            # Flip a coin
            if random.random() >= 0.5:  # player2 goes first
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
