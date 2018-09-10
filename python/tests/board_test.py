import pytest
from tictactoe import exceptions
from tictactoe.board import Board


@pytest.fixture
def board():
    return Board()


def test_board_handles_bad_user_input(board):
    for bad_key in ["9", "q"]:
        with pytest.raises(exceptions.KeyNotOnBoardError):
            board[bad_key]


def test_board_handles_str_or_int(board):
    board[0] == board["0"]


def test_board_prevents_picking_same_spot_twice(board):
    board[0] = "X"
    with pytest.raises(exceptions.SpotAlreadySelectedError):
        board[0] = "X"


def test_board_prevents_picking_same_spot_as_opponent(board):
    board[0] = "X"
    with pytest.raises(exceptions.SpotTakenByOpponentError):
        board[0] = "O"


def test_board_keeps_track_of_token_sequence(board):
    board[0] = "X"
    board[1] = "O"
    board[2] = "X"
    assert board.get_last_token_location() == "2"


def test_board_starts_at_turn_0(board):
    assert board.turn == 0


def test_board_finds_three_in_a_row(board):
    board[0] = "X"
    board[1] = "X"
    board[2] = "X"
    assert board.find_three_in_a_row() == (0, 1, 2)


def test_board_finds_two_in_a_row(board):
    board[0] = "X"
    board[1] = "X"
    assert board.find_two_in_a_row() == 2


def test_board_fails_to_find_two_in_row(board):
    board[0] = "X"
    board[1] = "O"
    assert board.find_two_in_a_row() == -1


def test_board_finds_two_in_a_row_by_token(board):
    board[0] = "O"
    board[1] = "O"
    assert board.find_two_in_a_row(token="X") == -1


def test_board_finds_available_two_in_a_row(board):
    board[0] = "X"
    board[1] = "X"
    board[2] = "O"
    assert board.find_two_in_a_row(token="X") == -1
