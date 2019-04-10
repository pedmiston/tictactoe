from tictactoe import board


def test_winning_patterns_for_3x3_board():
    expected = set(
        [
            (0, 1, 2),
            (3, 4, 5),
            (6, 7, 8),
            (0, 3, 6),
            (1, 4, 7),
            (2, 5, 8),
            (0, 4, 8),
            (2, 4, 6),
        ]
    )

    actual = board.get_winning_patterns()

    assert actual == expected
