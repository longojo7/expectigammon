"""
Name: Josh Longo and Kevin Shi
Filename: test_board.py
Description: This file contains the tests for the Board class, which represents the state of the backgammon board.
"""

# Imports
import pytest
import numpy as np
from src.board import Board

def test_board_length():
    """Test that the board is initialized with 28 points."""
    b = Board()
    assert len(b.board) == 28, "Board should have 28 points"

def test_board_zeroes():
    """Tests that the board initializes with all zeroes."""
    b = Board()
    assert np.all(b.board == 0), "Board should initialize with all zeroes"

def test_board_turn():
    """Tests that the board initializes with the correct turn."""
    b = Board()
    assert b.turn == 1, "Board should initialize with turn set to 1"

def test_new_game():
    """Tests the class method new_game to ensure it sets up the board correctly."""
    b = Board.new_game()
    assert isinstance(b, Board), "new_game should return an instance of Board"

def test_board_initialization():
    """Test that the board is initialized with the correct starting positions."""
    b = Board.new_game()
    expected_board = np.array([2, 0, 0, 0, 0, -5, 0, -3, 0, 0, 0, 5,
                               -5, 0, 0, 0, 3, 0, 5, 0, 0, 0, 0, -2,
                               0, 0, 0, 0])
    assert np.array_equal(b.board, expected_board), "Board should be initialized to the correct starting positions"

def test_board_copy():
    """Tests that the board_copy method creates a correct copy of the board."""
    b = Board.new_game()
    b_copy = b.board_copy()
    assert np.array_equal(b.board, b_copy.board), "Board copy should have the same board state"

def test_board_copy_turn():
    b = Board.new_game()
    b_copy = b.board_copy()
    assert b.turn == b_copy.turn, "Board copy should have the same turn"

def test_board_copy_change():
    """Tests that changing the original board does not affect the copy."""
    b = Board.new_game()
    b_copy = b.board_copy() 
    # change original board and check that copy does not change
    b.board[0] = 1
    assert b.board[0] != b_copy.board[0], "Board copy should be independent of original board"

def test_board_repr():
    """Tests the __repr__ method to make sure it prints correctly."""
    b = Board.new_game()
    assert repr(b) == "Points: [ 2  0  0  0  0 -5  0 -3  0  0  0  5 -5  0  0  0  3  0  5  0  0  0  0 -2], Bar: [0 0], Bear Off: [0 0]", "__repr__ should return the correct string representation of the board"
    
def test_board_str():
    """Tests the __str__ method to ensure it returns correct format."""
    b = Board.new_game()
    expected_str = "Board State:\n[-5  0  0  0  3  0] | [ 5  0  0  0  0 -2]\n[ 5  0  0  0 -3  0] | [-5  0  0  0  0  2]\nBar: P1=0 P2=0\nBear Off: P1=0 P2=0\n"
    assert str(b) == expected_str, "__str__ should return the correct string representation of the board"