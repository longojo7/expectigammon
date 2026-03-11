"""
Name: gammon.py
This is where our board game logic will go. We will implement the rules of backgammon here, 
and create a class to represent the game state. This class will have methods for making moves, 
checking for valid moves, and determining the winner of the game.
"""

# Imports
import random
import numpy as np

class Gammon:
    def __init__(self):
        """Initialize the backgammon game state."""
        self.board = self.initialize_board()

    def initialize_board(self):
        """Set up the initial board state for backgammon."""
        board = np.zeros(24, dtype=int)
        # Place the pieces where white (player 1) is positive and black (player 2) is negative
        board[0] = 2 
        board[5] = -5
        board[7] = -3
        board[11] = 5
        board[12] = -5
        board[16] = 3
        board[18] = 5
        board[23] = -2
        return board
    
    def make_move(self, player, from_point, to_point):
        """Make a move for the given player from one point to another."""
        # This method will contain the logic for moving pieces on the board
        pass


def main():
    # Test the board construction
    game = Gammon()
    print(game.board)

if __name__ == "__main__":
    main()
    