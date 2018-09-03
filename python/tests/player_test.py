import pytest
from tictactoe import exceptions
from tictactoe.models import Player


def test_player_cannot_set_improper_token():
    player = Player()
    for improper_token in ["[", "1"]:
        with pytest.raises(exceptions.ImproperTokenError):
            player.token = improper_token


def test_player_tokens_get_capitalized():
    player = Player()
    player.token = "x"
    assert player.token == "X"


def test_player_tokens_can_be_capitalized():
    player = Player()
    player.token = "X"
    assert player.token == "X"
