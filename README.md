# Tic Tac Toe

Play the game with `python3 game.py`

## Requirements

This is the coding challenge I was given when I applied to 8th Light at the end
of last summer. The challenge required me to build a Tic Tac Toe command line
app that met the following requirements:

- The game does not gracefully handle bad user input.
- In its current form, it’s supposed to be played at a difficulty level of
  “hard”, meaning the computer player cannot be beaten, but in reality you can
  beat it with the right moves.
- The game play left a lot to be desired. The user messages are lacking in many
  ways, which I’m sure you can tell.
- Allow the user to choose the level of difficulty (“easy” means the computer
  can easily be beaten, “medium” means it can be beaten but only with a series
  of intelligent moves, and “hard” means the it is unbeatable).
- Allow the user to choose the game type (human v. human, computer v. computer,
  human v. computer).
- Allow the user to choose which player goes first.
- Allow the user to choose with what “symbol” the players will mark their
  selections on the board (traditionally it’s “X” and “O”).

## Development

The Tic Tac Toe application requires only the python3 standard library,
but the tests are written using pytest.

```bash
pipenv install --dev  # install the dev packages
pipenv run pytest     # run the tests
pipenv run black .    # run the formatter
```
