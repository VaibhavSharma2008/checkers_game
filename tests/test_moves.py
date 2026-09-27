from copy import deepcopy

import pytest

from logic import (
    apply_move, count_pieces, create_initial_board, get_normal_moves,
    is_inside_board, is_playable, opponent, player_has_any_move,
)
from models import BLACK, RED, Move, Piece


def test_initial_board():
    board = create_initial_board()
    assert len(board) == 8
    assert all(len(row) == 8 for row in board)
    assert count_pieces(board, RED) == (12, 0)
    assert count_pieces(board, BLACK) == (12, 0)
    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if (row + col) % 2 == 0 or row in (3, 4):
                assert piece is None
            else:
                assert piece == Piece(BLACK if row < 3 else RED)


def test_boards_rows_and_pieces_are_independent():
    first, second = create_initial_board(), create_initial_board()
    assert first[0] is not first[1]
    first[0][1].is_king = True
    first[2][1] = None
    assert second[0][1] == Piece(BLACK)
    assert second[2][1] == Piece(BLACK)


@pytest.mark.parametrize("color, expected", [
    (RED, {(2, 1), (2, 3)}), (BLACK, {(4, 1), (4, 3)}),
])
def test_regular_moves_are_one_square_forward(empty_board, color, expected):
    empty_board[3][2] = Piece(color)
    before = deepcopy(empty_board)
    moves = get_normal_moves(empty_board, (3, 2))
    assert {move.destination for move in moves} == expected
    assert all(move.captured is None for move in moves)
    assert empty_board == before


@pytest.mark.parametrize("occupant", [RED, BLACK])
def test_occupied_destinations_are_excluded(empty_board, occupant):
    empty_board[3][2] = Piece(RED)
    empty_board[2][1] = Piece(occupant)
    assert get_normal_moves(empty_board, (3, 2)) == [Move((2, 3))]


@pytest.mark.parametrize("position, inside, playable", [
    ((-1, 0), False, False), ((8, 1), False, False),
    ((1, -1), False, False), ((0, 8), False, False),
    ((0, 0), True, False), ((0, 1), True, True),
    ((7, 6), True, True), ((7, 7), True, False),
])
def test_coordinates(position, inside, playable):
    assert is_inside_board(position) is inside
    assert is_playable(position) is playable


@pytest.mark.parametrize("color, position, expected", [
    (RED, (5, 0), [Move((4, 1))]),
    (BLACK, (2, 7), [Move((3, 6))]),
    (RED, (0, 1), []), (BLACK, (7, 0), []),
])
def test_edge_movement(empty_board, color, position, expected):
    empty_board[position[0]][position[1]] = Piece(color)
    assert get_normal_moves(empty_board, position) == expected


def test_empty_and_invalid_positions_have_no_moves(empty_board):
    for position in [(3, 2), (-1, 0), (8, 1), (4, 4)]:
        assert get_normal_moves(empty_board, position) == []


def test_apply_normal_move_keeps_piece_identity_and_other_squares():
    board = create_initial_board()
    moving = board[5][0]
    before = deepcopy(board)
    assert apply_move(board, (5, 0), Move((4, 1))) == (False, False)
    assert board[4][1] is moving
    assert board[5][0] is None
    before[5][0], before[4][1] = None, moving
    assert board == before


def test_opponents_and_move_availability(empty_board):
    assert opponent(RED) == BLACK
    assert opponent(BLACK) == RED
    assert not player_has_any_move(empty_board, RED)
    empty_board[0][1] = Piece(RED)
    assert not player_has_any_move(empty_board, RED)
    empty_board[0][1].is_king = True
    assert player_has_any_move(empty_board, RED)
