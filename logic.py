"""Board calculations and rules for American Checkers."""

from models import BLACK, BOARD_SIZE, RED, Board, Move, Piece, Position


def is_inside_board(position: Position) -> bool:
    row, col = position
    return 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE


def is_playable(position: Position) -> bool:
    return is_inside_board(position) and sum(position) % 2 == 1


def opponent(player: str) -> str:
    if player == RED:
        return BLACK
    if player == BLACK:
        return RED
    raise ValueError(f"Unknown player: {player}")


def create_initial_board() -> Board:
    board: Board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            if is_playable((row, col)):
                if row < 3:
                    board[row][col] = Piece(BLACK)
                elif row >= 5:
                    board[row][col] = Piece(RED)
    return board


def movement_directions(piece: Piece) -> tuple[int, ...]:
    if piece.is_king:
        return (-1, 1)
    return (-1,) if piece.color == RED else (1,)


def get_normal_moves(board: Board, position: Position) -> list[Move]:
    if not is_playable(position):
        return []
    row, col = position
    piece = board[row][col]
    if piece is None:
        return []
    moves = []
    for row_step in movement_directions(piece):
        for col_step in (-1, 1):
            destination = (row + row_step, col + col_step)
            if is_inside_board(destination):
                end_row, end_col = destination
                if board[end_row][end_col] is None:
                    moves.append(Move(destination))
    return moves


def get_captures(board: Board, position: Position) -> list[Move]:
    if not is_playable(position):
        return []
    row, col = position
    piece = board[row][col]
    if piece is None:
        return []
    moves = []
    for row_step in movement_directions(piece):
        for col_step in (-1, 1):
            captured = (row + row_step, col + col_step)
            destination = (row + 2 * row_step, col + 2 * col_step)
            if not is_inside_board(destination):
                continue
            jumped = board[captured[0]][captured[1]]
            if (
                jumped is not None
                and jumped.color != piece.color
                and board[destination[0]][destination[1]] is None
            ):
                moves.append(Move(destination, captured))
    return moves


def player_has_capture(board: Board, player: str) -> bool:
    for row, squares in enumerate(board):
        for col, piece in enumerate(squares):
            if piece is not None and piece.color == player:
                if get_captures(board, (row, col)):
                    return True
    return False


def get_legal_moves(
    board: Board,
    position: Position,
    player: str,
    forced_position: Position | None = None,
) -> list[Move]:
    if not is_playable(position):
        return []
    piece = board[position[0]][position[1]]
    if piece is None or piece.color != player:
        return []
    if forced_position is not None:
        return get_captures(board, position) if position == forced_position else []
    if player_has_capture(board, player):
        return get_captures(board, position)
    return get_normal_moves(board, position)


def can_select_piece(
    board: Board,
    position: Position,
    player: str,
    forced_position: Position | None = None,
) -> bool:
    return bool(get_legal_moves(board, position, player, forced_position))


def apply_move(board: Board, start: Position, move: Move) -> tuple[bool, bool]:
    """Apply an already validated move; return (captured, promoted)."""
    piece = board[start[0]][start[1]]
    if piece is None:
        raise ValueError("Cannot move an empty square")
    board[start[0]][start[1]] = None
    board[move.destination[0]][move.destination[1]] = piece
    captured = move.captured is not None
    if move.captured is not None:
        board[move.captured[0]][move.captured[1]] = None
    promotion_row = 0 if piece.color == RED else BOARD_SIZE - 1
    promoted = not piece.is_king and move.destination[0] == promotion_row
    if promoted:
        piece.is_king = True
    return captured, promoted


def count_pieces(board: Board, player: str) -> tuple[int, int]:
    regular = kings = 0
    for row in board:
        for piece in row:
            if piece is not None and piece.color == player:
                if piece.is_king:
                    kings += 1
                else:
                    regular += 1
    return regular, kings


def player_has_any_move(board: Board, player: str) -> bool:
    # Any capture is legal for some piece; otherwise a normal move is enough.
    for row, squares in enumerate(board):
        for col, piece in enumerate(squares):
            if piece is not None and piece.color == player:
                position = (row, col)
                if get_captures(board, position) or get_normal_moves(board, position):
                    return True
    return False
