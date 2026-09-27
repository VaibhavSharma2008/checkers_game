"""Application entry point for the American Checkers game."""

import pygame

from game import Game
import ui


def handle_event(game: Game, event: pygame.event.Event,
                 pending_action: str | None) -> tuple[bool, str | None]:
    """Return (keep_running, pending_confirmation) after one event."""
    if event.type == pygame.QUIT:
        return True, "exit"
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        if pending_action is not None:
            choice = ui.get_confirmation_choice(event.pos)
            if choice is False:
                return True, None
            if choice is True:
                if pending_action == "new_game":
                    game.new_game()
                elif pending_action == "reset_match":
                    game.reset_match()
                elif pending_action == "exit":
                    return False, None
                return True, None
            return True, pending_action
        action = ui.get_button_action(event.pos)
        if action == "new_game":
            if game.is_game_over:
                game.new_game()
                return True, None
            return True, action
        if action in ("reset_match", "exit"):
            return True, action
        position = ui.pixel_to_board(event.pos)
        if position is not None and not game.is_game_over:
            game.handle_square_click(position)
    return True, pending_action


def main() -> None:
    pygame.init()
    try:
        screen = ui.create_window()
        fonts = ui.create_fonts()
        game = Game()
        clock = pygame.time.Clock()
        running = True
        pending_action = None
        while running:
            for event in pygame.event.get():
                running, pending_action = handle_event(game, event, pending_action)
                if not running:
                    break
            if running:
                ui.draw_game(screen, game, fonts, pending_action)
                pygame.display.flip()
                clock.tick(60)
    finally:
        pygame.quit()


if __name__ == "__main__":
    main()
