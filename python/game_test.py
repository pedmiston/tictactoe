import pytest
from game import Game
from game import BAD_USER_INPUT, SPOT_ALREADY_SELECTED, SPOT_TAKEN_BY_OPPONENT


@pytest.fixture
def game(tmpdir):
    tmpfile = tmpdir.join('test-game.txt')
    game = Game(tmpfile)
    yield game
    game._file.close()


def test_game_handles_bad_user_input(game):
    for bad_key in ["9", "q"]:
        game.get_human_spot(simulate_key=bad_key)
        assert read_last_game_line(game) == BAD_USER_INPUT

def test_game_prevents_hum_picking_same_spot_twice(game):
    game.board[0] = "O"
    game.get_human_spot(simulate_key="0")
    assert read_last_game_line(game) == SPOT_ALREADY_SELECTED

def test_game_prevents_picking_same_spot_as_opponent(game):
    game.board[0] = "X"
    game.get_human_spot(simulate_key="0")
    assert read_last_game_line(game) == SPOT_TAKEN_BY_OPPONENT



def read_last_game_line(game):
    return read_last_line(game._file.name)

def read_last_line(txt):
    return open(txt, 'r').readlines()[-1].strip()
