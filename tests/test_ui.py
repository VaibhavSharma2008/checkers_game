"""Small integration checks; the core test files never import Pygame."""

from copy import deepcopy

import pygame
import pytest

from game import Game
import main
from models import BLACK, RED, MatchStats, Piece
import ui


@pytest.fixture
def display(monkeypatch):
    monkeypatch.setenv("SDL_VIDEODRIVER", "dummy")
    monkeypatch.setenv("SDL_AUDIODRIVER", "dummy")
    pygame.init()
    screen = ui.create_window()
    yield screen
    pygame.quit()


def click(position, button=1):
    return pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=button, pos=position)


@pytest.mark.parametrize("action", ["new_game", "reset_match", "exit"])
def test_confirmation_blocks_board_and_cancel_preserves_everything(action):
    game = Game()
    game.select_piece((5, 0))
    before = deepcopy(vars(game))
    running, pending = main.handle_event(game, click(ui.BUTTONS[action].center), None)
    assert running and pending == action
    assert vars(game) == before
    running, pending = main.handle_event(game, click(ui.square_rect((4, 1)).center), pending)
    assert running and pending == action
    assert vars(game) == before
    assert main.handle_event(game, click(ui.CANCEL_RECT.center), pending) == (True, None)
    assert vars(game) == before


@pytest.mark.parametrize("action", ["new_game", "reset_match", "exit"])
def test_confirm_action(action):
    game = Game()
    game.match_stats.record_win(RED)
    game.handle_square_click((5, 0))
    game.handle_square_click((4, 1))
    board = game.board
    _, pending = main.handle_event(game, click(ui.BUTTONS[action].center), None)
    running, pending = main.handle_event(game, click(ui.CONFIRM_RECT.center), pending)
    assert pending is None
    assert running is (action != "exit")
    if action == "exit":
        assert game.board is board
        assert game.match_stats.red_wins == 1
    else:
        assert game.board is not board
        assert game.current_player == RED
        assert game.match_stats.red_wins == (1 if action == "new_game" else 0)
        assert not game.is_game_over


def test_new_game_after_result_skips_confirmation():
    game = Game()
    game.finish_game(BLACK, "Red has no legal moves")
    assert main.handle_event(game, click(ui.BUTTONS["new_game"].center), None) == (True, None)
    assert not game.is_game_over
    assert game.match_stats.black_wins == game.match_stats.red_losses == 1


@pytest.mark.parametrize("action", ["reset_match", "exit"])
def test_reset_and_exit_still_require_confirmation_after_result(action):
    game = Game()
    game.finish_game(RED, "Black has no legal moves")
    assert main.handle_event(game, click(ui.BUTTONS[action].center), None) == (True, action)
    assert game.is_game_over


def test_window_close_requires_confirmation():
    game = Game()
    close = pygame.event.Event(pygame.QUIT)
    assert main.handle_event(game, close, None) == (True, "exit")
    assert main.handle_event(game, click(ui.CANCEL_RECT.center), "exit") == (True, None)
    assert not game.is_game_over
    assert game.match_stats == MatchStats()


def test_mouse_moves_and_ignores_game_over_and_right_clicks():
    game = Game()
    main.handle_event(game, click(ui.square_rect((5, 0)).center, button=3), None)
    assert game.selected_pos is None
    main.handle_event(game, click(ui.square_rect((5, 0)).center), None)
    assert game.selected_pos == (5, 0)
    main.handle_event(game, click(ui.square_rect((4, 1)).center), None)
    assert game.board[4][1] == Piece(RED)
    assert game.current_player == BLACK
    game.finish_game(RED, "Black has no legal moves")
    before = deepcopy(vars(game))
    main.handle_event(game, click(ui.square_rect((2, 1)).center), None)
    assert vars(game) == before


def test_coordinate_conversion_and_buttons():
    for row in range(8):
        for col in range(8):
            assert ui.pixel_to_board(ui.square_rect((row, col)).center) == (row, col)
    for point in [(31, 100), (32, 99), ui.BOARD_RECT.bottomright, (640, 100), (32, 708)]:
        assert ui.pixel_to_board(point) is None
    for action, rect in ui.BUTTONS.items():
        assert ui.get_button_action(rect.center) == action
    assert ui.get_button_action((0, 0)) is None


def test_complete_application_loop_and_shutdown(display, monkeypatch):
    events = iter([
        [],
        [click(ui.square_rect((5, 0)).center)],
        [click(ui.square_rect((4, 1)).center)],
        [pygame.event.Event(pygame.QUIT)],
        [click(ui.CANCEL_RECT.center)],
        [click(ui.BUTTONS["exit"].center)],
        [click(ui.CONFIRM_RECT.center)],
    ])
    monkeypatch.setattr(pygame.event, "get", lambda: next(events))
    main.main()
    assert not pygame.get_init()


@pytest.mark.parametrize("state", [
    "initial", "selected", "forced_jump", "promotion", "zero_pieces", "blocked",
    "draw", "new_game", "reset_match", "exit",
])
def test_render_states(display, tmp_path, state):
    game = Game()
    pending = None
    if state == "selected":
        game.handle_square_click((5, 2))
    elif state == "forced_jump":
        game.board = [[None] * 8 for _ in range(8)]
        game.board[7][0] = Piece(RED, True)
        game.board[7][4] = Piece(RED)
        for row, col in [(6, 1), (4, 1), (4, 3), (2, 5), (0, 7)]:
            game.board[row][col] = Piece(BLACK)
        game.handle_square_click((7, 0))
        game.try_move((5, 2))
    elif state == "promotion":
        game.board = [[None] * 8 for _ in range(8)]
        game.board[2][1] = Piece(RED)
        game.board[1][2] = Piece(BLACK)
        game.board[1][4] = Piece(BLACK)
        game.handle_square_click((2, 1))
        game.try_move((0, 3))
    elif state == "zero_pieces":
        game.board = [[None] * 8 for _ in range(8)]
        game.board[5][0] = Piece(RED)
        game.board[4][1] = Piece(BLACK)
        game.handle_square_click((5, 0))
        game.try_move((3, 2))
    elif state == "blocked":
        game.board = [[None] * 8 for _ in range(8)]
        for row, col in [(5, 4), (6, 1), (7, 2)]:
            game.board[row][col] = Piece(RED)
        game.board[5][0] = Piece(BLACK)
        game.handle_square_click((5, 4))
        game.try_move((4, 3))
    elif state == "draw":
        game.no_progress_turns = 79
        game.handle_square_click((5, 0))
        game.try_move((4, 1))
    elif state in ui.CONFIRMATION_MESSAGES:
        _, pending = main.handle_event(game, click(ui.BUTTONS[state].center), None)
    before = deepcopy(vars(game))
    ui.draw_game(display, game, ui.create_fonts(), pending)
    pygame.display.flip()
    assert vars(game) == before
    pygame.image.save(display, str(tmp_path / f"{state}.png"))
