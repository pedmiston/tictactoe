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
    """Optimal strategy for TicTacToe."""
    winning_move = board.find_winning_move(computer.token)
    if winning_move != -1:
        return winning_move

    blocking_move = board.find_blocking_move(computer.token)
    if blocking_move != -1:
        return blocking_move

    if len(board.moves) == 0:
        move = computer.prng.choice(board.available_corners())
    elif len(board.moves) == 2:
        prev_move = board.get_last_token_location()
        if prev_move == "4":
            move = computer.prng.choice(board.available_corners())
        else:
            move = "4"
    elif len(board.moves) == 3:
        # first move was corner
        move = computer.prng.choice(board.available)
    else:
        move = computer.prng.choice(board.available)
    return move
