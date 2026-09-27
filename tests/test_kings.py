import pytest

from logic import apply_move, get_captures, get_normal_moves
from models import BLACK, RED, Move, Piece


@pytest.mark.parametrize("color, start, destination", [
    (RED, (1, 2), (0, 1)), (BLACK, (6, 1), (7, 2)),
])
def test_promotion(empty_board, color, start, destination):
    piece = Piece(color)
    empty_board[start[0]][start[1]] = piece
    assert apply_move(empty_board, start, Move(destination)) == (False, True)
    assert piece.is_king
    assert empty_board[destination[0]][destination[1]] is piece


@pytest.mark.parametrize("color", [RED, BLACK])
def test_king_moves_one_square_in_all_four_directions(empty_board, color):
    empty_board[3][2] = Piece(color, True)
    assert {move.destination for move in get_normal_moves(empty_board, (3, 2))} == {
        (2, 1), (2, 3), (4, 1), (4, 3),
    }


def test_king_cannot_fly_over_gap_or_two_pieces(empty_board):
    empty_board[5][0] = Piece(RED, True)
    empty_board[3][2] = Piece(BLACK)
    assert get_captures(empty_board, (5, 0)) == []
    empty_board[4][1] = Piece(BLACK)
    assert get_captures(empty_board, (5, 0)) == []


@pytest.mark.parametrize("color, start, destination", [
    (RED, (1, 2), (0, 1)), (BLACK, (6, 1), (7, 2)),
])
def test_existing_king_is_not_promoted_again(empty_board, color, start, destination):
    empty_board[start[0]][start[1]] = Piece(color, True)
    assert apply_move(empty_board, start, Move(destination)) == (False, False)


def test_king_changes_direction_in_chain(empty_game):
    game = empty_game
    game.board[5][2] = Piece(RED, True)
    game.board[4][3] = Piece(BLACK)
    game.board[4][5] = Piece(BLACK)
    game.board[0][1] = Piece(BLACK)
    game.handle_square_click((5, 2))
    assert game.try_move((3, 4))
    assert game.forced_jump_pos == (3, 4)
    assert game.legal_moves == [Move((5, 6), (4, 5))]
    assert game.try_move((5, 6))
    assert game.current_player == BLACK
    assert game.red_captures == 2
    assert game.board[5][6] == Piece(RED, True)


@pytest.mark.parametrize("color", [RED, BLACK])
def test_capture_promotion_ends_turn_despite_available_king_jump(empty_game, color):
    game = empty_game
    enemy = BLACK if color == RED else RED

    def position(row, col):
        return (row, col) if color == RED else (7 - row, 7 - col)

    for row, col, owner in [(2, 1, color), (1, 2, enemy), (1, 4, enemy)]:
        r, c = position(row, col)
        game.board[r][c] = Piece(owner)
    game.current_player = color
    game.no_progress_turns = 79
    game.handle_square_click(position(2, 1))
    assert game.try_move(position(0, 3))
    r, c = position(0, 3)
    assert game.board[r][c] == Piece(color, True)
    assert get_captures(game.board, position(0, 3))
    assert game.current_player == enemy
    assert game.selected_pos is None
    assert game.forced_jump_pos is None
    assert game.legal_moves == []
    assert game.no_progress_turns == 0
    assert game.scoreboard(color)["captures"] == 1
    assert "promoted to King" in game.status_message
    assert not game.try_move(position(2, 5))
