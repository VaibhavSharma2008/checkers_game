"""Running game state and game-flow coordination."""

import logic
from models import RED, MatchStats, Move, Position


class Game:
    def __init__(self) -> None:
        self.match_stats = MatchStats()
        self.new_game()

    def new_game(self) -> None:
        """Start a fresh game, preserving this session's match statistics."""
        self.board = logic.create_initial_board()
        self.current_player = RED
        self.selected_pos: Position | None = None
        self.forced_jump_pos: Position | None = None
        self.legal_moves: list[Move] = []
        self.red_captures = 0
        self.black_captures = 0
        self.no_progress_turns = 0
        self.is_game_over = False
        self.winner: str | None = None
        self.game_over_reason = ""
        self.status_message = "Red's turn"

    def update_status(self) -> None:
        if self.is_game_over:
            return
        if self.forced_jump_pos is not None:
            self.status_message = "Continue jump with selected piece"
        elif logic.player_has_capture(self.board, self.current_player):
            self.status_message = f"{self.current_player}'s turn - Capture required"
        else:
            self.status_message = f"{self.current_player}'s turn"

    def select_piece(self, position: Position) -> None:
        if self.is_game_over or self.forced_jump_pos is not None:
            return
        if position == self.selected_pos:
            self.selected_pos = None
            self.legal_moves = []
            return
        moves = logic.get_legal_moves(self.board, position, self.current_player)
        if moves:
            self.selected_pos = position
            self.legal_moves = moves
            self.update_status()

    def reset_match(self) -> None:
        self.match_stats.reset()
        self.new_game()

    def scoreboard(self, player: str) -> dict[str, int]:
        regular, kings = logic.count_pieces(self.board, player)
        stats = self.match_stats
        if player == RED:
            captures = self.red_captures
            wins, losses, draws = stats.red_wins, stats.red_losses, stats.red_draws
        else:
            captures = self.black_captures
            wins, losses, draws = stats.black_wins, stats.black_losses, stats.black_draws
        return {
            "regular": regular, "kings": kings, "captures": captures,
            "wins": wins, "losses": losses, "draws": draws,
        }

    def handle_square_click(self, position: Position) -> None:
        if self.is_game_over or not logic.is_playable(position):
            return
        if self.selected_pos is not None and self.try_move(position):
            return
        self.select_piece(position)

    def try_move(self, destination: Position) -> bool:
        if self.is_game_over or self.selected_pos is None:
            return False
        moves = logic.get_legal_moves(
            self.board, self.selected_pos, self.current_player, self.forced_jump_pos
        )
        move = next((move for move in moves if move.destination == destination), None)
        if move is None:
            return False
        captured, promoted = logic.apply_move(self.board, self.selected_pos, move)
        if captured:
            if self.current_player == RED:
                self.red_captures += 1
            else:
                self.black_captures += 1
            # Crowning ends a capture turn, even if a new King could jump back.
            continuations = [] if promoted else logic.get_captures(self.board, destination)
            if continuations:
                self.selected_pos = destination
                self.forced_jump_pos = destination
                self.legal_moves = continuations
                self.status_message = "Continue jump with selected piece"
                return True
        moving_player = self.current_player
        self.complete_turn(captured or promoted)
        if promoted:
            self.status_message = (
                f"{moving_player} piece promoted to King. {self.status_message}"
            )
        return True

    def complete_turn(self, progress_made: bool) -> None:
        # Called once per whole turn; every final jump reports a capture.
        self.no_progress_turns = 0 if progress_made else self.no_progress_turns + 1
        self.selected_pos = None
        self.forced_jump_pos = None
        self.legal_moves = []
        other_player = logic.opponent(self.current_player)
        if sum(logic.count_pieces(self.board, other_player)) == 0:
            self.finish_game(self.current_player, f"{other_player} has no remaining pieces")
            return
        if not logic.player_has_any_move(self.board, other_player):
            self.finish_game(self.current_player, f"{other_player} has no legal moves")
            return
        # A decisive win takes precedence over the no-progress draw threshold.
        if self.no_progress_turns >= 80:
            self.finish_game(None, "80 turns without capture or promotion")
            return
        self.current_player = logic.opponent(self.current_player)
        self.update_status()

    def finish_game(self, winner: str | None, reason: str) -> None:
        if self.is_game_over:
            return
        self.is_game_over = True
        self.winner = winner
        self.game_over_reason = reason
        self.selected_pos = None
        self.forced_jump_pos = None
        self.legal_moves = []
        result = f"{winner} wins" if winner is not None else "Draw"
        self.status_message = f"{result}: {reason}"
        if winner is None:
            self.match_stats.record_draw()
        else:
            self.match_stats.record_win(winner)
