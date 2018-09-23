def easy(computer, board):
    """Choose one of the available spaces at random."""
    return computer.prng.choice(board.available())


def medium(computer, board):
    """Win or block if able, otherwise pick center or at random."""
    winning_move = board.find_winning_move(computer.token)
    if winning_move != -1:
        return winning_move

    blocking_move = board.find_blocking_move(computer.token)
    if blocking_move != -1:
        return blocking_move

    if board[4] == "4":
        return 4
    else:
        return computer.prng.choice(board.available())


def hard(computer, board):
    """Optimally select positions on a board."""
    # If you can win, win.
    winning_move = board.find_winning_move(computer.token)
    if winning_move != -1:
        return winning_move

    # If you need to block, block.
    blocking_move = board.find_blocking_move(computer.token)
    if blocking_move != -1:
        return blocking_move

    turn = len(board.moves)
    if not turn % 2:
        # Implement the optimal first turn strategy
        move = optimal_first_turn_strategy(computer, board, turn)
    else:
        # Implement the best response strategy
        move = optimal_response_strategy(computer, board, turn)

    return move


def optimal_first_turn_strategy(computer, board, turn):
    assert not turn % 2, f"turn {turn} is not a first turn strategy"
    if turn == 0:
        return computer.prng.choice(board.available_corners())
    elif turn == 2:
        if board[4] != "4":
            # other player picked center, go opposite corner
            return board.find_opposite_corner(computer.token)
        else:
            # pick adjacent corner
            return board.find_adjacent_corner(computer.token)
    elif turn == 4:
        # was blocked and player did not take middle
        return 4
    else:
        # game is a tie
        return computer.prng.choice(board.available())


def optimal_response_strategy(computer, board, turn):
    assert turn % 2, f"turn {turn} is not a response strategy"
    if turn == 1:
        if board[4] == "4":
            return 4
        else:
            return computer.prng.choice(board.available_corners())
    return computer.prng.choice(board.available())
