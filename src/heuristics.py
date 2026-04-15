"""
Name: Josh Longo and Kevin Shi
Filename: heuristics.py
Description: This file contains the three different heuristic functions we tested on and their evolution
"""
from src.gammon import Gammon

def h1(self, game):
    """The original heuristic which is very basic."""
    if game.game_over():
        return float("inf") * self.player_number
    heuristic = 0
    state = game.state.board
    # Total distance to travel
    for i in range(0, 24):
        if state[i] > 0:
            heuristic -= (24 - i) * state[i]
        else:
            heuristic -= (i + 1) * state[i]
    # Penalty for blots. Modify based on whether the blot is in danger?
    blot_penalty = 2   
    for i in range(0, 24):
        if state[i] == 1:
            heuristic -= blot_penalty
        elif state[i] == -1:
            heuristic += blot_penalty
    # Heavy penalty for pieces on the bar. Increase based on opponent's points at home?
    bar_penalty = 5     
    heuristic -= bar_penalty * state[24]
    heuristic += bar_penalty * state[25]
    return heuristic * self.player_number


def h2(self, game: Gammon):
    """The second iteration of our heuristic function."""
    if game.game_over():
        return float("inf") * self.player_number
    
    # Initialize heuristic score and get board state
    heuristic = 0
    state = game.state.board

    # set weights for heuristic features (we can tune these based on performance)
    pip_weight = 1
    blot_penalty = 3
    bar_penalty = 7
    prime_bonus = 3
    home_bonus = 2
    bearoff_bonus = 10

    # Apply pip count weight for distance to bearing off 
    for i in range(0, 24):
        if state[i] > 0:
            heuristic -= pip_weight * (24 - i) * state[i]
        else:
            heuristic -= pip_weight * (i + 1) * state[i]

    # Penalty for blots
    for i in range(0, 24):
        if state[i] == 1:
            # More dangerous if blot is on opponent home board
            danger = 2 if i < 6 else 1  
            heuristic -= blot_penalty * danger
        elif state[i] == -1:
            danger = 2 if i >= 18 else 1
            heuristic += blot_penalty * danger

    # Heavy penalty for pieces on the bar
    heuristic -= bar_penalty * state[24]
    heuristic += bar_penalty * state[25]

    # Apply bonus for primes or when you have consecutive points blocked off
    for i in range(23):
        if state[i] > 1 and state[i+1] > 1:
            heuristic += prime_bonus
        elif state[i] < -1 and state[i+1] < -1:
            heuristic -= prime_bonus

    # Apply bonus for pieces in home board for player 1
    for i in range(18, 24):
        if state[i] > 0:
            heuristic += home_bonus * state[i]
            
    # Penalize for pieces in home board for player 2
    for i in range(0, 6):
        if state[i] < 0:
            heuristic -= home_bonus * abs(state[i])

    # Apply bonus for pieces borne off
    heuristic += bearoff_bonus * state[26]
    heuristic -= bearoff_bonus * state[27]

    return heuristic * self.player_number

def h3(self, game: Gammon):
    """The final iteration of the heuristic."""
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