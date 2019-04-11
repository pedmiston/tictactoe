from tictactoe import screens, players


def test_welcome_screen_gets_game_type(stdscr):
    game_type_ix = 3
    stdscr.getkey.return_value = str(game_type_ix)
    window = screens.CursesWindow(stdscr)

    game_type = window.get_game_type()

    assert game_type == screens.GameType(game_type_ix)


def test_difficulty_screen_changes_player_difficulty(stdscr):
    player1 = players.Computer()
    player1.color_ix = 1
    player2 = players.Computer()
    player2.color_ix = 2

    stdscr.getkey.side_effect = ["3", "2"]

    difficulty_screen = screens.DifficultyScreen(stdscr, player1, player2)
    player1, player2 = difficulty_screen.update_computer_difficulties()

    assert player1.difficulty == "Hard"
    assert player2.difficulty == "Medium"
