from copy import deepcopy

import pytest

from logic import (
    apply_move, can_select_piece, get_captures, get_legal_moves,
    player_has_any_move, player_has_capture,
)
from models import BLACK, RED, Move, Piece


@pytest.mark.parametrize("color, start, jumped, landing", [
    (RED, (5, 2), (4, 3), (3, 4)),
    (BLACK, (2, 3), (3, 2), (4, 1)),
])
def test_single_forward_capture(empty_board, color, start, jumped, landing):
    enemy = BLACK if color == RED else RED
    piece = Piece(color)
    empty_board[start[0]][start[1]] = piece
    empty_board[jumped[0]][jumped[1]] = Piece(enemy)
    before = deepcopy(empty_board)
    assert get_captures(empty_board, start) == [Move(landing, jumped)]
    assert empty_board == before
    assert player_has_any_move(empty_board, color)
    assert apply_move(empty_board, start, Move(landing, jumped)) == (True, False)
    assert empty_board[landing[0]][landing[1]] is piece
    assert empty_board[start[0]][start[1]] is None
    assert empty_board[jumped[0]][jumped[1]] is None


@pytest.mark.parametrize("adjacent, landing", [
    (None, None), (RED, None), (BLACK, BLACK), (BLACK, RED),
])
def test_invalid_capture(empty_board, adjacent, landing):
    empty_board[5][2] = Piece(RED)
    empty_board[4][3] = Piece(adjacent) if adjacent else None
    empty_board[3][4] = Piece(landing) if landing else None
    assert not get_captures(empty_board, (5, 2))


@pytest.mark.parametrize("color, row, enemy_row", [(RED, 3, 4), (BLACK, 3, 2)])
def test_regular_backward_capture_is_forbidden(empty_board, color, row, enemy_row):
    empty_board[row][2] = Piece(color)
    empty_board[enemy_row][3] = Piece(BLACK if color == RED else RED)
    assert not get_captures(empty_board, (row, 2))


@pytest.mark.parametrize("start, jumped", [((1, 0), (0, 1)), ((3, 6), (2, 7))])
def test_capture_cannot_leave_board(empty_board, start, jumped):
    empty_board[start[0]][start[1]] = Piece(RED)
    empty_board[jumped[0]][jumped[1]] = Piece(BLACK)
    assert not get_captures(empty_board, start)


@pytest.mark.parametrize("jumped, landing", [
    ((2, 1), (1, 0)), ((2, 3), (1, 4)),
    ((4, 1), (5, 0)), ((4, 3), (5, 4)),
])
def test_king_captures_each_direction(empty_board, jumped, landing):
    empty_board[3][2] = Piece(RED, True)
    empty_board[jumped[0]][jumped[1]] = Piece(BLACK)
    assert get_captures(empty_board, (3, 2)) == [Move(landing, jumped)]


def test_global_mandatory_capture_and_choice(empty_board):
    empty_board[5][0] = Piece(RED)
    empty_board[5][4] = Piece(RED)
    empty_board[5][6] = Piece(RED)
    empty_board[4][1] = Piece(BLACK)
    empty_board[4][3] = Piece(BLACK)
    assert player_has_capture(empty_board, RED)
    assert can_select_piece(empty_board, (5, 0), RED)
    assert can_select_piece(empty_board, (5, 4), RED)
    assert not can_select_piece(empty_board, (5, 6), RED)
    assert get_legal_moves(empty_board, (5, 6), RED) == []
    assert get_legal_moves(empty_board, (5, 4), RED) == [Move((3, 2), (4, 3))]
    assert get_legal_moves(empty_board, (5, 4), RED, (5, 0)) == []
    assert not can_select_piece(empty_board, (4, 1), RED)
    assert not can_select_piece(empty_board, (-1, 0), RED)
    assert not can_select_piece(empty_board, (3, 2), RED)


def test_opponent_captures_do_not_restrict_current_player(empty_board):
    empty_board[3][2] = Piece(BLACK)
    empty_board[4][3] = Piece(RED)
    empty_board[2][1] = Piece(RED)
    assert player_has_capture(empty_board, BLACK)
    assert not player_has_capture(empty_board, RED)
    assert get_legal_moves(empty_board, (2, 1), RED)


@pytest.mark.parametrize("color", [RED, BLACK])
def test_triple_jump_counts_three_captures_and_one_turn(empty_game, color):
    game = empty_game
    enemy = BLACK if color == RED else RED

    def position(row, col):
        return (row, col) if color == RED else (7 - row, 7 - col)

    for row, col, owner in [(7, 0, color), (7, 4, color), (6, 1, enemy),
                            (4, 3, enemy), (2, 5, enemy), (0, 7, enemy)]:
        r, c = position(row, col)
        game.board[r][c] = Piece(owner)
    game.current_player = color
    game.no_progress_turns = 79
    game.handle_square_click(position(7, 0))
    assert game.try_move(position(5, 2))
    assert game.current_player == color
    assert game.selected_pos == game.forced_jump_pos == position(5, 2)
    assert game.no_progress_turns == 79
    game.handle_square_click(position(7, 4))
    game.handle_square_click(position(5, 2))
    assert game.selected_pos == position(5, 2)
    assert not game.try_move(position(4, 1))
    assert game.try_move(position(3, 4))
    assert game.current_player == color
    assert game.no_progress_turns == 79
    assert game.try_move(position(1, 6))
    assert game.current_player == enemy
    assert game.scoreboard(color)["captures"] == 3
    assert game.scoreboard(enemy)["captures"] == 0
    assert game.no_progress_turns == 0
    assert game.selected_pos is None
    assert game.forced_jump_pos is None
    assert game.legal_moves == []


@pytest.mark.parametrize("short_route", [True, False])
def test_branching_jump_allows_either_route(empty_game, short_route):
    game = empty_game
    game.board[7][0] = Piece(RED, True)
    for row, col in [(6, 1), (4, 1), (4, 3), (2, 5), (0, 7)]:
        game.board[row][col] = Piece(BLACK)
    game.handle_square_click((7, 0))
    assert game.try_move((5, 2))
    assert {move.destination for move in game.legal_moves} == {(3, 0), (3, 4)}
    assert game.try_move((3, 0) if short_route else (3, 4))
    if short_route:
        assert game.red_captures == 2
        assert game.current_player == BLACK
    else:
        assert game.current_player == RED
        assert game.try_move((1, 6))
        assert game.red_captures == 3
        assert game.current_player == BLACK


def test_game_cannot_select_non_capturing_piece(empty_game):
    game = empty_game
    game.board[5][0] = Piece(RED)
    game.board[5][4] = Piece(RED)
    game.board[4][1] = Piece(BLACK)
    game.handle_square_click((5, 4))
    assert game.selected_pos is None
    game.handle_square_click((5, 0))
    assert game.selected_pos == (5, 0)
    assert "Capture required" in game.status_message
    before = deepcopy(game.board)
    assert not game.try_move((4, 1))
    assert game.board == before
