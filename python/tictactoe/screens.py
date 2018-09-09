import time
import random
import itertools
import logging

from .app import curses
from .models import Human, Computer, Board
from . import exceptions

logger = logging.getLogger("game")


class Screen:
    """Parent class for all TicTacToe screens."""

    prompt_y, error_y = 1, 2  # subclasses should overwrite these
    choice_delay = 0.28

    def __init__(self, stdscr):
        """Initialize the screen as a wrapper around a curses window."""
        self.s = stdscr

    def draw_title(self, title):
        self.s.addstr(0, 0, title)

    def draw_description(self, description):
        self.s.addstr(1, 0, description)

    def get_key(self, prompt=None, keys=None, yx=None, default=None, highlight=False):
        """Get a key press from the user.

        Args:
            prompt: The text describing the accepted key presses.
            keys: A list of keys to accept. If keys is None, accept any key.
            yx: A tuple of (y, x) screen coordinates of where to echo the key press.
            default: A key to use as default. If a default key is provided and
                ENTER is pressed, the default key will be returned.
            highlight: Whether to highlight the cell at the yx position.

        Returns:
            key: A string of the key pressed by the user.
        """
        if prompt:
            self.draw_prompt(prompt)
        yx = yx or self.s.getyx()
        if default is not None:
            self.s.addstr(yx[0], yx[1], default)
        if highlight:
            self.s.chgat(yx[0], yx[1], 1, curses.A_STANDOUT)
        self.s.refresh()
        while True:
            key = self.s.getkey()
            # The enter key is "\n" when using getkey() or the constant curses.KEY_ENTER when using getch()
            if key == "\n" and default is not None:
                key = default
                break
            elif keys is None or key in keys:
                break

        self.s.addstr(yx[0], yx[1], key, curses.A_STANDOUT)
        return key

    def draw_choices(self, choices, highlight=None, start_y=None):
        """Draw response choices.

        Args:
            choices: dict of keys and labels.
            highlight: key to highlight as default. Optional.
            start_y: row to start drawing choices. If start_y is None,
                one row below the current cursor position is used.
        """
        if start_y is None:
            start_y = self.s.getyx()[0] + 1

        for i, (key, label) in enumerate(choices.items()):
            row = start_y + i
            self.s.addstr(row, 0, f"({key}) {label}")
            if key == highlight:
                self.s.chgat(row, 0, 3, curses.A_STANDOUT)

    def draw_prompt(self, msg):
        self.s.move(self.prompt_y, 0)
        self.s.deleteln()
        self.s.insertln()
        self.s.addstr(msg)

    def draw_error_message(self, msg=None):
        self.s.move(self.error_y, 0)
        self.s.deleteln()
        self.s.insertln()
        if msg is None:
            return
        error_attrs = curses.color_pair(1)
        error_attrs |= curses.A_STANDOUT
        self.s.addstr(f"!", error_attrs)
        self.s.addstr(f" {msg}", curses.color_pair(1))


class WelcomeScreen(Screen):
    """The WelcomeScreen welcomes the player and asks for game type."""

    game_types = {
        "1": "Human v Computer",
        "2": "Human v Human",
        "3": "Computer v Computer",
    }

    def draw(self):
        self.s.clear()
        self.draw_title("Let's play Tic Tac Toe!")
        self.draw_description("Which type of game would you like to play?")
        self.draw_choices(self.game_types, highlight="1", start_y=3)
        self.s.refresh()

        # set prompt 2 lines below choices
        self.prompt_y = self.s.getyx()[0] + 2

    def get_game_type(self):
        choices = ["1", "2", "3", "q"]
        prompt = "Enter [1-3] or Q to quit: "
        key = self.get_key(
            prompt=prompt, keys=choices, default=choices[0], highlight=True
        )
        if key == "q":
            raise exceptions.PlayerQuitException()
        elif key not in self.game_types:
            raise exceptions.TicTacToeError(
                f"unknown key '{key}' not in game types: {self.game_types}"
            )

        # highlight selected game type
        self.draw_choices(self.game_types, highlight=key, start_y=3)
        self.s.refresh()
        time.sleep(self.choice_delay)

        return self.game_types[key]


class TokenScreen(Screen):
    """The TokenScreen allows players to pick their tokens."""

    def __init__(self, stdscr, player1, player2):
        super().__init__(stdscr)
        self.player1, self.player2 = player1, player2

    def draw(self):
        self.s.clear()
        self.draw_title("Pick your tokens!")

        self.s.addstr(2, 0, f"{self.player1}: ")
        self.player1_token_yx = self.s.getyx()
        self.s.addstr(self.player1.token)

        self.s.addstr(3, 0, f"{self.player2}: ")
        self.player2_token_yx = self.s.getyx()
        self.s.addstr(self.player2.token)

        self.s.refresh()

        self.prompt_y = self.s.getyx()[0] + 2
        self.error_y = self.prompt_y + 1

    def update_player_tokens(self):
        log_fmt = "{player} selected token {player.token}"
        self.update_player_token(self.player1, self.player1_token_yx)
        self.draw_error_message(msg=None)
        logger.info(log_fmt.format(player=self.player1))
        self.update_player_token(
            self.player2, self.player2_token_yx, opponent_token=self.player1.token
        )
        logger.info(log_fmt.format(player=self.player2))

    def update_player_token(self, player, token_yx, opponent_token=None):
        while True:
            prompt = f"Enter a letter [A-Z] to use as a token."
            key = self.get_key(
                prompt=prompt, yx=token_yx, default=player.token, highlight=True
            )
            if opponent_token is not None and key.upper() == opponent_token:
                self.draw_error_message(
                    "You must use a different token than the other player."
                )
                continue

            try:
                player.token = key
            except ImproperTokenError:
                self.draw_error_message("You can't use that as a token.")
            else:
                # "echo" the capitalized token to the screen
                self.s.addstr(token_yx[0], token_yx[1], player.token)
                break

        self.draw_error_message(msg=None)  # clear error message


class DifficultyScreen(Screen):
    """The DifficultyScreen asks the player to set the computer difficulties."""

    difficulties = {"1": "Easy", "2": "Medium", "3": "Hard"}

    def __init__(self, stdscr, player1, player2):
        """Initialize a screen for setting computer player difficulties."""
        super().__init__(stdscr)
        self.player1, self.player2 = player1, player2
        # Set flag to skip if neither player is a Computer
        self.skip = not (
            isinstance(self.player1, Computer) or isinstance(self.player2, Computer)
        )

    def draw(self):
        self.s.clear()
        self.draw_title("Select difficulty")
        self.draw_choices(self.difficulties, highlight="1", start_y=2)
        self.s.refresh()

        # set prompt 2 lines below choices
        self.prompt_y = self.s.getyx()[0] + 2

    def update_computer_difficulties(self):
        if isinstance(self.player1, Computer):
            self.get_difficulty(self.player1)

        self.draw_choices(self.difficulties, highlight="1", start_y=2)
        if isinstance(self.player2, Computer):
            self.get_difficulty(self.player2)

    def get_difficulty(self, player):
        self.draw_description(f"Set a difficulty for {player}")
        keys = ["1", "2", "3"]
        prompt = f"Enter [1-3]: "
        key = self.get_key(prompt=prompt, keys=keys, default=keys[0], highlight=True)

        self.draw_choices(self.difficulties, highlight=key, start_y=2)
        self.s.refresh()
        time.sleep(self.choice_delay)

        player.difficulty = self.difficulties[key]
        logger.info(f"Set difficulty of {player} to {player.difficulty}")


class OrderScreen(Screen):
    """The OrderScreen asks which player will go first."""

    choices = {"1": "{player1}", "2": "{player2}", "3": "Flip a coin"}
    player1, player2 = None, None

    def __init__(self, stdscr, player1, player2):
        super().__init__(stdscr)
        self.player1 = player1
        self.player2 = player2

        # Update choice text to reflect player names
        self.choices["1"] = self.choices["1"].format(player1=self.player1)
        self.choices["2"] = self.choices["2"].format(player2=self.player2)

    def draw(self):
        self.s.clear()
        self.draw_title("Who goes first?")
        self.draw_choices(self.choices, highlight="1", start_y=2)
        self.s.refresh()
        self.prompt_y = self.s.getyx()[0] + 2

    def get_player_order(self):
        prompt = "Enter [1-3] or Q to quit: "
        keys = ["1", "2", "3", "q"]
        key = self.get_key(prompt=prompt, keys=keys, default=keys[0], highlight=True)
        if key == "q":
            raise exceptions.PlayerQuitException()
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

        self.draw_choices(self.choices, highlight=key, start_y=2)
        self.s.refresh()
        time.sleep(self.choice_delay)

        return self.player1, self.player2


class PlayScreen(Screen):
    """The PlayScreen is for playing TicTacToe."""

    def __init__(self, stdscr, player1, player2):
        super().__init__(stdscr)
        self.player1, self.player2 = player1, player2
        self.board = Board(tokens=[player1.token, player2.token])

        # Create a window for drawing the board
        nlines = 6
        ncols = 12
        start_y, start_x = 2, 3
        window = self.s.subwin(nlines, ncols, start_y, start_x)
        self.board_window = BoardWindow(window, self.board)

        # Set prompt below board
        self.prompt_y = start_y + nlines
        self.error_y = self.prompt_y + 1

    def play(self):
        winning_player = None
        while not self.board.is_over() and not self.board.is_tie():
            self.move_player(self.player1)
            if self.board.is_over():
                # player1 wins
                winning_player = self.player1
                break
            if not self.board.is_over() and not self.board.is_tie():
                self.move_player(self.player2)
                if self.board.is_over():
                    # player2 wins
                    winning_player = self.player2
                    break

        self.board_window.draw()
        self.s.move(self.prompt_y, 0)
        self.s.deleteln()
        self.s.insertln()
        if winning_player is None:
            self.s.addstr("The game ended in a tie.")
            logger.info("Game ended in a tie")
        else:
            ixs = self.board.find_three_in_a_row()
            self.board_window.highlight_three_in_a_row(*ixs)
            self.board_window.w.refresh()
            self.s.addstr(f"{winning_player} wins!", curses.A_STANDOUT)
            logger.info(f"{winning_player} wins")

        self.prompt_y += 1
        prompt = "Press any key to quit the game."
        self.get_key(prompt=prompt)

    def move_player(self, player):
        self.s.clear()
        self.s.addstr(0, 0, f"{player}'s turn")
        self.board_window.draw()
        if isinstance(player, Human):
            move = self.get_human_move(player)
        elif isinstance(player, Computer):
            move = self.show_computer_move(player)
        else:
            # smells!
            raise TicTacToeException()

        self.board_window.highlight_square(move)
        self.board_window.w.refresh()
        time.sleep(self.choice_delay * 2)

    def get_human_move(self, human_player):
        prompt = "Enter [0-9] or Q to quit: "
        keys = list(map(str, range(10))) + ["q"]
        while True:
            key = self.get_key(prompt=prompt, keys=keys)
            if key == "q":
                raise exceptions.PlayerQuitException()
            try:
                self.board[key] = human_player.token
            except SpotAlreadySelectedError:
                error_message = "You've already placed a token on that square!"
            except SpotTakenByOpponentError:
                error_message = "Your opponent has already claimed that square."
            else:
                logger.info(f"{human_player} placed a token on {key}")
                break
            # If the loop wasn't broken, there was an error
            self.draw_error_message(error_message)

        return int(key)

    def show_computer_move(self, computer_player):
        """Animate the Computer's move."""
        self.draw_prompt(f"{computer_player}'s turn...")
        self.s.refresh()
        move = computer_player.eval(self.board)
        self.board[move] = computer_player.token
        logger.info(f"{computer_player} placed a token on {move}")
        self.s.refresh()
        time.sleep(self.choice_delay * 2)
        self.board_window.draw()
        return int(move)


class BoardWindow:
    def __init__(self, window, board):
        self.w = window
        self.board = board

        rows_with_tokens = [0, 2, 4]
        cols_with_tokens = [1, 5, 9]
        self.token_yxs = list(itertools.product(rows_with_tokens, cols_with_tokens))

    def draw(self):
        v, h, p = "|", "=", "+"
        self.w.clear()
        self.w.addstr(
            0,
            0,
            " {0} {v} {1} {v} {2} ".format(
                self.board[0], self.board[1], self.board[2], v=v
            ),
        )
        self.w.addstr(1, 0, f"{h}{h}{h}{p}{h}{h}{h}{p}{h}{h}{h}")
        self.w.addstr(
            2,
            0,
            " {0} {v} {1} {v} {2} ".format(
                self.board[3], self.board[4], self.board[5], v=v
            ),
        )
        self.w.addstr(3, 0, f"{h}{h}{h}{p}{h}{h}{h}{p}{h}{h}{h}")
        self.w.addstr(
            4,
            0,
            " {0} {v} {1} {v} {2} ".format(
                self.board[6], self.board[7], self.board[8], v=v
            ),
        )
        self.w.refresh()

    def highlight_square(self, i):
        y, x = self.token_yxs[i]
        self.w.chgat(y, x, 1, curses.A_STANDOUT)

    def highlight_three_in_a_row(self, *ixs):
        for i in ixs:
            y, x = self.token_yxs[i]
            self.w.chgat(y, x, 1, curses.A_STANDOUT)
