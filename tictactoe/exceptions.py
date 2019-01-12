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
