import pytest
from tictactoe import exceptions, patterns
from tictactoe.board import Board, Move


def test_board_handles_bad_user_input(xo_board):
    for bad_key in ["9", "q"]:
        with pytest.raises(exceptions.KeyNotOnBoardError):
            xo_board[bad_key]


def test_board_handles_str_or_int(xo_board):
    xo_board[0] == xo_board["0"]


def test_board_prevents_picking_same_spot_twice(xo_board):
    xo_board[0] = "X"
    with pytest.raises(exceptions.SpotAlreadySelectedError):
        xo_board[0] = "X"


def test_board_prevents_picking_same_spot_as_opponent(xo_board):
    xo_board[0] = "X"
    with pytest.raises(exceptions.SpotTakenByOpponentError):
        xo_board[0] = "O"


def test_board_keeps_track_of_moves(xo_board):
    xo_board[0] = "X"
    xo_board[1] = "O"
    xo_board[2] = "X"
    assert xo_board.moves[0] == Move(0, "X")
    assert xo_board.moves[-1] == Move(2, "X")


def test_board_finds_winning_pattern(xo_board):
    xo_board[0] = "X"
    xo_board[1] = "X"
    xo_board[2] = "X"
    assert xo_board.find_winning_pattern() == (0, 1, 2)


def test_board_detects_all_winning_patterns():
    for s1, s2, s3 in patterns.winning_patterns:
        xo_board = Board(tokens=["X", "O"])
        xo_board[s1] = "X"
        xo_board[s2] = "X"
        xo_board[s3] = "X"
        assert xo_board.is_over()


def test_board_detects_tie(xo_board):
    for s in [0, 2, 3, 7, 8]:
        xo_board[s] = "X"
    for s in [1, 4, 5, 6]:
        xo_board[s] = "O"
    assert xo_board.is_tie()


def test_board_finds_adjacent_corner(xo_board):
    xo_board[0] = "X"
    assert xo_board.find_adjacent_corner("X") == 2


def test_boad_fails_to_find_adjacent_corner_if_blocked(xo_board):
    xo_board[0] = "X"
    xo_board[1] = "O"
    xo_board[3] = "O"
    assert xo_board.find_adjacent_corner("X") == -1


def test_board_finds_opposite_corner(xo_board):
    xo_board[0] = "X"
    assert xo_board.find_opposite_corner("X") == 8
