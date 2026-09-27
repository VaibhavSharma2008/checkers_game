from copy import deepcopy

import pytest

from game import Game
from models import BLACK, RED, Piece


@pytest.mark.parametrize("winner", [RED, BLACK])
@pytest.mark.parametrize("reason", ["no remaining pieces", "no legal moves"])
def test_win_conditions_and_statistics_once(empty_game, winner, reason):
    game = empty_game
    enemy = BLACK if winner == RED else RED

    def position(row, col):
        return (row, col) if winner == RED else (7 - row, 7 - col)

    if reason == "no remaining pieces":
        placement = [(5, 0, winner), (4, 1, enemy)]
        start, destination = position(5, 0), position(3, 2)
    else:
        placement = [(5, 4, winner), (5, 0, enemy), (6, 1, winner), (7, 2, winner)]
        start, destination = position(5, 4), position(4, 3)
    for row, col, owner in placement:
        r, c = position(row, col)
        game.board[r][c] = Piece(owner)
    game.current_player = winner
    game.handle_square_click(start)
    assert game.try_move(destination)
    assert game.is_game_over
    assert game.winner == winner
    assert game.current_player == winner
    assert game.game_over_reason == f"{enemy} has {reason}"
    assert game.scoreboard(winner)["wins"] == 1
    assert game.scoreboard(enemy)["losses"] == 1
    before = deepcopy(vars(game))
    game.finish_game(winner, "duplicate result")
    game.handle_square_click(destination)
    assert not game.try_move(start)
    assert vars(game) == before


def test_blocked_player_win_takes_precedence_over_draw(empty_game):
    game = empty_game
    game.board[5][4] = Piece(RED)
    game.board[5][0] = Piece(BLACK)
    game.board[6][1] = Piece(RED)
    game.board[7][2] = Piece(RED)
    game.no_progress_turns = 79
    game.handle_square_click((5, 4))
    assert game.try_move((4, 3))
    assert game.no_progress_turns == 80
    assert game.winner == RED
    assert game.match_stats.red_draws == game.match_stats.black_draws == 0


def test_game_remains_active_when_opponent_can_move():
    game = Game()
    game.handle_square_click((5, 0))
    assert game.try_move((4, 1))
    assert not game.is_game_over
    assert game.winner is None
    assert not any(vars(game.match_stats).values())


def test_draw_after_eighty_actual_completed_turns(empty_game):
    game = empty_game
    game.board[7][0] = Piece(RED, True)
    game.board[0][7] = Piece(BLACK, True)
    cycle = [((7, 0), (6, 1)), ((0, 7), (1, 6)),
             ((6, 1), (7, 0)), ((1, 6), (0, 7))]
    for turn in range(80):
        start, destination = cycle[turn % 4]
        game.handle_square_click(start)
        assert game.try_move(destination)
        assert game.no_progress_turns == turn + 1
        assert game.is_game_over is (turn == 79)
    assert game.winner is None
    assert game.game_over_reason == "80 turns without capture or promotion"
    assert game.match_stats.red_draws == game.match_stats.black_draws == 1
    assert game.match_stats.red_wins == game.match_stats.black_wins == 0
    game.finish_game(None, "duplicate")
    assert game.match_stats.red_draws == game.match_stats.black_draws == 1


@pytest.mark.parametrize("chain", [False, True])
def test_capture_resets_counter_only_when_turn_finishes(empty_game, chain):
    game = empty_game
    game.board[5][0] = Piece(RED)
    game.board[4][1] = Piece(BLACK)
    game.board[0][7] = Piece(BLACK)
    if chain:
        game.board[2][3] = Piece(BLACK)
    game.no_progress_turns = 79
    game.handle_square_click((5, 0))
    assert game.try_move((3, 2))
    if chain:
        assert game.no_progress_turns == 79
        assert not game.is_game_over
        assert game.try_move((1, 4))
    assert game.no_progress_turns == 0
    assert not game.is_game_over


def test_quiet_promotion_resets_counter(empty_game):
    game = empty_game
    game.board[1][2] = Piece(RED)
    game.board[6][7] = Piece(BLACK)
    game.no_progress_turns = 79
    game.handle_square_click((1, 2))
    assert game.try_move((0, 1))
    assert game.no_progress_turns == 0
    assert not game.is_game_over
    assert game.board[0][1].is_king


def test_selection_and_invalid_move_do_not_count_as_turns():
    game = Game()
    game.no_progress_turns = 78
    game.handle_square_click((5, 0))
    assert not game.try_move((3, 2))
    game.handle_square_click((5, 0))
    assert game.no_progress_turns == 78
    game.handle_square_click((5, 0))
    assert game.try_move((4, 1))
    assert game.no_progress_turns == 79
    assert not game.is_game_over
