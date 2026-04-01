"""
Name: Josh Longo and Kevin Shi
Filename: expectigammon.py
Description: This file contains the expectiminimax algorithm using the game representation in gammon.py.
"""
from numpy.f2py.crackfortran import expectbegin

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

    def get_moveset(self, game: Gammon, rolls, player):
        results = []

        def recurse(current_game, remaining_rolls, path):
            valid_moves = current_game.valid_moves(player, remaining_rolls)

            # Base case: no rolls left or no valid moves
            if not remaining_rolls or not valid_moves:
                if path:
                    results.append(tuple(path))
                return

            for move in valid_moves:
                game_copy = current_game.copy()
                rolls_copy = remaining_rolls.copy()
                game_copy.make_move(player, move[0], move[1], rolls_copy)
                rolls_copy.remove(move[2])
                recurse(game_copy, rolls_copy, path + [move])

        recurse(game, rolls, [])
        return set(results)

    def apply_moves(self, game: Gammon, moveset, rolls, player):
        for move in moveset:
            game.make_move(player, move[0], move[1], rolls)

    def make_move(self, game: Gammon):
        rolls = game.roll_dice()
        moveset = self.get_moveset(game, rolls, self.player_number)
        # Pass turn if no valid moves
        if not moveset:
            pass
        # Keep track of which full moveset gives best expectation
        best = -float('inf')
        best_moves = None
        for moves in moveset:
            game_copy = game.copy()
            self.apply_moves(game_copy, moves, rolls, self.player_number)
            move_expectation = self.expectiminimax(game_copy)
            if move_expectation > best:
                best = move_expectation
                best_moves = moves

        # If all moves guarantee loss, choose any one
        if best_moves is None:
            best_moves = moveset.pop()

        # Run game.make_move()
        self.apply_moves(game, moveset, rolls, self.player_number)

    def expectiminimax(self, game: Gammon, depth=3, is_max_turn = False):
        if depth == 0 or game.game_over():
            return self.h(game)

        if is_max_turn:
            best_value = -float("inf")

            for possible_roll in self.roll_outcomes:
                game_copy = game.copy()
                expected_value = 0

                moveset = self.get_moveset(game_copy, possible_roll, self.player_number)
                for moves in moveset:
                    self.apply_moves(game_copy, moves, possible_roll, self.player_number)
                    expected_value += self.expectiminimax(game_copy, depth - 1, not is_max_turn)

                best_value = max(best_value, expected_value / len(self.roll_outcomes))

            return best_value

        else:
            best_value = float("inf")

            for possible_roll in self.roll_outcomes:
                game_copy = game.copy()
                expected_value = 0

                moveset = self.get_moveset(game_copy, possible_roll, -self.player_number)
                for moves in moveset:
                    self.apply_moves(game_copy, moves, possible_roll, -self.player_number)
                    expected_value += self.expectiminimax(game_copy, depth - 1, not is_max_turn)

                best_value = min(best_value, expected_value / len(self.roll_outcomes))

            return best_value

    def h(self, game: Gammon):
        if game.game_over():
            return float("inf") * self.player_number

        heuristic = 0

        state = game.state.board
        # Total distance to travel
        for i in range(0, 24):
            if state[i] > 0:
                heuristic -= (23 - i) * state[i]
            else:
                heuristic -= (i + 1) * state[i]

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