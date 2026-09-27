# American Checkers Desktop Game

A small local two-player American Checkers / English Draughts desktop game built with Python and Pygame.

## Project structure

- `main.py` starts the application and owns the event loop.
- `models.py` contains shared constants and data models.
- `logic.py` contains board calculations and Checkers rules.
- `game.py` coordinates the running game state.
- `ui.py` contains Pygame drawing and pixel-input helpers.
- `tests/` contains the Pytest test suite.

## Setup

Create and activate a Python virtual environment, then install the dependencies:

```powershell
python -m pip install -r requirements.txt
```

The project skeleton is currently in place. Gameplay will be implemented story by story.
