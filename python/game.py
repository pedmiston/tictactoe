import sys
import curses
import random
import time
import string
import logging
import logging.config


logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': True,
    'handlers': {
        'game.log': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'game.log',
            'mode': 'w',
        },
    },
    'loggers': {
        'game': {
            'handlers': ['game.log'],
            'level': 'NOTSET',
        },
    }
})
logger = logging.getLogger('game')


game_types = {
    "1": "Human v Computer",
    "2": "Human v Human",
    "3": "Computer v Computer"
}


class Game:
    screen = None
    board = None
    player1 = None
    player2 = None

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
            stdscr: A curses.Window object

        Example:
            >>> import curses
            >>> game = Game()
            >>> curses.wrapper(game)
        """
        self.screen = Screen(stdscr)

        # Draw welcome screen and ask for game type
        self.screen.draw_welcome_screen()
        key = self.screen.get_key(list(game_types.keys()) + ["q"])
        if key == "q":
            logger.info("player quit the game")
            return
        game_type = game_types[key]
        if game_type == "Human v Computer":
            self.player1, self.player2 = Human(), Computer()
        elif game_type == "Human v Human":
            self.player1, self.player2 = Human("Player1"), Human("Player2")
        elif game_type == "Computer v Computer":
            self.player1, self.player2 = Computer("Computer1"), Computer("Computer2")
        else:
            raise TicTacToeError(f"unknown game type '({key}) {game_type}'")
        logger.info(f"player selected {game_type}")

        # Modify player settings
        self.edit_player_settings()

        # Set player order
        self.screen.draw_player_order(self.player1, self.player2)
        key = self.screen.get_key(["1", "2", "3"])
        if key == "1":
            pass
        elif key == "2":
            self.player1, self.player2 = self.player2, self.player1
        elif key == "3":
            if random.random() >= 0.5:
                self.player1, self.player2 = self.player2, self.player1
        else:
            raise TicTacToeError()
        logger.info(f"{self.player1} is going first")

        # Play the game until it's over or a player quits
        self.board = Board(tokens=[self.player1.token, self.player2.token])
        try:
            self.play_board()
        except PlayerQuitException:
            logger.info("player quit the game")
        else:
            logger.info("game over")

    def edit_player_settings(self):
        player1_token_yx, player2_token_yx = self.screen.draw_player_settings(self.player1, self.player2)

        # Edit player1 settings
        while True:
            self.screen.s.addstr(5, 0, "Enter the token to use for player 1.")
            key = self.screen.get_key(yx=player1_token_yx)
            try:
                self.player1.token = key
            except ImproperTokenError:
                self.screen.s.addstr(6, 0, "You can't use that as a token.")
            else:
                logger.info(f"{self.player1} selected token '{self.player1.token}'")
                self.screen.s.addstr(player1_token_yx[0], player1_token_yx[1], self.player1.token)
                break

        # Edit player2 settings
        while True:
            self.screen.s.addstr(5, 0, "Enter the token to use for player 2.")
            key = self.screen.get_key(yx=player2_token_yx)
            if key.upper() == self.player1.token:
                self.screen.s.addstr(6, 0, "You must use a different token from player 1.")
            else:
                try:
                    self.player2.token = key
                except ImproperTokenError:
                    self.screen.s.addstr(6, 0, "You can't use that as a token.")
                else:
                    logger.info(f"{self.player2} selected token '{self.player2.token}'")
                    self.screen.s.addstr(
                        player2_token_yx[0], player2_token_yx[1], self.player2.token
                    )
                    break

    def play_board(self):
        while not self.board.is_over() and not self.board.is_tie():
            self.screen.show_player_move(self.board, self.player1)
            if not self.board.is_over() and not self.board.is_tie():
                self.screen.show_player_move(self.board, self.player2)


class Screen:
    def __init__(self, stdscr):
        """Create a Tic Tac Toe screen out of a curses window."""
        self.s = stdscr

    def draw_welcome_screen(self):
        self.s.clear()
        self.s.addstr(0, 0, "Let's play Tic Tac Toe!")
        self.s.addstr(2, 0, "Which type of game would you like to play?")
        for i, game_type in game_types.items():
            self.s.addstr(2+int(i), 0, f"({i}) {game_type}")
        self.s.addstr(7, 0, "Enter [1-3] or Q to quit: ")
        self.s.refresh()

    def draw_player_settings(self, player1, player2):
        # Draw entire player settings screen before getting input
        self.s.clear()
        self.s.addstr(0, 0, "Edit player settings")

        ## Draw player1 settings
        self.s.addstr(2, 0, f"{player1} token: ")
        player1_token_yx = self.s.getyx()
        self.s.addstr("X")

        ## Draw player2 settings
        self.s.addstr(3, 0, f"{player2} token: ")
        player2_token_yx = self.s.getyx()
        self.s.addstr("O")

        return player1_token_yx, player2_token_yx

    def show_player_move(self, board, player):
        if isinstance(player, Human):
            self.show_human_move(board, player)
        elif isinstance(player, Computer):
            self.show_computer_move(board, player)
        else:
            # smells!
            raise TicTacToeException()

    def show_human_move(self, board, human):
        self.s.clear()
        self.s.refresh()
        self.s.addstr(0, 0, str(board))
        self.s.addstr(6, 0, "Enter [1-9] or Q to quit: ")
        input_yx = self.s.getyx()
        error_message_y = self.s.getyx()[0] + 1
        while True:
            key = self.get_key(yx=input_yx)
            if key == "q":
                raise PlayerQuitException()
            try:
                board[key] = human.token
            except KeyNotOnBoardError:
                error_message = "That key was not one of your options."
            except SpotAlreadySelectedError:
                error_message = "You've already placed a token in that square!"
            except SpotTakenByOpponentError:
                error_message = "Your opponent has already claimed that square."
            else:
                logger.info(f"{human} placed a token on {key}")
                break
            self.s.addstr(error_message_y, 0, error_message)

    def show_computer_move(self, board, computer):
        """Animate the Computer's move."""
        self.s.clear()
        self.s.refresh()
        self.s.addstr(0, 0, str(board))
        self.s.addstr(6, 0, f"{computer}'s turn...")
        move = computer.eval(board)
        board[move] = computer.token
        logger.info(f"{computer} placed a token on {move}")
        self.s.refresh()
        time.sleep(1)
        self.s.addstr(0, 0, str(board))

    def draw_player_order(self, player1, player2):
        self.s.clear()
        self.s.addstr(0, 0, "Who goes first?")
        self.s.addstr(2, 0, f"(1) {player1}")
        self.s.addstr(3, 0, f"(2) {player2}")
        self.s.addstr(4, 0, f"(3) Flip a coin")
        self.s.addstr(6, 0, "Enter [1-3]: ")
        self.s.refresh()

    def get_key(self, keys=None, yx=None):
        curses.echo()
        yx = yx or self.s.getyx()
        while True:
            key = self.s.getkey(*yx)
            if keys is None or key in keys:
                break
        curses.noecho()
        return key


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
    parser.add_argument('-l', '--logging', action='store_true', help='write game log')
    args = parser.parse_args()
    if args.logging:
        logger.setLevel(logging.DEBUG)
    game = Game()
    curses.wrapper(game)
