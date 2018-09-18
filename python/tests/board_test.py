import pytest
from tictactoe import exceptions
from tictactoe.board import Board, Move


@pytest.fixture
def board():
    return Board(tokens=["X", "O"])


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


def test_board_keeps_track_of_moves(board):
    board[0] = "X"
    board[1] = "O"
    board[2] = "X"
    assert board.moves[0] == Move(0, "X")
    assert board.moves[-1] == Move(2, "X")


def test_board_finds_winning_pattern(board):
    board[0] = "X"
    board[1] = "X"
    board[2] = "X"
    assert board.find_winning_pattern() == (0, 1, 2)


def test_board_finds_winning_move(board):
    board[0] = "X"
    board[1] = "X"
    assert board.find_winning_move("X") == 2


def test_board_fails_to_find_incomplete_pattern(board):
    board[0] = "X"
    board[5] = "X"
    assert board.find_winning_move("X") == -1


def test_board_fails_to_find_occupied_winning_move(board):
    board[0] = "X"
    board[1] = "X"
    board[2] = "O"
    assert board.find_winning_move("X") == -1


def test_board_finds_blocking_move(board):
    board[0] = "X"
    board[1] = "X"
    assert board.find_blocking_move("O") == 2

def test_board_detects_all_winning_patterns():
    for s1, s2, s3 in Board.winning_patterns:
        board = Board()
        board[s1] = "X"
        board[s2] = "X"
        board[s3] = "X"
        assert board.is_over()

def test_board_detects_tie(board):
    for s in [0, 2, 3, 7, 8]:
        board[s] = "X"
    for s in [1, 4, 5, 6]:
        board[s] = "O"
    assert board.is_tie()
