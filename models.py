"""Shared data models and constants for American Checkers."""

from dataclasses import dataclass
from typing import TypeAlias

RED = "Red"
BLACK = "Black"
BOARD_SIZE = 8

Position: TypeAlias = tuple[int, int]


@dataclass
class Piece:
    color: str
    is_king: bool = False


Board: TypeAlias = list[list[Piece | None]]


@dataclass
class Move:
    destination: Position
    captured: Position | None = None


@dataclass
class MatchStats:
    red_wins: int = 0
    red_losses: int = 0
    red_draws: int = 0
    black_wins: int = 0
    black_losses: int = 0
    black_draws: int = 0

    def record_win(self, winner: str) -> None:
        if winner == RED:
            self.red_wins += 1
            self.black_losses += 1
        elif winner == BLACK:
            self.black_wins += 1
            self.red_losses += 1
        else:
            raise ValueError(f"Unknown player: {winner}")

    def record_draw(self) -> None:
        self.red_draws += 1
        self.black_draws += 1

    def reset(self) -> None:
        self.red_wins = self.red_losses = self.red_draws = 0
        self.black_wins = self.black_losses = self.black_draws = 0
