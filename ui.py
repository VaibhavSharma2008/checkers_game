"""Pygame presentation and input-coordinate helpers."""

import pygame

from game import Game
from models import BLACK, BOARD_SIZE, RED, Position

WINDOW_SIZE = (1040, 760)
BOARD_ORIGIN = (32, 100)
SQUARE_SIZE = 76
BOARD_PIXELS = BOARD_SIZE * SQUARE_SIZE
BOARD_RECT = pygame.Rect(*BOARD_ORIGIN, BOARD_PIXELS, BOARD_PIXELS)
HUD_RECT = pygame.Rect(672, 100, 336, 608)
BACKGROUND = (22, 30, 35)
PANEL = (32, 43, 49)
TEXT = (242, 235, 219)
MUTED = (168, 183, 186)
LIGHT_SQUARE = (222, 210, 184)
DARK_SQUARE = (76, 110, 104)
RED_PIECE = (207, 76, 67)
BLACK_PIECE = (36, 44, 54)
ACCENT = (242, 193, 94)
BUTTONS = {
    "new_game": pygame.Rect(692, 564, 296, 38),
    "reset_match": pygame.Rect(692, 612, 296, 38),
    "exit": pygame.Rect(692, 660, 296, 38),
}
CONFIRM_RECT = pygame.Rect(320, 432, 184, 42)
CANCEL_RECT = pygame.Rect(536, 432, 184, 42)
CONFIRMATION_MESSAGES = {
    "new_game": ("Start a new game?", "The unfinished game will be abandoned. Match scores are kept."),
    "reset_match": ("Reset the match?", "All wins, losses and draws will be cleared. A fresh game will start."),
    "exit": ("Exit Checkers?", "The game will close. Match scores are kept only during this session."),
}


def create_window() -> pygame.Surface:
    pygame.display.set_caption("American Checkers")
    return pygame.display.set_mode(WINDOW_SIZE)


def create_fonts() -> dict[str, pygame.font.Font]:
    return {
        "title": pygame.font.Font(None, 38),
        "heading": pygame.font.Font(None, 28),
        "body": pygame.font.Font(None, 24),
        "small": pygame.font.Font(None, 21),
    }


def square_rect(position: Position) -> pygame.Rect:
    row, col = position
    return pygame.Rect(
        BOARD_ORIGIN[0] + col * SQUARE_SIZE,
        BOARD_ORIGIN[1] + row * SQUARE_SIZE,
        SQUARE_SIZE,
        SQUARE_SIZE,
    )


def draw_board(screen: pygame.Surface) -> None:
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            color = DARK_SQUARE if (row + col) % 2 else LIGHT_SQUARE
            pygame.draw.rect(screen, color, square_rect((row, col)))


def draw_pieces(screen: pygame.Surface, game: Game) -> None:
    for row, squares in enumerate(game.board):
        for col, piece in enumerate(squares):
            if piece is None:
                continue
            center = square_rect((row, col)).center
            x, y = center
            color = RED_PIECE if piece.color == RED else BLACK_PIECE
            pygame.draw.circle(screen, (25, 35, 37), (x, y + 3), 29)
            pygame.draw.circle(screen, color, center, 28)
            pygame.draw.circle(screen, (227, 170, 143) if piece.color == RED else MUTED,
                               center, 27, 2)
            pygame.draw.circle(screen, (255, 210, 169) if piece.color == RED else (102, 116, 130),
                               center, 21, 1)
            if piece.is_king:
                crown = [(x - 15, y + 7), (x - 18, y - 10), (x - 7, y - 3),
                         (x, y - 15), (x + 7, y - 3), (x + 18, y - 10),
                         (x + 15, y + 7)]
                pygame.draw.polygon(screen, ACCENT, crown)
                pygame.draw.line(screen, ACCENT, (x - 14, y + 12), (x + 14, y + 12), 3)
            if game.forced_jump_pos is not None and (row, col) != game.forced_jump_pos:
                shade = pygame.Surface((60, 60), pygame.SRCALPHA)
                pygame.draw.circle(shade, (*BACKGROUND, 150), (30, 30), 30)
                screen.blit(shade, (x - 30, y - 30))


def draw_highlights(screen: pygame.Surface, game: Game) -> None:
    if game.selected_pos is not None:
        pygame.draw.circle(screen, ACCENT, square_rect(game.selected_pos).center, 33, 3)
    for move in game.legal_moves:
        rect = square_rect(move.destination)
        if move.captured is not None:
            pygame.draw.rect(screen, ACCENT, rect.inflate(-8, -8), 4, border_radius=8)
            pygame.draw.circle(screen, ACCENT, rect.center, 10, 3)
        else:
            pygame.draw.circle(screen, ACCENT, rect.center, 8)


def draw_text(screen, text, font, color, position) -> None:
    screen.blit(font.render(text, True, color), position)


def draw_wrapped_text(screen, text, font, color, rect) -> None:
    line = ""
    y = rect.top
    for word in text.split():
        candidate = f"{line} {word}".strip()
        if line and font.size(candidate)[0] > rect.width:
            draw_text(screen, line, font, color, (rect.left, y))
            y += font.get_linesize()
            line = word
        else:
            line = candidate
    if line:
        draw_text(screen, line, font, color, (rect.left, y))


def draw_hud(screen: pygame.Surface, game: Game, fonts: dict) -> None:
    draw_text(screen, "AMERICAN CHECKERS", fonts["title"], TEXT, (32, 27))
    draw_text(screen, "LOCAL TWO-PLAYER  /  RED MOVES FIRST", fonts["small"], MUTED, (34, 67))
    pygame.draw.rect(screen, PANEL, HUD_RECT, border_radius=12)
    title = "Game complete" if game.is_game_over else f"{game.current_player}'s turn"
    draw_text(screen, title, fonts["heading"], ACCENT, (692, 120))
    draw_wrapped_text(screen, game.status_message, fonts["body"], TEXT,
                      pygame.Rect(692, 162, 296, 100))
    for player, y in ((RED, 278), (BLACK, 397)):
        score = game.scoreboard(player)
        pygame.draw.rect(screen, BACKGROUND, (688, y, 304, 105), border_radius=8)
        color = RED_PIECE if player == RED else MUTED
        pygame.draw.circle(screen, color, (706, y + 21), 6)
        draw_text(screen, player, fonts["heading"], TEXT, (721, y + 10))
        pieces = f"Pieces {score['regular']}    Kings {score['kings']}    Captures {score['captures']}"
        results = f"Wins {score['wins']}      Losses {score['losses']}      Draws {score['draws']}"
        draw_text(screen, pieces, fonts["small"], MUTED, (700, y + 44))
        draw_text(screen, results, fonts["small"], TEXT, (700, y + 74))
    draw_text(screen, f"No-progress turns: {game.no_progress_turns} / 80",
              fonts["small"], MUTED, (692, 525))
    draw_text(screen, "Select a checker, then a highlighted square.",
              fonts["small"], MUTED, (32, 725))


def draw_button(screen, rect, label, font, primary=False) -> None:
    color = ACCENT if primary else (54, 69, 77)
    pygame.draw.rect(screen, color, rect, border_radius=7)
    text = font.render(label, True, BACKGROUND if primary else TEXT)
    screen.blit(text, text.get_rect(center=rect.center))


def draw_controls(screen: pygame.Surface, fonts: dict) -> None:
    for action, label in (("new_game", "New Game"), ("reset_match", "Reset Match"),
                          ("exit", "Exit")):
        draw_button(screen, BUTTONS[action], label, fonts["body"], action == "new_game")


def get_button_action(mouse_position: tuple[int, int]) -> str | None:
    for action, rect in BUTTONS.items():
        if rect.collidepoint(mouse_position):
            return action
    return None


def pixel_to_board(mouse_position: tuple[int, int]) -> Position | None:
    if not BOARD_RECT.collidepoint(mouse_position):
        return None
    x, y = mouse_position
    return (y - BOARD_RECT.top) // SQUARE_SIZE, (x - BOARD_RECT.left) // SQUARE_SIZE


def draw_game_over(screen: pygame.Surface, game: Game, fonts: dict) -> None:
    shade = pygame.Surface(BOARD_RECT.size, pygame.SRCALPHA)
    shade.fill((10, 18, 22, 115))
    screen.blit(shade, BOARD_RECT)
    banner = pygame.Rect(BOARD_RECT.left + 44, BOARD_RECT.centery - 80, 520, 160)
    pygame.draw.rect(screen, PANEL, banner, border_radius=12)
    pygame.draw.rect(screen, ACCENT, banner, 2, border_radius=12)
    title = f"{game.winner} wins" if game.winner is not None else "Draw"
    text = fonts["title"].render(title, True, ACCENT)
    screen.blit(text, text.get_rect(center=(banner.centerx, banner.top + 38)))
    reason = fonts["body"].render(game.game_over_reason, True, TEXT)
    screen.blit(reason, reason.get_rect(center=(banner.centerx, banner.top + 83)))
    hint = fonts["small"].render("Choose New Game to play again", True, MUTED)
    screen.blit(hint, hint.get_rect(center=(banner.centerx, banner.top + 126)))


def draw_confirmation(screen: pygame.Surface, action: str, fonts: dict) -> None:
    shade = pygame.Surface(WINDOW_SIZE, pygame.SRCALPHA)
    shade.fill((7, 12, 16, 185))
    screen.blit(shade, (0, 0))
    panel = pygame.Rect(280, 260, 480, 240)
    pygame.draw.rect(screen, PANEL, panel, border_radius=14)
    pygame.draw.rect(screen, ACCENT, panel, 2, border_radius=14)
    title, message = CONFIRMATION_MESSAGES[action]
    draw_text(screen, title, fonts["title"], TEXT, (312, 289))
    draw_wrapped_text(screen, message, fonts["body"], MUTED,
                      pygame.Rect(312, 345, 416, 70))
    draw_button(screen, CONFIRM_RECT, "Confirm", fonts["body"], True)
    draw_button(screen, CANCEL_RECT, "Cancel", fonts["body"])


def get_confirmation_choice(mouse_position: tuple[int, int]) -> bool | None:
    if CONFIRM_RECT.collidepoint(mouse_position):
        return True
    if CANCEL_RECT.collidepoint(mouse_position):
        return False
    return None


def draw_game(screen: pygame.Surface, game: Game, fonts: dict,
              pending_action: str | None = None) -> None:
    screen.fill(BACKGROUND)
    draw_board(screen)
    draw_pieces(screen, game)
    draw_highlights(screen, game)
    draw_hud(screen, game, fonts)
    draw_controls(screen, fonts)
    if game.is_game_over:
        draw_game_over(screen, game, fonts)
    if pending_action is not None:
        draw_confirmation(screen, pending_action, fonts)
