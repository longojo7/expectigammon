"""
Name: Josh Longo and Kevin Shi
Filename: expectigammon.py
Description: This file contains the expectiminimax algorithm using the game representation in gammon.py.
"""

# Imports
from src.board import Board
from src.gammon import Gammon
import numpy as np

class Player:
    def __init__(self, player_number):
        self.player_number = player_number
        self.roll_outcomes = []
        # To demonstrate algorithm
        self.current_roll = None
        self.current_move = None
        self.current_score = None
        for i in range(1, 7):
            for j in range(1, 7):
                roll = [i, j]
                self.roll_outcomes.append(roll if i != j else roll * 2)

    def take_turn(self, game: Gammon):
        rolls = game.roll_dice()
        self.current_roll = rolls
        # Create potential full movesets
        # Run expectiminimax
        # Keep track of which full moveset gives best expectation
        # Run game.make_move() on it
        best_score = -float("inf")
        best_move = None

        # Get valid moves for the current roll
        valid_moves = game.valid_moves(self.player_number, rolls)

        # No moves available
        if not valid_moves:
            return 

        # Evaluate each move using expectiminimax and keep track of the best one
        for move in valid_moves:
            game_copy = game.copy()
            game_copy.make_move(self.player_number, move[0], move[1], rolls)
            score = self.expectiminimax(game_copy, depth=1, is_max_turn=False)
            if score > best_score:
                best_score = score
                best_move = move

        self.current_move = best_move
        self.current_score = best_score
        # Make the best move found
        if best_move:
            game.make_move(self.player_number, best_move[0], best_move[1], rolls)

    def expectiminimax(self, game: Gammon, depth=3, is_max_turn = True):
        # if depth is 0 or game is over return heuristic value of the game state
        if depth == 0 or game.game_over():
            return self.h(game)

        if is_max_turn:
            best_value = -float("inf")

            for possible_roll in self.roll_outcomes:
                roll = possible_roll.copy()
                valid_moves = game.valid_moves(self.player_number, roll)

                # If no move is available skip the turn and recurse
                if not valid_moves:
                    val = self.expectiminimax(game, depth - 1, not is_max_turn)
                    best_value = max(best_value, val)
                    continue

                expected_value = 0
                # Average score across all moves for this roll (chance node)
                for move in valid_moves:
                    # get a fresh copy per move
                    game_copy = game.copy()
                    game_copy.make_move(self.player_number, move[0], move[1], roll)
                    expected_value += self.expectiminimax(game_copy, depth - 1, not is_max_turn)
                
                # Take the best expected value across all possible rolls
                best_value = max(best_value, expected_value/36)

            return best_value

        else:
            # Duplicate above code but for min so minimize over opponents moves
            best_value = float("inf")

            for possible_roll in self.roll_outcomes:
                roll = possible_roll.copy()
                valid_moves = game.valid_moves(-self.player_number, roll)

                if not valid_moves:
                    val = self.expectiminimax(game, depth - 1, not is_max_turn)
                    best_value = min(best_value, val)
                    continue

                expected_value = 0
                for move in valid_moves:
                    game_copy = game.copy()
                    game_copy.make_move(-self.player_number, move[0], move[1], roll)
                    expected_value += self.expectiminimax(game_copy, depth - 1, not is_max_turn)

                best_value = min(best_value, expected_value / 36)
            return best_value

    def h(self, game: Gammon):
        if game.game_over():
            return float("inf") * self.player_number

        heuristic = 0

        state = game.state.board
        # Total distance to travel
        for i in range(0, 24):
            if state[i] > 0:
                heuristic += (23 - i) * state[i]
            else:
                heuristic += (i + 1) * state[i]

        # Penalty for blots
        blot_penalty = 2    # Modify based on whether the blot is in danger?
        for i in range(0, 24):
            if state[i] == 1:
                heuristic -= blot_penalty
            elif state[i] == -1:
                heuristic += blot_penalty

        # Heavy penalty for pieces on the bar
        bar_penalty = 5     # Increase based on opponent's points at home?
        heuristic -= bar_penalty * state[24]
        heuristic += bar_penalty * state[25]

        return heuristic * self.player_number

def main():
    # Run one move of expectiminimax and print the board state before and after
    game = Gammon()
    player1 = Player(1)
    player2 = Player(-1)

    # the initial board state
    print("Initial board state:")
    print(game.state)

    print("\nEvaluating position at depth=1...")
    score = player1.expectiminimax(game, depth=1)
    print(f"Position score for player 1: {score:.4f}")

    print("\nPlayer 1 taking turn...")
    player1.take_turn(game)

    print(f"Rolled:     {player1.current_roll}")
    print(f"Best move:  {player1.current_move}")
    print(f"Move score: {player1.current_score:.4f}")

    print("\nBoard state after player 1's move:")
    print(game.state)

if __name__ == "__main__":
    main()