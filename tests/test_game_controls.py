from copy import deepcopy

import pytest

from game import Game
from logic import count_pieces
from models import BLACK, RED, MatchStats, Move, Piece


def assert_fresh_game(game):
    assert count_pieces(game.board, RED) == (12, 0)
    assert count_pieces(game.board, BLACK) == (12, 0)
    assert game.current_player == RED
    assert game.red_captures == game.black_captures == 0
    assert game.selected_pos is None
    assert game.forced_jump_pos is None
    assert game.legal_moves == []
    assert game.no_progress_turns == 0
    assert not game.is_game_over
    assert game.winner is None
    assert game.game_over_reason == ""
    assert game.status_message == "Red's turn"


def prepare_used_game(game):
    game.match_stats.record_win(RED)
    game.match_stats.record_win(RED)
    game.match_stats.record_win(BLACK)
    game.match_stats.record_draw()
    game.board[5][0] = None
    game.board[3][2] = Piece(BLACK, True)
    game.current_player = BLACK
    game.red_captures = 4
    game.black_captures = 3
    game.selected_pos = game.forced_jump_pos = (3, 2)
    game.legal_moves = [Move((5, 4), (4, 3))]
    game.no_progress_turns = 43
    game.status_message = "Continue jump with selected piece"


def test_initial_game():
    game = Game()
    assert_fresh_game(game)
    assert game.match_stats == MatchStats()


@pytest.mark.parametrize("finished", [False, True])
def test_new_game_resets_everything_except_statistics(finished):
    game = Game()
    prepare_used_game(game)
    if finished:
        game.finish_game(BLACK, "Red has no legal moves")
    old_board = game.board
    stats = game.match_stats
    expected = deepcopy(stats)
    game.new_game()
    assert_fresh_game(game)
    assert game.board is not old_board
    assert game.match_stats is stats
    assert game.match_stats == expected


def test_abandoning_unfinished_game_records_no_result():
    game = Game()
    game.handle_square_click((5, 0))
    game.handle_square_click((4, 1))
    game.new_game()
    assert game.match_stats == MatchStats()


def test_selection_reselection_deselection_and_invalid_clicks():
    game = Game()
    game.handle_square_click((5, 0))
    assert game.selected_pos == (5, 0)
    for invalid in [(0, 1), (6, 1), (4, 3), (5, 1), (-1, 0), (8, 1)]:
        before = deepcopy(vars(game))
        game.handle_square_click(invalid)
        assert vars(game) == before
    game.handle_square_click((5, 2))
    assert game.selected_pos == (5, 2)
    game.handle_square_click((5, 2))
    assert game.selected_pos is None
    assert game.legal_moves == []


def test_match_stats_records_each_result():
    stats = MatchStats()
    stats.record_win(RED)
    assert stats == MatchStats(red_wins=1, black_losses=1)
    stats.record_win(BLACK)
    stats.record_draw()
    assert stats == MatchStats(1, 1, 1, 1, 1, 1)
    stats.reset()
    assert stats == MatchStats()


@pytest.mark.parametrize("finished", [False, True])
def test_reset_match_clears_session_and_current_game(finished):
    game = Game()
    prepare_used_game(game)
    if finished:
        game.finish_game(None, "80 turns without capture or promotion")
    old_board = game.board
    game.reset_match()
    assert_fresh_game(game)
    assert game.board is not old_board
    assert game.match_stats == MatchStats()
