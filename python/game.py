import tictactoe

# curses is in the python standard library, but it may not be available
# on Windows because it depends on the GNU program ncurses.
import curses


if __name__ == "__main__":
    game = tictactoe.Game("game.log")
    curses.wrapper(game)
