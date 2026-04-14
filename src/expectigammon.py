"""
Name: Josh Longo and Kevin Shi
Filename: expectigammon.py
Description: This file contains the expectiminimax algorithm using the game representation in gammon.py.
"""

# Imports
from src.board import Board
from src.gammon import Gammon
import numpy as np
import time

class Player:
    def __init__(self, player_number):
        self.player_number = player_number
        self.roll_outcomes = []
        # To demonstrate algorithm
        self.current_roll = None
        self.current_move = None
        self.current_score = None
        # Generate all 21 possible rolls
        for i in range(1, 7):
            for j in range(i, 7):
                roll = [i, j]
                self.roll_outcomes.append(roll if i != j else roll * 2)
        # for measuring nodes visited and pruned
        self.nodes_visited = 0
        self.nodes_pruned = 0
        self.score_move_call = 0
        # add a transposition table to store already evaluated board states (board state + depth + whose turn it is)
        self.transposition_table = {}

    def get_moveset(self, game: Gammon, rolls, player, cap=None):
        results = {}

        def recurse(current_game, remaining_rolls, path):
            if cap and len(results) >= cap:
                return
            valid_moves = current_game.valid_moves(player, remaining_rolls)

            # Base case: no rolls left or no valid moves
            if not remaining_rolls or not valid_moves:
                if path:
                    # sorting the moves in the path and using a set to track unique movesets
                    key = tuple(sorted((path)))
                    # Ensure we remove permutations of the same moveset
                    if key not in results:
                        results[key] = path
                return

            for move in valid_moves:
                game_copy = current_game.copy()
                rolls_copy = remaining_rolls.copy()
                game_copy.make_move(player, move[0], move[1], rolls_copy)
                rolls_copy.remove(move[2])
                recurse(game_copy, rolls_copy, path + [move])

        recurse(game, rolls, [])
        results = list(results.values()) 
        return results

    def apply_moves(self, game: Gammon, moveset, rolls, player):
        for move in moveset:
            game.make_move(player, move[0], move[1], rolls)

    def score_moveset(self, game: Gammon, moveset, rolls, player):
        """Quickly apply moveset and return heuristic score of resulting position for move ordering."""
        self.score_move_call += 1
        game_copy = game.copy()
        self.apply_moves(game_copy, moveset, rolls, player)
        return self.h(game_copy)
    
    def ordered_moveset(self, game: Gammon, rolls, player, moves_cap=5):
        """Orders the moveset based on heuristic score of resulting position for move ordering with forward prunning."""
        moveset = self.get_moveset(game, rolls, player)
        # Handle Max and Min
        is_max = (player == self.player_number)
        # Implement forward pruning to cap number of moves evaluated for each roll
        return sorted(moveset, key=lambda moves: self.score_moveset(game, moves, rolls, player), reverse=is_max)[:moves_cap]

    def take_turn(self, game: Gammon, depth=2, moves_cap=5):
        # reset transposition table at the start of each turn since we won't revisit states across turns
        self.transposition_table = {}

        # Also reset current move, current roll, and current score for demonstration purposes
        self.current_move = None
        self.current_roll = None
        self.current_score = None

        # Roll dice
        rolls = game.roll_dice()
        self.current_roll = rolls

        # Implement move ordering so that we can evaluate best moves and prune worse moves for chance nodes
        moveset = self.ordered_moveset(game, rolls, self.player_number, moves_cap=moves_cap)

        # Pass turn if no valid moves
        if not moveset:
            if self.player_number == 1 and game.state.board[24] > 0:
                print("Player 1 (White) has pieces on the bar but can't re-enter, skipping turn.")
            elif self.player_number == -1 and game.state.board[25] > 0:
                print("Player 2 (Black) has pieces on the bar but can't re-enter, skipping turn.")
            else:
                print("No valid moves, skipping turn.")
            return
        
        # Keep track of which full moveset gives best expectation
        best = -float('inf')
        best_moves = None
        for moves in moveset:
            game_copy = game.copy()
            self.apply_moves(game_copy, moves, rolls, self.player_number)
            move_expectation = self.expectiminimax(game_copy, depth, is_max_next=(self.player_number == -1), moves_cap=moves_cap)
            if move_expectation > best:
                best = move_expectation
                best_moves = moves

        # If all moves guarantee loss, choose any one
        if best_moves is None:
            best_moves = moveset[0]

        self.current_move = best_moves
        self.current_score = best
        # Run game.make_move()
        self.apply_moves(game, best_moves, rolls, self.player_number)

    def expectiminimax(self, game: Gammon, depth=2, is_max_next=False, alpha=-float("inf"), beta=float("inf"), moves_cap=2):
        # Key for tranposition table
        key = (tuple(game.state.board), depth, is_max_next)
        # Check if we've already evaluated this state at this depth and turn and return if so
        if key in self.transposition_table:
            return self.transposition_table[key]
        
        # Increment nodes visited
        self.nodes_visited += 1
        if depth == 0 or game.game_over():
            return self.h(game)

        if is_max_next:
            total_expected = 0

            for possible_roll in self.roll_outcomes:
                # Initialize alpha, beta, and best value for this roll
                alpha_roll = alpha
                beta_roll = beta
                best_value = float("-inf")

                # Skip move ordering in recursive calls to save time, but still get moveset with early exit once cap is reached
                move_lst = self.get_moveset(game, possible_roll, self.player_number, cap=moves_cap)
                if not move_lst:
                    # If no valid moves, just evaluate the expectation of the next state
                    game_copy = game.copy()
                    val = self.expectiminimax(game_copy, depth - 1, not is_max_next, alpha_roll, beta_roll, moves_cap=moves_cap)
                    weight = 1/36 if len(possible_roll) == 4 else 2/36
                    total_expected += val * weight
                    continue

                for moves in move_lst:
                    game_copy = game.copy()
                    self.apply_moves(game_copy, moves, possible_roll, self.player_number)
                    val = self.expectiminimax(game_copy, depth - 1, not is_max_next, alpha_roll, beta_roll, moves_cap=moves_cap)
                    best_value = max(best_value, val)
                    # Update alpha for this roll and prune if possible
                    alpha_roll = max(alpha_roll, best_value)
                    if alpha_roll >= beta_roll:
                        # Increment nodes pruned by the number of moves we didn't evaluate for this roll
                        self.nodes_pruned += len(move_lst) - move_lst.index(moves) - 1
                        break
                
                # Weight each roll
                weight = 1/36 if len(possible_roll) == 4 else 2/36
                total_expected += best_value * weight

            # store total expected in transposition table for this position depth and turn
            self.transposition_table[key] = total_expected

            return total_expected

        else:
            total_expected = 0

            for possible_roll in self.roll_outcomes:
                # Initialize alpha, beta, and best value for this roll
                alpha_roll = alpha
                beta_roll = beta
                # Min chooses the worst move for you
                best_value = float("inf")
                
                # Skip move ordering in recursive calls to save time, but still get moveset with early exit once cap is reached
                move_lst = self.get_moveset(game, possible_roll, -self.player_number, cap=moves_cap)
                if not move_lst:
                    # If no valid moves, just evaluate the expectation of the next state
                    game_copy = game.copy()
                    val = self.expectiminimax(game_copy, depth - 1, not is_max_next, alpha_roll, beta_roll, moves_cap=moves_cap)
                    weight = 1/36 if len(possible_roll) == 4 else 2/36
                    total_expected += val * weight
                    continue

                for moves in move_lst:
                    game_copy = game.copy()
                    self.apply_moves(game_copy, moves, possible_roll, -self.player_number)
                    val = self.expectiminimax(game_copy, depth - 1, not is_max_next, alpha_roll, beta_roll, moves_cap=moves_cap)
                    # Minimize the expected value for the opponent's turn
                    best_value = min(best_value, val)
                    # Update beta for this roll and prune if possible
                    beta_roll = min(beta_roll, best_value)
                    if alpha_roll >= beta_roll:
                        # Increment nodes pruned by the number of moves we didn't evaluate for this roll
                        self.nodes_pruned += len(move_lst) - move_lst.index(moves) - 1
                        break

                # Weight each roll
                weight = 1/36 if len(possible_roll) == 4 else 2/36
                total_expected += best_value * weight

            # store total expected in transposition table for this position depth and turn
            self.transposition_table[key] = total_expected

            return total_expected

    def h(self, game: Gammon):
        """Heuristic function."""
        if game.game_over():
            return float("inf") * self.player_number
        # Initiailze heuristic
        heuristic = 0
        state = game.state.board
        # Weights
        pip_weight = 2
        blot_penalty = 5
        bar_penalty = 10
        prime_bonus = 3
        home_bonus = 2
        bearoff_bonus = 10

        # Calculate pip disparity to determine stuck penalty
        white_pip = sum((24 - i) * state[i] for i in range(24) if state[i] > 0)
        black_pip = sum((i + 1) * abs(state[i]) for i in range(24) if state[i] < 0)
        stuck_penalty = 8 if (black_pip - white_pip) < -30 else 3

        # Handles pip count, blots, home bonus, and stuck penalty
        for i in range(24):
            if state[i] > 0:
                heuristic -= pip_weight * (24 - i) * state[i]
                heuristic += home_bonus * state[i] if i >= 18 else 0
                heuristic -= stuck_penalty * state[i] if i < 6 else 0
                if state[i] == 1:
                    threat = sum(1 for j in range(max(0, i - 6), i) if state[j] < -1)
                    danger = (2 if i < 6 else 1) * (1 + threat)
                    heuristic -= blot_penalty * danger
            elif state[i] < 0:
                heuristic -= pip_weight * (i + 1) * state[i]
                heuristic -= home_bonus * abs(state[i]) if i < 6 else 0
                heuristic += stuck_penalty * abs(state[i]) if i >= 18 else 0
                if state[i] == -1:
                    threat = sum(1 for j in range(i + 1, min(24, i + 7)) if state[j] > 1)
                    danger = (2 if i >= 18 else 1) * (1 + threat)
                    heuristic += blot_penalty * danger

        # Apply prime bonus if consecutive blocked points in home board
        for i in range(18, 23):
            if state[i] > 1 and state[i + 1] > 1:
                heuristic += prime_bonus
        for i in range(0, 5):
            if state[i] < -1 and state[i + 1] < -1:
                heuristic -= prime_bonus

        # Bar and bearoff
        heuristic -= bar_penalty * state[24]
        heuristic += bar_penalty * state[25]
        heuristic += bearoff_bonus * state[26]
        heuristic -= bearoff_bonus * state[27]

        return heuristic * self.player_number

def play_game(player1: Player, player2: Player, depth=2, moves_cap=5, print_moves=False, turn_limit=80):
    # Create the game and initialize turn
    game = Gammon()
    turn = 0
    # start timer
    start = time.time()

    if print_moves:
        print("Initial board state:")
        print(game.state)
    
    # Play until game over or turn limit reached
    while not game.game_over() and turn < turn_limit:
        current_p = player1 if turn % 2 == 0 else player2
        player_color = "Player 1 (White)" if current_p == player1 else "Player 2 (Black)"
        if print_moves:
            print(f"===={player_color} taking turn {turn + 1}====")

        # Take turn and print results then increment turn
        current_p.take_turn(game, depth=depth, moves_cap=moves_cap)
        if print_moves:
            print(f"Rolled:        {current_p.current_roll}")
            if current_p.current_move:
                print(f"Best move:     {current_p.current_move}")
                print(f"Move score:    {current_p.current_score:.2f}")
            print(game.state)
        turn += 1

    # Check winner and print results
    winner = game.check_winner()
    if winner == 1:
        print("Player 1 (White) wins!")
    elif winner == -1:
        print("Player 2 (Black) wins!")
    else:
        print(f"Game ended after {turn_limit} turns with no winner.")
    # stop timer and print elapsed time
    elapsed = time.time() - start
    print(f"Game completed in {elapsed:.2f}s after {turn} turns.")
    return winner, turn, elapsed

def simulate(n_games=50, depth=1, moves_cap=5):
    p1_wins = 0
    total_turns = 0
    total_time = 0
    for _ in range(n_games):
        player1 = Player(1)
        player2 = Player(-1)
        winner, turn, elapsed = play_game(player1, player2, depth=depth, moves_cap=moves_cap, print_moves=False)
        if winner == 1:
            p1_wins += 1
        total_turns += turn
        total_time += elapsed
    print(f"P1 win rate: {p1_wins/n_games:.2%}")
    print(f"Avg turns: {total_turns/n_games:.1f}")
    print(f"Avg time: {total_time/n_games:.1f}s")

def main():
    # Simulate a whole game
    game = Gammon()
    player1 = Player(1)
    player2 = Player(-1)
    # play_game(player1, player2, depth=1, moves_cap=10, print_moves=True)
    simulate(n_games=50)

    # print("Initial board state:")
    # print(game.state)
    # Iniitialze depth and moves cap
    # depth = 2
    # moves_cap = 5
    # print(f"Evaluating position at depth={depth}")
    # score = player1.expectiminimax(game, depth=depth)
    # print(f"Position score for player 1: {score:.4f}")
    # print(f"Nodes visited (eval): {player1.nodes_visited}")
    # print(f"Nodes pruned  (eval): {player1.nodes_pruned}")

    # Reset before take_turn so we get isolated stats for the turn
    # player1.nodes_visited = 0
    # player1.nodes_pruned = 0

    # print(f"Player 1 taking turn at depth={depth}")
    # start = time.time()
    # player1.take_turn(game, depth=depth, moves_cap=moves_cap)
    # elapsed = time.time() - start

    # print(f"Rolled:        {player1.current_roll}")
    # print(f"Best move:     {player1.current_move}")
    # print(f"Move score:    {player1.current_score:.2f}")
    # print(f"Time:          {elapsed:.2f}s")
    # print(f"Nodes visited: {player1.nodes_visited}")
    # print(f"Nodes pruned:  {player1.nodes_pruned}")
    # print(f"Score moveset calls: {player1.score_move_call}")

    # print("\nBoard state after player 1's move:")
    # print(game.state)

if __name__ == "__main__":
    main()