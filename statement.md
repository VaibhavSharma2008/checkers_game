# American Checkers Desktop Game

## Problem statement

Traditional checkers is easy to learn but enforcing every rule consistently can be difficult during casual play. Players may overlook mandatory captures, multi-jump continuations, promotion rules, end-game conditions, or draw limits. This project provides a local desktop implementation that validates moves automatically and presents the game state clearly.

## Scope

The project implements American Checkers for two players sharing one Windows computer. It includes the standard 8 x 8 board, legal diagonal movement, mandatory captures, chained jumps, king promotion, win and draw detection, session statistics, confirmation dialogs, and automated tests. The current scope excludes computer opponents, networking, saved games, user accounts, and persistent storage.

## Target users

- Students learning Python, game logic, event-driven programming, and automated testing
- Two players who want a lightweight offline checkers game
- Instructors evaluating modular software design and rule validation

## High-level features

- Local two-player checkers gameplay with mouse input
- Automatic enforcement of moves, captures, chained jumps, and promotion
- Clear visual highlighting for selectable moves and required captures
- Win, loss, and 80-turn draw detection
- In-session scoreboard and safe new-game, reset, and exit controls
- Pytest coverage for rules, game flow, controls, and rendering
