"""
Name: Josh Longo and Kevin Shi
Filename: test_gammon.py
Description: This file contains the tests for the Gammon class, which contains the backgammon game logic.
"""

# Imports
import pytest
import numpy as np
from src.board import Board
from src.gammon import Gammon

def test_initial_board_state():
    """Test that the initial board state is set up correctly."""
    game = Gammon()
    expected_board = np.array([2, 0, 0, 0, 0, -5, 0, -3, 0, 0, 0, 5, -5, 0, 0, 0, 3, 0, 5, 0, 0, 0, 0, -2, 0, 0, 0, 0])
    assert np.array_equal(game.state.board, expected_board), "Initial board state is incorrect."

def test_roll_dice_range():
    """Test that roll_dice returns values between 1 and 6."""
    game = Gammon()
    for _ in range(100):
        roll = game.roll_dice()
        assert all(1 <= die <= 6 for die in roll), "Dice rolls should be between 1 and 6."

def test_roll_doubles():
    """Test that rolling doubles gives four moves."""
    game = Gammon()
    for _ in range(100):
        roll = game.roll_dice()
        if roll[0] == roll[1]:
            assert len(roll) == 4, "Rolling doubles should give four moves."
        else:
            assert len(roll) == 2, "Rolling non-doubles should give two moves."

def test_white_valid_move_bar():
    """Tests valid moves correctly produces list for white."""
    game = Gammon()
    # Set up where player 1 has a piece on the bar
    game.state.board[24] = 1 
    roll = [3, 4]
    valid_moves = game.valid_moves(1, roll)
    assert all(move[0] == 24 for move in valid_moves), "Player must move from the bar if they have pieces there."
    assert len(valid_moves) == 2, "There should be valid moves from the bar."
    assert (24, 2, 3) in valid_moves and (24, 3, 4) in valid_moves, "Moving from the bar to points 2 and 3 should be valid moves."

def test_black_valid_move_bar():
    """Tests valid moves correctly produces list for black."""
    game = Gammon()
    # Set up where player 2 has a piece on the bar
    game.state.board[25] = 1 
    roll = [3, 4]
    valid_moves = game.valid_moves(-1, roll)
    assert all(move[0] == 25 for move in valid_moves), "Player must move from the bar if they have pieces there."
    assert len(valid_moves) == 2, "There should be valid moves from the bar."
    assert (25, 21, 3) in valid_moves and (25, 20, 4) in valid_moves, "Moving from the bar to points 21 and 20 should be valid moves."

def test_bear_off_valid_white():
    """Tests valid moves correctly produces list for white bearing off."""
    game = Gammon()
    # Set up where player 1 is bearing off pieces
    game.state.board = np.zeros(28, dtype=int)
    game.state.board[22] = 1
    game.state.board[23] = 1
    roll = [1, 2]
    valid_moves = game.valid_moves(1, roll)
    assert (22, 26, 2) in valid_moves and (23, 26, 1) in valid_moves, "When all white pieces are in black home board, valid moves should include bearing off."
    assert len(valid_moves) == 2, "There should be valid moves for bearing off."
    assert all(move[1] == 26 for move in valid_moves), "Valid moves should be bearing off to point 26."

def test_bear_off_valid_black():
    """Tests valid moves correctly produces list for black bearing off."""
    game = Gammon()
    # Set up where player 2 is bearing off pieces
    game.state.board = np.zeros(28, dtype=int)
    game.state.board[0] = -1
    game.state.board[1] = -1
    roll = [1, 2]
    valid_moves = game.valid_moves(-1, roll)
    assert (0, 27, 1) in valid_moves and (1, 27, 2) in valid_moves, "When all black pieces are in white home board, valid moves should include bearing off."
    assert len(valid_moves) == 2, "There should be valid moves for bearing off."
    assert all(move[1] == 27 for move in valid_moves), "Valid moves should be bearing off to point 27."

def test_bear_off_valid_white_higher_roll():
    """Tests that white can bear off any piece that is lower than roll"""
    game = Gammon()
    game.state.board = np.zeros(28, dtype=int)
    game.state.board[23] = 1
    game.state.board[22] = 1
    roll = [4, 3]
    valid_moves = game.valid_moves(1, roll)
    assert ((23, 26, 4) in valid_moves and (23, 26, 3) in valid_moves and
            (22, 26, 4) in valid_moves and (22, 26, 3) in valid_moves), "White should be able to bear off from any lower point"

def test_bear_off_valid_black_higher_roll():
    """Tests that black can bear off any piece that is lower than roll"""
    game = Gammon()
    game.state.board = np.zeros(28, dtype=int)
    game.state.board[0] = -1
    game.state.board[1] = -1
    roll = [4, 3]
    valid_moves = game.valid_moves(-1, roll)
    assert ((0, 27, 4) in valid_moves and (0, 27, 3) in valid_moves and
            (1, 27, 4) in valid_moves and (1, 27, 3) in valid_moves), "Black should be able to bear off from any lower point"

def test_bear_off_valid_white_lower_roll():
    """Tests that white must move higher piece forward at home board when roll is lower"""
    game = Gammon()
    game.state.board = np.zeros(28, dtype=int)
    game.state.board[23] = 1
    game.state.board[18] = 1
    roll = [4, 3]
    valid_move = game.valid_moves(1, roll)
    assert (18, 22, 4) in valid_move and (18, 21, 3) in valid_move, "White should be forced to move higher piece forward"
    assert (23, 26, 4) not in valid_move and (23, 26, 3) not in valid_move, "White should not be able to bear off"

def test_bear_off_valid_black_lower_roll():
    """Tests that black must move higher piece forward at home board when roll is lower"""
    game = Gammon()
    game.state.board = np.zeros(28, dtype=int)
    game.state.board[0] = -1
    game.state.board[5] = -1
    roll = [4, 3]
    valid_move = game.valid_moves(-1, roll)
    assert (5, 1, 4) in valid_move and (5, 2, 3) in valid_move, "Black should be forced to move higher piece forward"
    assert (0, 27, 4) not in valid_move and (0, 27, 3) not in valid_move, "Black should not be able to bear off"

def test_valid_move():
    """Test that make_move returns True for a valid move."""
    game = Gammon()
    game.state.board = np.zeros(28, dtype=int)
    game.state.board[0] = 1 
    roll = [3, 4]
    result = game.make_move(1, 0, 3, roll)
    assert result is True, "make_move should return True for a valid move."

def test_invalid_move():
    """Test that make_move returns False for an invalid move."""
    game = Gammon()
    roll = [3, 4]
    result = game.make_move(1, 0, 5, roll)
    assert result is False, "make_move should return False for an invalid move."

def test_update_board():
    """Test that make_move correctly updates the board state for a valid move."""
    game = Gammon()
    roll = [3, 4]
    game.make_move(1, 0, 3, roll)
    assert game.state.board[0] == 1, "Source should now have only one piece (or one less)."
    assert game.state.board[3] == 1, "Destination point should have one piece after the move."

def test_hit_blot_white():
    """Test that make_move correctly handles hitting a blot for white (player 1)."""
    game = Gammon()
    # Set up a blot for player 1 at point 3
    game.state.board = np.zeros(28, dtype=int)
    game.state.board[0] = 1
    game.state.board[3] = -1 
    roll = [3, 4]
    game.make_move(1, 0, 3, roll)
    assert game.state.board[3] == 1, "Player 1 should now have a piece at point 3 after hitting the blot."
    assert game.state.board[0] == 0, "Player 1 should have moved the piece from point 0."
    assert game.state.board[25] == 1, "Player 2 should have a piece on the bar after being hit."

def test_hit_blot_black():
    """Test that make_move correctly handles hitting a blot for black (player 2)."""
    game = Gammon()
    game.state.board = np.zeros(28, dtype=int)
    game.state.board[23] = -1
    game.state.board[18] = 1 
    roll = [5, 1]
    game.make_move(-1, 23, 18, roll)
    assert game.state.board[18] == -1, "Player 2 should now have a piece at point 18 after hitting the blot."
    assert game.state.board[23] == 0, "Player 2 should have moved the piece from the point 23."
    assert game.state.board[24] == 1, "Player 1 should have a piece on the bar after being hit."

def test_hit_blot_from_bar():
    """Test that make_move correctly handles hitting a blot when moving from the bar."""
    game = Gammon()
    game.state.board = np.zeros(28, dtype=int)
    game.state.board[24] = 1 
    game.state.board[3] = -1 
    roll = [3, 4]
    game.make_move(1, 24, 3, roll)
    assert game.state.board[3] == 1, "Player 1 should now have a piece at point 3 after hitting the blot."
    assert game.state.board[24] == 0, "Player 1 should have moved the piece from the bar."
    assert game.state.board[25] == 1, "Player 2 should have a piece on the bar after being hit."

def test_bear_off_move_white():
    """Test that make_move correctly handles bearing off for white (player 1)."""
    game = Gammon()
    game.state.board = np.zeros(28, dtype=int)
    game.state.board[22] = 1
    roll = [1, 2]
    game.make_move(1, 22, 26, roll)
    assert game.state.board[22] == 0, "Player 1 should have moved the piece from point 22."
    assert game.state.board[26] == 1, "Player 1 should have a piece in the bear off area after bearing off."

def test_bear_off_move_black():
    """Test that make_move correctly handles bearing off for black (player 2)."""
    game = Gammon()
    game.state.board = np.zeros(28, dtype=int)
    game.state.board[0] = -1
    roll = [1, 2]
    game.make_move(-1, 0, 27, roll)
    assert game.state.board[0] == 0, "Player 2 should have moved the piece from point 0."
    assert game.state.board[27] == 1, "Player 2 should have a piece in the bear off area after bearing off."

def test_bear_off_with_higher_roll():
    """Test that when you roll a higher number than needed to bear off, the move still leads to bearing off."""
    game = Gammon()
    game.state.board = np.zeros(28, dtype=int)
    game.state.board[22] = 1
    roll = [5, 4]
    result = game.make_move(1, 22, 26, roll)
    assert result is True, "make_move should return True for a valid bear off move even if the roll is higher than needed."
    assert game.state.board[22] == 0, "Player 1 should have moved the piece from point 22."
    assert game.state.board[26] == 1, "Player 1 should have a piece in the bear off area after bearing off."

def test_invalid_bear_off_move():
    """Test that make_move returns False for trying to bear off with low roll."""
    game = Gammon()
    game.state.board = np.zeros(28, dtype=int)
    game.state.board[18] = 1
    roll = [5, 4]
    result = game.make_move(1, 18, 26, roll)
    assert result is False, "make_move should return False when you can't bear off with roll."

def test_invalid_bear_off_spot():
    """Test that make_move returns False for trying to bear off to the wrong home."""
    game = Gammon()
    game.state.board = np.zeros(28, dtype=int)
    game.state.board[22] = 1
    roll = [1, 2]
    result = game.make_move(1, 22, 27, roll)
    assert result is False, "make_move should return False when trying to bear off to the wrong home."

def test_move_from_bar_white():
    """Test that make_move correctly handles moving from the bar."""
    game = Gammon()
    game.state.board = np.zeros(28, dtype=int)
    game.state.board[24] = 1 
    game.state.board[5] = -2
    game.state.board[4] = -2
    game.state.board[2] = -2
    game.state.board[1] = -2
    game.state.board[0] = -2
    roll = [3, 4]
    result = game.make_move(1, 24, 3, roll)
    assert result is True, "make_move should return True for a valid move from the bar."
    assert game.state.board[24] == 0, "Player 1 should have moved the piece from the bar."
    assert game.state.board[3] == 1, "Player 1 should have a piece at point 3 after moving from the bar."

def test_move_from_bar_black():
    """Test that make_move correctly handles moving from the bar for black."""
    game = Gammon()
    game.state.board = np.zeros(28, dtype=int)
    game.state.board[25] = 1 
    game.state.board[18] = 2
    game.state.board[19] = 2
    game.state.board[20] = 2
    game.state.board[22] = 2
    game.state.board[23] = 2
    roll = [3, 4]
    result = game.make_move(-1, 25, 21, roll)
    assert result is True, "make_move should return True for a valid move from the bar."
    assert game.state.board[25] == 0, "Player 2 should have moved the piece from the bar."
    assert game.state.board[21] == -1, "Player 2 should have a piece at point 21 after moving from the bar."

def test_move_from_bar_blocked():
    """Test that make_move returns False when trying to move from the bar to a blocked point."""
    game = Gammon()
    game.state.board = np.zeros(28, dtype=int)
    game.state.board[24] = 1 
    game.state.board[2] = -2
    game.state.board[3] = -2
    game.state.board[4] = -2
    roll = [3, 4]
    result = game.make_move(1, 24, 3, roll)
    assert result is False, "make_move should return False when trying to move from the bar to a blocked point."

def test_no_winner():
    """Test that check_winner returns 0 when there is no winner."""
    game = Gammon()
    assert game.check_winner() == 0, "check_winner should return 0 when there is no winner."
    assert game.game_over() is False, "game_over should return False when there is no winner."

def test_winner_white():
    """Test that check_winner returns 1 when white has borne off all pieces."""
    game = Gammon()
    game.state.board = np.zeros(28, dtype=int)
    game.state.board[26] = 15
    assert game.check_winner() == 1
    assert game.game_over() is True, "game_over should return True when white has won."

def test_winner_black():
    """Test that check_winner returns -1 when black has borne off all pieces."""
    game = Gammon()
    game.state.board = np.zeros(28, dtype=int)
    game.state.board[27] = 15 
    assert game.check_winner() == -1
    assert game.game_over() is True, "game_over should return True when black has won."

def test_white_move_wins():
    """Test that a move where white wins is handled correctly."""
    game = Gammon()
    game.state.board = np.zeros(28, dtype=int)
    game.state.board[22] = 1
    game.state.board[26] = 14
    roll = [1, 2]
    game.make_move(1, 22, 26, roll)
    assert game.check_winner() == 1, "check_winner should return 1 when white wins after a move."
    assert game.game_over() is True, "game_over should return True when white wins after a move."

def test_move_from_bar_to_bear_off():
    """Test that make_move doesn't let you bear off from bar."""
    game = Gammon()
    game.state.board = np.zeros(28, dtype=int)
    game.state.board[26] = 0
    game.state.board[24] = 1 
    game.state.board[22] = 1
    game.state.board[23] = 1
    roll = [1, 2]
    result = game.make_move(1, 24, 26, roll)
    assert result is False, "make_move should return False when trying to bear off from the bar."
    assert game.state.board[24] == 1, "Player 1 should have moved the piece from the bar."
    assert game.state.board[26] == 0, "Player 1 should not have a piece in the bear off area after failing to move from the bar to bearing off."

def test_move_from_bear_off():
    """Test that make_move doesn't let you move from the bear off area."""
    game = Gammon()
    game.state.board = np.zeros(28, dtype=int)
    game.state.board[26] = 1 
    roll = [1, 2]
    result = game.make_move(1, 26, 22, roll)
    assert result is False, "make_move should return False when trying to move from the bear off area."
    assert game.state.board[26] == 1, "Player 1 should still have the piece in the bear off area after failing to move from there."
