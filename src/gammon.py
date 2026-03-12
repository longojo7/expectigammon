"""
Name: Josh Longo and Kevin Shi
Filename: gammon.py
Description: The Gammon class contains our board game logic, where we implement the rules of backgammon.
"""

# Imports
import random
import numpy as np
from src.board import Board

class Gammon:
    def __init__(self):
        """Initialize the backgammon game state."""
        self.board = Board()
    
    def make_move(self, player, from_point, to_point):
        """Make a move for the given player from one point to another."""
        # This logic is not correct as is but a placeholder when I think of how to implement
        if player == 1:
            # Have to check if player is currently taking pieces of the board
            # Have to check if a piece is currently on the bar and if so, they have to move that piece first
            # Have to check if the move is valid (e.g., not moving to a point occupied by two or more opponent pieces)
            # Have to check if the move is legal based on the dice rolls
            self.board.points[from_point] -= player
            self.board.points[to_point] += player
        else:
            self.board.points[from_point] += player
            self.board.points[to_point] -= player

    def can_move(self, player):
        """Return a list of valid moves for the given player."""
        pass

    def check_winner(self):
        """Check if there is a winner and return the winner's player number."""
        pass

    # This might need to be in its in own class since it is more of a utility function but I will see how it goes
    def roll_dice(self):
        """Simulate rolling two dice and return the results."""
        die1 = random.randint(1, 6)
        die2 = random.randint(1, 6)

        # If doubles, return four of the same die
        if die1 == die2:
            return [die1] * 4  
        return [die1, die2]
    
    def game_state(self):
        """Return the current state of the game."""
        return self.board
    
    def game_over(self):
        """Check if the game is over."""
        pass



def main():
    # Test the board construction
    game = Gammon()
    # print(game.board)

    print(game.roll_dice())
    print(game.roll_dice())
    print(game.roll_dice())
    print(game.roll_dice())
    print(game.roll_dice())
    print(game.roll_dice())

if __name__ == "__main__":
    main()
    