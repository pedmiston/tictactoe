def easy(computer, board):
    """Easy computer chooses one of the available spaces at random."""
    return computer.prng.choice(board.available)

def medium(computer, board):
    # are there two of mine in a row? -> win
    # are there two of my opponents in a row? -> block

    if board.turn == 0:
        move = "4"
    else:
        move = computer.prng.choice(board.available)
    return move

def hard(computer, board):
    winning_move = board.find_two_in_a_row(token=computer.token)
    if winning_move != -1:
        return winning_move

    blocking_move = board.find_two_in_a_row(blocking_token=computer.token)
    if blocking_move != -1:
        return blocking_move

    if board.turn == 0:
        move = computer.prng.choice(board.available_corners())
    elif board.turn == 1:
        prev_move = board.get_last_token_location()
        if prev_move == "4":
            move = computer.prng.choice(board.available_corners())
        else:
            move = "4"
    elif board.turn == 2:
        # first move was corner
        move = computer.prng.choice(board.available)
    else:
        move = computer.prng.choice(board.available)
    return move

algorithms = {"easy": easy, "medium": medium, "hard": hard}
