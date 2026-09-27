# American Checkers Desktop Game

A small local two-player American Checkers / English Draughts desktop game built with Python and Pygame.

## Project structure

- `main.py` starts the application and owns the event loop.
- `models.py` contains shared constants and data models.
- `logic.py` contains board calculations and Checkers rules.
- `game.py` coordinates the running game state.
- `ui.py` contains Pygame drawing and pixel-input helpers.
- `tests/` contains the Pytest test suite.

## Run

The prepared virtual environment in this workspace can run the game directly:

```powershell
.\.venv\Scripts\python.exe main.py
```

For a fresh copy, use Python 3.12 (the tested version):

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

Run these commands from the project folder. If `py` is unavailable, use your
Python interpreter's full path or `python` when it is on PATH. Activation is
optional; the commands above avoid PowerShell activation-policy issues.

The fixed game window is 1040 by 760 pixels. No image assets or internet
connection are needed after dependency installation.

## Play

Red starts at the bottom and moves first. Click a usable checker, then a marked
destination. Click the selected checker again to deselect it, or another usable
friendly checker to change selection. Invalid clicks are ignored.

- Regular pieces move one square diagonally forward and capture forward only.
- Captures are mandatory across the whole board. Gold outlines mark captures;
  small gold dots mark ordinary moves.
- After a jump, the same checker must continue while captures remain. Other
  pieces dim during the chain. Choose either route when jumps branch; the
  longest sequence is not required.
- Reaching the opposite back row crowns a King. Kings move one square and
  capture in all four diagonal directions; they do not fly.
- Promotion during a capture immediately ends the turn, even if the new King
  could capture backward.
- You win when your opponent has no pieces or no legal moves after your turn.
- A draw occurs after 80 completed player turns without capture or promotion.
  Each full jump chain is one turn. A decisive win takes precedence over a draw.

The HUD shows regular pieces and Kings separately, captures in the current game,
and wins/losses/draws for this application session.

## Controls

- **New Game** resets the board and current-game counters but preserves W/L/D.
  It asks for confirmation while a game is active, and starts immediately after
  a completed game. Abandoning a game records no result.
- **Reset Match** always asks for confirmation, clears W/L/D, and starts a fresh
  game with Red to move.
- **Exit**, including the window close button, asks for confirmation.
  Scores are not saved after the application closes.

Confirmations block board input. Cancel leaves the game unchanged.

## Tests

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

The five core test files cover board setup, movement, captures, Kings, results,
and controls without importing Pygame. `tests/test_ui.py` adds small event-loop
and rendering checks using SDL's dummy display, so tests do not open a window.
Rendered test frames are written to Pytest's temporary directory for inspection.

To run only the core tests:

```powershell
.\.venv\Scripts\python.exe -m pytest -q --ignore=tests/test_ui.py
```

## How the program works

`main.py` receives mouse events and asks `ui.py` to translate pixels to a board
square. `Game` asks `logic.py` for legal moves, applies a chosen move, then either
forces another jump or completes the turn. Completing a turn updates the draw
counter, checks wins before draws, records a result once, or switches players.
Finally, `ui.py` draws the resulting state.

The board is an 8x8 list of lists containing `Piece` objects or `None`. A piece's
location exists only in the board indices. `Move` stores a destination and the
optional square of one captured checker. `MatchStats` holds six session counters.
`Game` is the only substantial application class.

Only `main.py` and `ui.py` import Pygame. There are exactly five application
modules, with no AI, networking, save files, or extra frameworks.

## Verification

The implementation covers CHK-001 through CHK-060. Validation includes core
Pytest cases, mouse-event/confirmation integration checks, visual inspection of
ten rendered states, and a native Windows launch/render/confirmed-exit smoke test.
The visual check covers selection, capture branches, forced-piece dimming,
promotion crowns, both win reasons, draws, and all three confirmation prompts.
