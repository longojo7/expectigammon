"""
Name: Josh Longo and Kevin Shi
Filename: board.py
Description: This file will contain the Board class, which represents the state of the backgammon board.
"""

# Imports
import numpy as np

# Board class to represent the state of the backgammon board
class Board:

    def __init__(self):
        """Initialize the backgammon board state."""
        # 24 points on the board, use dicts for bar and bear off to track pieces on the bar and bear off
        self.points = np.zeros(24, dtype=int)
        self.bar = {1: 0, -1: 0} 
        self.bear_off = {1: 0, -1: 0}
        self.turn = 1 

    @classmethod
    def new_game(cls):
        """Create a board with in the initial state of a new game"""
        board = cls()
        board.setup_pieces()
        return board

    def setup_pieces(self):
        """Set up the initial board state for backgammon."""
        # Place the pieces where white (player 1) is positive and black (player 2) is negative
        self.points[0] = 2 
        self.points[5] = -5
        self.points[7] = -3
        self.points[11] = 5
        self.points[12] = -5
        self.points[16] = 3
        self.points[18] = 5
        self.points[23] = -2

    def __copy__(self):
        """Creates a copy of the current board."""
        board_copy = Board()
        board_copy.points = np.copy(self.points)
        board_copy.bar = self.bar.copy()
        board_copy.bear_off = self.bear_off.copy()
        board_copy.turn = self.turn
        return board_copy
    
    def __repr__(self):
        """Display the current state of the board."""
        return f"Points: {self.points}, Bar: {self.bar}, Bear Off: {self.bear_off}"
    
    def __str__(self):
        """Display the current state of the board in a more readable format."""
        board_str = "Board State:\n"
        for i in range(24):
            board_str += f"Point {i+1}: {self.points[i]}\n"
        board_str += f"Bar: {self.bar}\n"
        board_str += f"Bear Off: {self.bear_off}\n"
        return board_str
    
def main():

    # This is just a placeholder for testing the Board class
    board = Board.new_game()
    
    # print the board with repr and str to see the difference
    print(repr(board))
    print(board)

if __name__ == "__main__":
    main()