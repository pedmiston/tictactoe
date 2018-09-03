from .game import Game, curses

game = Game("game.log")
curses.wrapper(game)
