import pytest

from game import Game


@pytest.fixture
def empty_board():
    return [[None for _ in range(8)] for _ in range(8)]


@pytest.fixture
def empty_game(empty_board):
    game = Game()
    game.board = empty_board
    return game
