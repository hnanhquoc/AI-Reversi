#!/usr/bin/env python2

from socketIO_client import SocketIO, BaseNamespace

from algorithms import *
from cache_dict import *
from util import *


class PlayReversi(object):
    def __init__(self):
        self.board = []
        self.game_state = (self.board, role)
        self.legal_cache = CacheDict()

        self.num = raw_input(
            "1. Random\n2. Minimax\n3. Alpha Beta Prunning\n4. Monte Carlo Tree Search\nPlease choose an agent: ")

    def make_a_move(self, updated_board, player):
        self.board = updated_board
        # my_move_x = raw_input("Enter x: ")
        # my_move_y = raw_input("Enter y: ")
        # picked = self.agent_pick_move(self.game_state)
        if self.num == '2':
            result = minimax(self.board, player, 3)
        elif self.num == '3':
            result = alphabeta(self.board, player, 5)
        else:
            result = random_strategy(player, self.board)
        return {'X': result[0], 'Y': result[1]}

    def update_board(self, updated_board):
        self.board = updated_board
        print print_board(self.board)

    def agent_pick_move(self, state):
        turn = state[1]
        legal_moves = self.legal_moves(state)
        picked = None
        if turn == role:
            if turn == P1:
                picked = self.white_agent.get_action(state, legal_moves)
            elif turn == P2:
                picked = self.black_agent.get_action(state, legal_moves)
            else:
                raise ValueError

        if picked is None:
            return None
        elif picked not in legal_moves:
            info(str(picked) + ' is not a legal move! Game over.')
            quit()

        return picked

    def legal_moves(self, game_state, force_cache=False):
        # Note: this is a very naive and inefficient way to find
        # all available moves by brute force.  I am sure there is a
        # more clever way to do this.  If you want better performance
        # from agents, this would probably be the first area to improve.
        if force_cache:
            return self.legal_cache.get(game_state)

        board = game_state[0]
        if board.is_full():
            return []

        cached = self.legal_cache.get(game_state)
        if cached is not None:
            return cached

        board_size = board.get_size()
        moves = []  # list of x,y positions valid for turn

        for y in range(board_size):
            for x in range(board_size):
                if self.is_valid_move(game_state, x, y):
                    moves.append((x, y))

        self.legal_cache.update(game_state, moves)
        return moves

    def is_valid_move(self, game_state, x, y):
        board, turn = game_state
        piece = board.board[y][x]
        if piece != EMPTY:
            return False

        enemy = opponent[turn]

        # now check in all directions, including diagonal
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                if dy == 0 and dx == 0:
                    continue

                # there needs to be >= 1 opponent piece
                # in this given direction, followed by 1 of player's piece
                distance = 1
                yp = (distance * dy) + y
                xp = (distance * dx) + x

                while is_in_bounds(xp, yp, board.size) and board.board[yp][xp] == enemy:
                    distance += 1
                    yp = (distance * dy) + y
                    xp = (distance * dx) + x

                if distance > 1 and is_in_bounds(xp, yp, board.size) and board.board[yp][xp] == turn:
                    return True
        return False


class ReversiNamespace(BaseNamespace):
    def on_updated(self, data):
        """ Response to updated event
        """
        print('updated triggered')
        board = data['board']
        play_reversi.update_board(board)

    def on_yourturn(self, data):
        """ Response to yourturn event
        """
        print('yourturn triggered')
        move = play_reversi.make_a_move(data['board'], data['player'])
        self.emit('mymove', {'rowIdx': move['X'], 'colIdx': move['Y']})

    def on_errormessage(self, data):
        """ Response to errormessage event
        """
        print(data)

    def on_end(self, data):
        """ Response to end event
        """
        print('The winner is ', data['winner'])
        print('P1 count: ', data['player1'])
        print('P2 count: ', data['player2'])


global play_reversi
play_reversi = PlayReversi()

token = raw_input('Enter your token: ')
# Use socketio with defined Namespace
# socketIO = SocketIO('localhost', 8100, ReversiNamespace, params={'token': token})
socketIO = SocketIO('localhost', 8100, params={'token': token})
gameplay = socketIO.define(ReversiNamespace, '/play')
socketIO.wait()
