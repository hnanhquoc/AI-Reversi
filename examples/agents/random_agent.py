import random
from agents.agent import Agent
from util import *

class RandomAgent(Agent):
    """An agent that simply chooses
    totally random legal moves."""

    def __init__(self, reversi, turn):
        self.reversi = reversi
        self.color = turn

    def get_action(self, state, legal_moves):
        if not legal_moves:
            return None
        return random.choice(legal_moves)

    def reset(self):
        pass

    def observe_win(self, winner):
        pass
