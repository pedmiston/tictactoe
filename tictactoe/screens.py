import enum
import time
import random
import itertools
import logging
import curses
from tictactoe import board, players, exceptions


logger = logging.getLogger("game")


class GameType(enum.Enum):
    HUMAN_V_COMPUTER = 1
    HUMAN_V_HUMAN = 2
    COMPUTER_V_COMPUTER = 3


class CursesWindow:
    """A wrapper around a curses window application."""

    CHOICE_DELAY = 0.5

    def __init__(self, stdscr):
        self.stdscr = stdscr

    def addstr(self, *args, **kwargs):
        self.stdscr.addstr(*args, **kwargs)
        self.stdscr.clrtoeol()

    def getyx(self):
        return self.stdscr.getyx()

    def chgat(self, *args, **kwargs):
        self.stdscr.chgat(*args, **kwargs)

    def refresh(self):
        self.stdscr.refresh()

    def getkey(self):
        return self.stdscr.getkey()

    def move(self, y, x):
        self.stdscr.move(y, x)

    def clearln(self):
        self.stdscr.deleteln()
        self.stdscr.insertln()

    def clear(self):
        self.stdscr.clear()

    def subwin(self, nlines, ncols, start_y, start_x):
        return self.stdscr.subwin(nlines, ncols, start_y, start_x)

    def draw_choices(
        self,
        choices,
        highlight_key=None,
        highlight_line=None,
        start_y=None,
        choice_colors=None,
    ):
        """Draw response choices.

        Args:
            choices: dict of keyboard keys to response labels.
            highlight_key: keyboard key of choice to highlight as the default key. Optional.
            highlight_line: keyboard key of line to highlight, e.g., after it has been selected. Optional.
            start_y: row to start drawing response choices. If not provided,
                one row below the current cursor position is used.
            choice_colors: dict of choice keys to curses color pair indices. Optional.
        """
        if start_y is None:
            start_y = self.getyx()[0] + 1

        for i, (key, label) in enumerate(choices.items()):
            row = start_y + i

            # TODO: Refactor this!
            if choice_colors and key in choice_colors:
                self.addstr(row, 0, f"({key}) ")
                self.addstr(f"{label}", curses.color_pair(choice_colors[key]))
            else:
                self.addstr(row, 0, f"({key}) {label}")

            if key == highlight_key:
                if choice_colors and key in choice_colors:
                    self.chgat(
                        row,
                        0,
                        3,
                        curses.color_pair(choice_colors[key]) | curses.A_STANDOUT,
                    )
                else:
                    self.chgat(row, 0, 3, curses.A_STANDOUT)

            if key == highlight_line:
                len_of_choice_prefix = 4
                end_x = len_of_choice_prefix + len(choices[key])
                if choice_colors and key in choice_colors:
                    self.chgat(
                        row,
                        0,
                        end_x,
                        curses.color_pair(choice_colors[key]) | curses.A_STANDOUT,
                    )
                else:
                    self.chgat(row, 0, end_x, curses.A_STANDOUT)
        
        self.refresh()

    def get_response(
        self, keys=None, yx=None, default=None, highlight=False, highlight_color_ix=None
    ):
        """Ask for a key press from the user.

        Args:
            keys: A list of keys to accept. If keys is None, accept any key.
            yx: A tuple of (y, x) screen coordinates of where to echo the key press.
                If not provided, the current cursor position is used.
            default: A key to use as default. If a default key is provided and
                ENTER is pressed, the default key will be returned.
            highlight: Whether to highlight the cell at the yx position.
            highlight_color_ix: Whether to highlight the key in a curses color pair. Optional.

        Returns:
            key: A string of the key pressed by the user.
        """
        yx = yx or self.getyx()
        if default is not None:
            self.addstr(yx[0], yx[1], default)

        if highlight:
            # TODO: Refactor
            if highlight_color_ix:
                self.chgat(
                    yx[0],
                    yx[1],
                    1,
                    curses.color_pair(highlight_color_ix) | curses.A_STANDOUT,
                )
            else:
                self.chgat(yx[0], yx[1], 1, curses.A_STANDOUT)

        while True:
            # The enter key is "\n" when using getkey()
            # or the constant curses.KEY_ENTER when using getch()
            key = self.getkey()
            if key == "\n" and default is not None:
                key = default
                break
            elif keys is None or key in keys:
                break

        self.addstr(yx[0], yx[1], key, curses.A_STANDOUT)
        return key

    def get_game_type(self):
        """Returns the game type from a key press."""
        game_type_labels = {
            str(GameType.HUMAN_V_COMPUTER.value): "Human v Computer",
            str(GameType.HUMAN_V_HUMAN.value): "Human v Human",
            str(GameType.COMPUTER_V_COMPUTER.value): "Computer v Computer",
        }

        self.clear()
        self.addstr(0, 0, "Let's play Tic Tac Toe!")
        self.addstr(1, 0, "Which type of game would you like to play?")
        self.draw_choices(game_type_labels, highlight_key="1", start_y=3)

        prompt_y = self.getyx()[0] + 2
        self.addstr(prompt_y, 0, "Enter [1-3] or Q to quit: ")
        response_yx = self.getyx()

        self.addstr(
            prompt_y + 1,
            0,
            "Press ENTER to accept the highlighted choice.",
            curses.color_pair(3),
        )

        choices = [str(i) for i in game_type_labels] + ["q"]
        key = self.get_response(
            keys=choices, yx=response_yx, default=choices[0], highlight=True
        )
        if key == "q":
            raise exceptions.PlayerQuitException()

        self.draw_choices(game_type_labels, highlight_line=key, start_y=3)
        time.sleep(self.CHOICE_DELAY)

        return GameType(int(key))


class Screen:
    """Parent class for all TicTacToe screens."""


    def draw_error_message(self, msg, error_y):
        self.move(error_y, 0)
        c = (
            curses.color_pair(1) | curses.A_STANDOUT
        )  # combine color with standout effects with bitwise "or"
        self.addstr(f"!", c)
        self.addstr(f" {msg}", curses.color_pair(1))

class TokenScreen(Screen):
    """The TokenScreen allows players to pick their tokens."""

    def __init__(self, window, player1, player2):
        super().__init__(window)
        self.player1, self.player2 = player1, player2

    def draw(self):
        self.window.clear()
        self.draw_title("Pick your tokens!")

        self.window.addstr(
            2, 0, f"{self.player1}: ", curses.color_pair(self.player1.color_ix)
        )
        self.player1_token_yx = self.window.getyx()
        self.window.addstr(
            self.player1_token_yx[0],
            self.player1_token_yx[1],
            self.player1.token,
            curses.color_pair(self.player1.color_ix),
        )

        self.window.addstr(
            3, 0, f"{self.player2}: ", curses.color_pair(self.player2.color_ix)
        )
        self.player2_token_yx = self.window.getyx()
        self.window.addstr(
            self.player2_token_yx[0],
            self.player2_token_yx[1],
            self.player2.token,
            curses.color_pair(self.player2.color_ix),
        )

        self.window.refresh()

        self.prompt_y = self.window.getyx()[0] + 2
        self.error_y = self.prompt_y + 1

    def update_player_tokens(self):
        log_fmt = "{player} selected token {player.token}"

        # Update Player 1 token
        self.update_player_token(self.player1, self.player1_token_yx)
        logger.info(log_fmt.format(player=self.player1))

        # Update Player 2 token
        self.update_player_token(
            self.player2, self.player2_token_yx, opponent_token=self.player1.token
        )
        logger.info(log_fmt.format(player=self.player2))

    def update_player_token(self, player, token_yx, opponent_token=None):
        while True:
            prompt = f"Enter a letter [A-Z] to use as a token."
            key = self.get_key(
                prompt=prompt,
                yx=token_yx,
                default=player.token,
                highlight=True,
                highlight_color_ix=player.color_ix,
            )
            if opponent_token is not None and key.upper() == opponent_token:
                self.draw_error_message(
                    "You must use a different token than the other player."
                )
                continue

            try:
                player.token = key
            except exceptions.ImproperTokenError:
                self.draw_error_message("You can't use that as a token.")
            else:
                # "echo" the capitalized token to the screen
                self.window.addstr(
                    token_yx[0],
                    token_yx[1],
                    player.token,
                    curses.color_pair(player.color_ix),
                )
                break

        self.draw_error_message(msg=None)  # clear error message


class DifficultyScreen(Screen):
    """The DifficultyScreen asks the player to set the computer difficulties."""

    difficulties = {"1": "Easy", "2": "Medium", "3": "Hard"}

    def __init__(self, window, player1, player2):
        super().__init__(window)
        self.player1, self.player2 = player1, player2
        # Set flag to skip if neither player is a Computer
        self.skip = not (
            isinstance(self.player1, players.Computer)
            or isinstance(self.player2, players.Computer)
        )

    def draw(self):
        self.window.clear()
        self.draw_choices(self.difficulties, highlight_key="1", start_y=2)
        self.window.refresh()

        # set prompt 2 lines below choices
        self.prompt_y = self.window.getyx()[0] + 2

    def update_computer_difficulties(self):
        if isinstance(self.player1, players.Computer):
            self.get_difficulty(self.player1)

        self.draw_choices(self.difficulties, highlight_key="1", start_y=2)
        if isinstance(self.player2, players.Computer):
            self.get_difficulty(self.player2)

    def get_difficulty(self, player):
        self.draw_title(f"Set a difficulty for ")
        y, x = self.window.getyx()
        self.window.addstr(y, x, str(player), curses.color_pair(player.color_ix))

        keys = ["1", "2", "3"]
        prompt = f"Enter [1-3]: "
        key = self.get_key(prompt=prompt, keys=keys, default=keys[0], highlight=True)

        self.draw_choices(self.difficulties, highlight_line=key, start_y=2)
        self.window.refresh()
        time.sleep(self.choice_delay)

        difficulty = self.difficulties[key]
        if difficulty == "Easy":
            player = players.EasyComputer(player.label)
        elif difficulty == "Medium":
            player = players.MediumComputer(player.label)
        elif difficulty == "Hard":
            player = players.HardComputer(player.label)
        else:
            raise TicTacToeError()

        logger.info(f"Set difficulty of {player} to {player.difficulty}")


class OrderScreen(Screen):
    """The OrderScreen asks which player will go first."""

    choices = {"1": "{player1}", "2": "{player2}", "3": "Flip a coin"}
    player1, player2 = None, None

    def __init__(self, window, player1, player2):
        super().__init__(window)
        self.player1 = player1
        self.player2 = player2

        # Update choice text to reflect player names
        self.choices["1"] = self.choices["1"].format(player1=self.player1)
        self.choices["2"] = self.choices["2"].format(player2=self.player2)

        self.choice_colors = {"1": self.player1.color_ix, "2": self.player2.color_ix}

    def draw(self):
        self.window.clear()
        self.draw_title("Who goes first?")
        self.draw_choices(
            self.choices, highlight_key="1", start_y=2, choice_colors=self.choice_colors
        )
        self.window.refresh()
        self.prompt_y = self.window.getyx()[0] + 2

    def reorder_players(self):
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

        self.draw_choices(
            self.choices,
            highlight_line=key,
            start_y=2,
            choice_colors=self.choice_colors,
        )
        self.window.refresh()
        time.sleep(self.choice_delay)

        return self.player1, self.player2


class PlayScreen(Screen):
    """The PlayScreen is for playing TicTacToe."""

    def __init__(self, window, board, player1, player2):
        super().__init__(window)
        self.player1, self.player2 = player1, player2
        self.board = board
        self.board_window = BoardWindow.from_window(window, self.board)

        # Set prompt below board
        self.prompt_y = 8
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
        self.window.move(self.prompt_y, 0)
        self.window.clearln()
        if winning_player is None:
            self.window.addstr("The game ended in a tie.")
            logger.info("Game ended in a tie")
        else:
            self.board_window.highlight_winning_pattern()
            self.board_window.w.refresh()
            self.window.addstr(
                f"{winning_player} wins!",
                curses.color_pair(winning_player.color_ix) | curses.A_STANDOUT,
            )
            logger.info(f"{winning_player} wins")

        self.prompt_y += 1
        prompt = "Press any key."
        self.get_key(prompt=prompt)

    def move_player(self, player):
        self.window.clear()
        self.window.addstr(0, 0, f"{player}'s turn", curses.color_pair(player.color_ix))
        self.board_window.draw()
        if isinstance(player, players.Human):
            move = self.get_human_move(player)
        elif isinstance(player, players.Computer):
            move = self.show_computer_move(player)
        else:
            # smells!
            raise TicTacToeException()

        self.board_window.highlight_square(move, player_color_ix=player.color_ix)
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
            except exceptions.SpotAlreadySelectedError:
                error_message = "You've already placed a token on that square!"
            except exceptions.SpotTakenByOpponentError:
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
        self.window.refresh()
        move = computer_player.move(self.board)
        self.board[move] = computer_player.token
        logger.info(f"{computer_player} placed a token on {move}")
        self.window.refresh()
        time.sleep(self.choice_delay * 2)
        self.board_window.draw()
        return int(move)


class EndScreen(Screen):
    def __init__(self, stdscr, board, board_window):
        super().__init__(stdscr)
        self.board_window = board_window

        # Set prompt below board
        self.prompt_y = 8

    def draw(self):
        self.window.clear()
        self.draw_title("Game over!")
        self.window.refresh()

    def ask_play_again(self):
        self.window.clear()
        self.draw_title("Game over!")
        self.board_window.draw()
        self.board_window.highlight_winning_pattern()
        self.board_window.w.refresh()
        prompt = "Press ENTER to play again or any other key to exit."
        key = self.get_key(prompt)
        return key == "\n"


class BoardWindow:
    def __init__(self, window, board):
        self.w = window
        self.board = board

        rows_with_tokens = [0, 2, 4]
        cols_with_tokens = [1, 5, 9]
        self.token_yxs = list(itertools.product(rows_with_tokens, cols_with_tokens))
        self.space_colors = {}

    @classmethod
    def from_window(cls, window, board, nlines=6, ncols=12, start_y=2, start_x=3):
        window = window.subwin(nlines, ncols, start_y, start_x)
        return BoardWindow(window, board)

    def draw(self):
        v, h, p = "|", "=", "+"
        self.w.clear()

        # fmt: off
        self.w.addstr(0, 0, " {0} {v} {1} {v} {2} ".format(
            self.board[0], self.board[1], self.board[2], v=v
        ))
        self.w.addstr(1, 0, f"{h}{h}{h}{p}{h}{h}{h}{p}{h}{h}{h}")
        self.w.addstr(2, 0, " {0} {v} {1} {v} {2} ".format(
            self.board[3], self.board[4], self.board[5], v=v
        ))
        self.w.addstr(3, 0, f"{h}{h}{h}{p}{h}{h}{h}{p}{h}{h}{h}")
        self.w.addstr(4, 0, " {0} {v} {1} {v} {2} ".format(
            self.board[6], self.board[7], self.board[8], v=v
        ))
        # fmt: on

        # update spaces taken by player tokens with correct colors
        for space, color_ix in self.space_colors.items():
            y, x = self.token_yxs[space]
            self.w.chgat(y, x, 1, curses.color_pair(color_ix))

        self.w.refresh()

    def highlight_square(self, i, player_color_ix=None):
        y, x = self.token_yxs[i]
        if player_color_ix:
            self.w.chgat(
                y, x, 1, curses.color_pair(player_color_ix) | curses.A_STANDOUT
            )
            # store this space as this color for subsequent draws
            self.space_colors[i] = player_color_ix
        else:
            self.w.chgat(y, x, 1, curses.A_STANDOUT)

    def highlight_winning_pattern(self, *ixs):
        spaces = self.board.find_winning_pattern()
        for s in spaces:
            y, x = self.token_yxs[s]
            if self.space_colors and s in self.space_colors:
                color_ix = self.space_colors[s]
                self.w.chgat(y, x, 1, curses.color_pair(color_ix) | curses.A_STANDOUT)
            else:
                self.w.chgat(y, x, 1, curses.A_STANDOUT)


def configure_curses():
    if curses.has_colors():
        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.curs_set(0)  # make cursor invisible


def game_has_computer_players(player1, player2):
    return isinstance(player1, players.Computer) or isinstance(
        player2, players.Computer
    )
