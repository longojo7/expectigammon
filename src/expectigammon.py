"""
Name: Josh Longo and Kevin Shi
Filename: expecitgammon.py
Description: This file contains the expectiminimax algorithm using the game representation in gammon.py.
"""

# Imports
from gammon import Gammon
import numpy as np

from src.board import Board


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

    def expectiminimax(self, game: Gammon, depth=3, is_max_turn = True):
        if depth == 0 or game.game_over():
            return self.h(game)


        board_copy = game.state.board_copy()
        if is_max_turn:
            best_value = -float("inf")

            for move in get_moves(game):
                # apply potential move

                expected_value = 0
                for next_roll in self.roll_outcomes:
                    new_copy = board_copy.copy()
                    # apply new move
                    expected_value += self.expectiminimax(new_copy, depth - 1, not is_max_turn)

                best_value = max(best_value, expected_value/36)

            return best_value

        else:
            # Duplicate above code but for min
            pass

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