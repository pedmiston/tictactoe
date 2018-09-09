from .app import Game, curses

game = Game("game.log")
curses.wrapper(game)
