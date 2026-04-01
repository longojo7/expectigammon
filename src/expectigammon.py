"""
Name: Josh Longo and Kevin Shi
Filename: expectigammon.py
Description: This file contains the expectiminimax algorithm using the game representation in gammon.py.
"""

# Imports
from board import Board
from gammon import Gammon
import numpy as np




class Player:
    def __init__(self, player_number):
        self.player_number = player_number
        self.roll_outcomes = []
        for i in range(1, 7):
            for j in range(1, 7):
                roll = [i, j]
                self.roll_outcomes.append(roll if i != j else roll * 2)

    def make_move(self, game: Gammon):
        rolls = game.roll_dice()
        valid_moves = game.valid_moves(self.player_number, rolls)
        # Create potential full movesets
        # Run expectiminimax
        # Keep track of which full moveset gives best expectation
        # Run game.make_move() on it

    def expectiminimax(self, game: Gammon, depth=3, is_max_turn = True):
        if depth == 0 or game.game_over():
            return self.h(game)


        game_copy = game.copy()
        if is_max_turn:
            best_value = -float("inf")

            for possible_roll in self.roll_outcomes:
                expected_value = 0

                roll = possible_roll.copy()
                valid_moves = game_copy.valid_moves(self.player_number, roll)
                # Need to handle making both moves
                for move in valid_moves:
                    game_copy.make_move(self.player_number, move[0], move[1], roll)

                    expected_value += self.expectiminimax(game_copy, depth - 1, not is_max_turn)

                best_value = max(best_value, expected_value/36)

            return best_value

        else:
            # Duplicate above code but for min
            best_value = float("inf")
            for possible_roll in self.roll_outcomes:
                expected_value = 0
                roll = possible_roll.copy()
                valid_moves = game_copy.valid_moves(-self.player_number, roll)
                for move in valid_moves:
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