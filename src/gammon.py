"""
Name: Josh Longo and Kevin Shi
Filename: gammon.py
Description: The Gammon class contains our board game logic, where we implement the rules of backgammon.
"""

# Imports
import random
import numpy as np
from board import Board

class Gammon:
    def __init__(self):
        """Initialize the backgammon game state."""
        self.state = Board.new_game()
    
    def make_move(self, player, from_point, to_point, roll):
        """Make a move for the given player from one point to another."""
        # check if move is valid
        if (from_point, to_point) not in self.valid_moves(player, roll):
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

        # place the piece in the destination point
        if to_point == 26 or to_point == 27:
            # bear off the piece
            self.state.board[to_point] += 1
        else:
            self.state.board[to_point] += player
        return True

    def valid_moves(self, player, roll):
        """Return a list of valid moves for the given player based on the current board state and dice rolls."""
        if player == 1:
            # Check if the player has any pieces on the bar
            if self.state.board[24] > 0:
                # If so, they must move a piece from the bar first
                return [(24, die - 1) for die in roll if self.state.board[die - 1] >= -1]
            
            # Check if the player is currently bearing off pieces
            elif np.all(self.state.board[6:25] <= 0):
                valid_moves = []
                for die in roll:
                    if self.state.board[die - 1] > 0:
                        valid_moves.append((die - 1, 26))
                    else:
                        for point in range(die - 1, -1, -1):
                            if self.state.board[point] > 0:
                                valid_moves.append((point, 26))
                                break
                return valid_moves
            
            # Otherwise generate valid moves based on the current board state and dice rolls
            else:
                valid_moves = []
                # track moves already seen
                seen = set()
                for from_point in range(24):
                    # Check if there are pieces to move
                    if self.state.board[from_point] > 0:  
                        if len(roll) == 4:
                            die = roll[0]
                            for num in range(1, 5):
                                to_point = from_point + num * die
                                prev_point = from_point + (num - 1) * die
                                move = (from_point, to_point)
                                if (to_point < 24 and self.state.board[prev_point] >= -1 and 
                                    self.state.board[to_point] >= -1 and move not in seen):
                                    valid_moves.append(move)
                                    seen.add(move)
                                else:
                                    break
                        else:
                            for die in roll:
                                to_point = from_point + die
                                move = (from_point, to_point)
                                if to_point < 24 and self.state.board[to_point] >= -1 and move not in seen:  
                                    valid_moves.append(move)
                                    seen.add(move)
                            # also check sum of both dice 
                            first_point = from_point + roll[0]
                            to_point = from_point + sum(roll)
                            move = (from_point, to_point)
                            if (to_point < 24 and self.state.board[first_point] >= -1 
                            and self.state.board[to_point] >= -1 and move not in seen):
                                valid_moves.append(move)
                                seen.add(move)
                return valid_moves
            
        elif player == -1:
            # Similar logic for player 2 but in opposite direction
            if self.state.board[25] > 0:
                return [(25, 24 - die) for die in roll if self.state.board[24 - die] <= 1]
            
            # Check if the player is currently bearing off pieces
            elif np.all(self.state.board[:18] >= 0) and self.state.board[25] == 0:
                valid_moves = []
                for die in roll:
                    if self.state.board[24 - die] < 0:
                        valid_moves.append((24 - die, 27))
                    else:
                        for point in range(24 - die, 24, 1):
                            if self.state.board[point] < 0:
                                valid_moves.append((point, 27))
                                break
                return valid_moves
            else:
                valid_moves = []
                # track moves already seen
                seen = set()
                for from_point in range(24):
                    # Check if there are pieces to move
                    if self.state.board[from_point] < 0:  
                        if len(roll) == 4:
                            die = roll[0]
                            for num in range(1, 5):
                                to_point = from_point - num * die
                                prev_point = from_point - (num - 1) * die
                                move = (from_point, to_point)
                                if (to_point >= 0 and self.state.board[prev_point] <= 1 and 
                                    self.state.board[to_point] <= 1 and move not in seen):
                                    valid_moves.append(move)
                                    seen.add(move)
                                else:
                                    break
                        else:
                            for die in roll:
                                to_point = from_point - die
                                move = (from_point, to_point)
                                if to_point >= 0 and self.state.board[to_point] <= 1 and move not in seen:  
                                    valid_moves.append(move)
                                    seen.add(move)
                            # also check sum of both dice 
                            first_point = from_point - roll[0]
                            to_point = from_point - sum(roll)
                            move = (from_point, to_point)
                            if (to_point >= 0 and self.state.board[first_point] <= 1 
                            and self.state.board[to_point] <= 1 and move not in seen):
                                valid_moves.append(move)
                                seen.add(move)
                return valid_moves

    def can_move(self, player, from_point, to_point):
        """Return a list of valid moves for the given player."""
        # Check to see if the move is outside the bounds of the board
        if from_point < 0 or from_point >= 24 or to_point < 0 or to_point >= 24:
            print("Invalid move: Points must be between 1 and 24.")
            return False

    def check_winner(self):
        """Check if there is a winner and returns the player number."""
        # return 1 if player 1 wins, return -1 if player 2 wins, return 0 if no winner yet
        if self.state.board[26] == 15:
            return 1
        elif self.state.board[27] == -15:
            return -1
        else:
            return 0

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
        return self.state
    
    def game_over(self):
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
    print(f"You got a {roll[0]} and a {roll[0]}")

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
    