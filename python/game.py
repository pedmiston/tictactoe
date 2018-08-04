import sys


BAD_USER_INPUT = "The square you entered is not on the board!"
SPOT_ALREADY_SELECTED = "You've already placed a piece in that square!"
SPOT_TAKEN_BY_OPPONENT = "Your opponent has already taken that spot."


class TicTacToeException(Exception):
    pass

class SpotAlreadySelectedException(TicTacToeException):
    pass

class SpotTakenByOpponentException(TicTacToeException):
    pass


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
        return self._board[key]

    def __setitem__(self, key, value):
        """Places a token on the board.

        >>> board[4] = "X"  # attempts to place "X" in square 4
        """
        prev = self[key]
        if prev == value:
            raise SpotAlreadySelectedException()
        elif prev in self.tokens:
            raise SpotTakenByOpponentException()
        self._board[key] = value


class Game:
    def __init__(self, file=None):
        if file is None:
            self._file = sys.stdout
        else:
            self._file = open(file, "w+", 1)

        self.com = "X"  # the computer's marker
        self.hum = "O"  # the user's marker
        self.board = Board(tokens=[self.com, self.hum])

    def draw(self, msg):
        """Draw something to the game buffer."""
        self._file.write(str(msg))

    def start_game(self):
        # start by printing the board
        self.draw(self.board)
        # loop through until the game was won or tied
        while not self.game_is_over(self.board) and not self.tie(self.board):
            self.get_human_spot()
            if not self.game_is_over(self.board) and not self.tie(self.board):
                self.eval_board()

            self.draw(self.board)

        self.draw("Game over")

    def get_human_spot(self, simulate_key=None):
        in_turn = True
        while in_turn:
            if simulate_key is not None:
                key = simulate_key
                in_turn = False
                self.draw(f"Enter [0-8]: {key}\n")
            else:
                key = input("Enter [0-8]: ")

            try:
                self.board[int(key)] = self.hum
            except (ValueError, IndexError):
                self.draw(BAD_USER_INPUT+'\n')
            except SpotAlreadySelectedException:
                self.draw(SPOT_ALREADY_SELECTED+'\n')
            except SpotTakenByOpponentException:
                self.draw(SPOT_TAKEN_BY_OPPONENT+'\n')
            else:
                in_turn = False

    def eval_board(self):
        spot = None
        while spot is None:
            if self.board[4] == "4":
                spot = 4
                self.board[spot] = self.com
            else:
                spot = self.get_best_move(self.board, self.com)
                if self.board[spot] != "X" and self.board[spot] != "O":
                    self.board[spot] = self.com
                else:
                    spot = None

    def get_best_move(self, board, next_player, depth=0, best_score={}):
        available_spaces = [s for s in board if s != "X" and s != "O"]
        best_move = None

        for avail in available_spaces:
            board[int(avail)] = self.com
            if self.game_is_over(board):
                best_move = int(avail)
                board[int(avail)] = avail
                return best_move
            else:
                board[int(avail)] = self.hum
                if self.game_is_over(board):
                    best_move = int(avail)
                    board[int(avail)] = avail
                    return best_move
                else:
                    board[int(avail)] = avail

        if best_move:
            return best_move
        else:
            return int(available_spaces[0])

    def three_in_a_row(self, *args):
        return (
            args[0] == args[1] == args[2] == "X" or args[0] == args[1] == args[2] == "O"
        )

    def game_is_over(self, b):
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

    def tie(self, b):
        return len([s for s in b if s == "X" or s == "O"]) == 9


if __name__ == "__main__":
    game = Game()
    game.start_game()
