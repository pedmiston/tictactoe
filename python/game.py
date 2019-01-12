import tictactoe

# curses is in the python standard library, but it may not be available
# on Windows because it depends on the GNU program "ncurses".
import curses


if __name__ == "__main__":
    game = tictactoe.Game("game.log")

    # curses.wrapper "wraps" the game in a curses terminal window application
    # environment, passing the window in as the first argument. This method
    # ensures that control is properly handed back to the native terminal
    # application upon exit or error.
    curses.wrapper(game)
