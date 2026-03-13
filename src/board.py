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
        self.board = np.zeros(28, dtype=int)
        self.turn = 1 

    @classmethod
    def new_game(cls):
        """Create a board with in the initial state of a new game"""
        board = cls()
        board.setup_board()
        return board

    def setup_board(self):
        """Set up the initial board state for backgammon."""
        # Place the pieces where white (player 1) is positive and black (player 2) is negative
        self.board[0] = 2 
        self.board[5] = -5
        self.board[7] = -3
        self.board[11] = 5
        self.board[12] = -5
        self.board[16] = 3
        self.board[18] = 5
        self.board[23] = -2

    def board_copy(self):
        """Creates a copy of the current board."""
        board_copy = Board()
        board_copy.board = np.copy(self.board)
        board_copy.turn = self.turn
        return board_copy
    
    def __repr__(self):
        """Display the current state of the board."""
        return f"Points: {self.board[:24]}, Bar: {self.board[24:26]}, Bear Off: {self.board[26:28]}"
    
    def __str__(self):
        """Display the current state of the board in a more readable format."""
        board_str = "Board State:\n"
        for i in range(24):
            board_str += f"Point {i+1}: {self.board[i]}\n"
        board_str += f"Bar: {self.board[24:26]}\n"
        board_str += f"Bear Off: {self.board[26:28]}\n"
        return board_str
    
def main():

    # This is just a placeholder for testing the Board class
    board = Board.new_game()
    
    # print the board with repr and str to see the difference
    print(repr(board) + "\n")
    print(board)

    # Testing a copy
    new_board = board.board_copy()
    print("board and new_board are copies:", np.array_equal(board.board, new_board.board))

if __name__ == "__main__":
    main()