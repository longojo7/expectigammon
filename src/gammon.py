"""
Name: Josh Longo and Kevin Shi
Filename: gammon.py
Description: The Gammon class contains our board game logic, where we implement the rules of backgammon.
"""

# Imports
import random
import numpy as np
from src.board import Board
from typing import Self

class Gammon:
    def __init__(self):
        """Initialize the backgammon game state."""
        self.state = Board.new_game()

    def copy(self) -> Self:
        """Make a copy of the current game state."""
        copy = Gammon()
        copy.state = self.state.board_copy()
        return copy

    def make_move(self, player, from_point, to_point, roll) -> bool:
        """Make a move for the given player from one point to another."""
        # check if move is valid
        valid_moves = self.valid_moves(player, roll)
        if not any(
            move[0] == from_point and move[1] == to_point
            for move in valid_moves
        ):
            print("Invalid move")
            return False
        
        # remove piece from source
        if from_point == 24 or from_point == 25:
            self.state.board[from_point] -= 1  # off the bar
        else:
            self.state.board[from_point] -= player

        # check if move hits a blot
        if to_point < 24 and self.state.board[to_point] == -player:
            # move opponent's piece to the bar
            if player == 1:
                # opponent's piece goes to their bar 
                self.state.board[25] += 1  
            else:
                # opponent's piece goes to their bar
                self.state.board[24] += 1 
            # move player's piece to the point 
            self.state.board[to_point] = player  

        else:
            # place the piece in the destination point
            if to_point == 26 or to_point == 27:
                # bear off the piece
                self.state.board[to_point] += 1
            else:
                self.state.board[to_point] += player
        return True

    def valid_moves(self, player, roll) -> list[tuple[int, int, int]]:
        """
        Return a list of valid moves for the given player based on the current board state and dice rolls.
        Moves are returned in a tuple (from_point, to_point, die_value).
        """
        if player == 1:
            # Check if the player has any pieces on the bar
            if self.state.board[24] > 0:
                # If so, they must move a piece from the bar first
                return [(24, die - 1, die) for die in roll if self.state.board[die - 1] >= -1]
            
            # Check if the player is currently bearing off pieces
            elif np.all(self.state.board[:18] <= 0) and self.state.board[24] == 0:
                valid_moves = []
                # have to track seen moves for doubles
                seen = set()
                for die in roll:
                    # check if there is a piece at the point corresponding to roll
                    if self.state.board[24 - die] > 0:
                        move = (24 - die, 26, die)
                        if move not in seen:
                            valid_moves.append(move)
                            seen.add(move)
                    else:
                        # No exact match so allow any piece to move forward or bear off with overshoot
                        home_pieces = [p for p in range(18, 24) if self.state.board[p] > 0]
                        if not home_pieces:
                            return valid_moves
                        for point in home_pieces:
                            to_point = point + die
                            if to_point < 24 and self.state.board[to_point] >= -1:
                                # Move forward within home board
                                move = (point, to_point, die)
                                if move not in seen:
                                    valid_moves.append(move)
                                    seen.add(move)
                                # break if forward move not found
                                break
                        else:
                            # If no forward move possible allow piece to overshoot and bear off
                            if home_pieces:
                                point = min(home_pieces)
                                move = (point, 26, die)
                                if move not in seen:
                                    valid_moves.append(move)
                                    seen.add(move)
                return valid_moves
            
            # Otherwise generate valid moves based on the current board state and dice rolls
            else:
                valid_moves = []
                # track moves already seen
                seen = set()
                for from_point in range(24):
                    # Check if there are pieces to move
                    if self.state.board[from_point] > 0:  
                        # check if move is valid for each die
                        for die in roll:
                            to_point = from_point + die
                            move = (from_point, to_point, die)
                            if to_point < 24 and self.state.board[to_point] >= -1 and move not in seen:  
                                valid_moves.append(move)
                                seen.add(move)
                return valid_moves
            
        elif player == -1:
            # Similar logic for player 2 but in opposite direction
            if self.state.board[25] > 0:
                return [(25, 24 - die, die) for die in roll if self.state.board[24 - die] <= 1]
            
            # Check if the player is currently bearing off pieces
            elif np.all(self.state.board[6:] >= 0) and self.state.board[25] == 0:
                valid_moves = []
                # have to track seen moves when doubles are rolled
                seen = set()
                for die in roll:
                    if self.state.board[die - 1] < 0:
                        move = (die - 1, 27, die)
                        if move not in seen:
                            valid_moves.append(move)
                            seen.add(move)
                    else:
                        # find the highest occupied point which is max point number for player 2
                        home_pieces = [p for p in range(5, -1, -1) if self.state.board[p] < 0]
                        # guard for when no pieces are left at home board return empty list gracefully
                        if not home_pieces:
                            return valid_moves
                        for point in home_pieces:
                            to_point = point - die
                            if to_point >= 0 and self.state.board[to_point] <= 1:
                                # Must move forward on board
                                move = (point, to_point, die)
                                if move not in seen:
                                    valid_moves.append(move)
                                    seen.add(move)
                                break
                        else:
                            if home_pieces:
                                point = max(home_pieces)
                                move = (point, 27, die)
                                if move not in seen:
                                    valid_moves.append(move)
                                    seen.add(move)
                return valid_moves
            else:
                valid_moves = []
                # track moves already seen
                seen = set()
                for from_point in range(24):
                    # Check if there are pieces to move
                    if self.state.board[from_point] < 0: 
                        # check if move is valid for each die 
                        for die in roll:
                            to_point = from_point - die
                            move = (from_point, to_point, die)
                            if to_point >= 0 and self.state.board[to_point] <= 1 and move not in seen:  
                                valid_moves.append(move)
                                seen.add(move)
                return valid_moves
        else:
            raise ValueError('Invalid player')

    def check_winner(self) -> int:
        """Check if there is a winner and returns the player number."""
        # return 1 if player 1 wins, return -1 if player 2 wins, return 0 if no winner yet
        if self.state.board[26] == 15:
            return 1
        elif self.state.board[27] == 15:
            return -1
        else:
            return 0

    # This might need to be in its in own class since it is more of a utility function but I will see how it goes
    def roll_dice(self) -> list[int]:
        """Simulate rolling two dice and return the results."""
        die1 = random.randint(1, 6)
        die2 = random.randint(1, 6)

        # If doubles, return four of the same die
        if die1 == die2:
            return [die1] * 4  
        return [die1, die2]
    
    def game_state(self) -> Board:
        """Return the current state of the game."""
        return self.state
    
    def game_over(self) -> bool:
        """Check if the game is over."""
        if self.check_winner() != 0:
            return True
        return False



def main():
    # Test the board construction
    game = Gammon()
    # print(game.board)

    # roll once to test
    roll = game.roll_dice()
    if roll[0] == roll[1]:
        print(f"You rolled doubles: {roll[0]} and {roll[1]}")
    else:
        print(f"You rolled: {roll[0]} and {roll[1]}")

    # make a move and print the board state
    valid_moves = game.valid_moves(game.state.turn, roll)
    print("Valid moves:", valid_moves)

    print("Current game state:")
    print(repr(game.game_state()))
    print(str(game.game_state()))

    # make the first valid move and print the new game state
    game.make_move(game.state.turn, valid_moves[0][0], valid_moves[0][1], roll)
    print("New game state:")
    print(repr(game.game_state()))

if __name__ == "__main__":
    main()
    