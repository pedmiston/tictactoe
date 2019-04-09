# I mentioned this in your Memory app too, but I like having the exceptions all
# together like this. There's a possible maintenance cost, which I think is
# pretty unlikely to happen for a game like this but is still worth mentioning,
# in that if we need to de-couple the UI and the core game logic, this file mixes
# those things together and so would have to change as part of an unrelated change.
#
# Again, I wouldn't change it now, but it's something to keep in mind: this file
# mixes business logic knowledge and user interface knowledge.
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
