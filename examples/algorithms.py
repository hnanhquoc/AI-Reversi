import random
import time

EMPTY, P1, P2, OUTER = -1, 1, 2, 0
PIECES = (EMPTY, P1, P2, OUTER)
PLAYERS = {P1: 'Player 1', P2: 'Player 2'}

# 8 directions
DIRECTIONS = [[0, 1], [1, 1], [1, 0], [1, -1], [0, -1], [-1, -1], [-1, 0], [-1, 1]]


# Check a move is legal (on board)
def isOnBoard(x, y):
    # Returns True if the coordinates are located on the board.
    return x >= 0 and x <= 7 and y >= 0 and y <= 7


# Initial board
def initial_board():
    board = []
    w, h = 8, 8
    board = [[EMPTY for x in xrange(w)] for y in xrange(h)]
    # The middle four squares should hold the initial piece positions.
    # board[3][3] = P1
    # board[3][4] = P2
    # board[4][3] = P2
    # board[4][4] = P1
    board[4][4] = P1
    board[4][5] = P2
    board[5][4] = P2
    board[5][5] = P1

    return board


# print current state of board
def print_board(board):
    rep = ''
    rep += '  %s\n' % ' '.join(map(str, xrange(0, 8)))
    for row in xrange(8):
        begin, end = 0, 8
        rep += '%d %s\n' % (row, ' '.join(str(board[row][begin:end])))
    return rep


# find the opponent of player
def opponent(player):
    return P1 if player is P2 else P2


# Check move from player is valid
def isValidMove(board, player, xstart, ystart):
    # Returns False if the player's move on space xstart, ystart is invalid.
    # If it is a valid move, returns a list of spaces that would become the player's if they made a move here.
    if board[xstart][ystart] != EMPTY or not isOnBoard(xstart, ystart):
        return False

    board[xstart][ystart] = player  # temporarily set the tile on the board.

    otherPlayer = opponent(player)

    tilesToFlip = []
    for dir in DIRECTIONS:
        x, y = xstart, ystart
        x += dir[0]  # first step in the direction
        y += dir[1]  # first step in the direction
        if isOnBoard(x, y) and board[x][y] == otherPlayer:
            # There is a piece belonging to the other player next to our piece.
            x += dir[0]
            y += dir[1]
            if not isOnBoard(x, y):
                continue
            while board[x][y] == otherPlayer:
                x += dir[0]
                y += dir[1]
                if not isOnBoard(x, y):  # break out of while loop, then continue in for loop
                    break
            if not isOnBoard(x, y):
                continue
            if board[x][y] == player:
                # There are pieces to flip over. Go in the reverse direction until we reach the original space, noting all the tiles along the way.
                while True:
                    x -= dir[0]
                    y -= dir[1]
                    if x == xstart and y == ystart:
                        break
                    tilesToFlip.append([x, y])

    board[xstart][ystart] = EMPTY  # restore the empty space
    if len(tilesToFlip) == 0:  # If no tiles were flipped, this is not a valid move.
        return False
    return tilesToFlip


# Return a list of valid move from player with current state of board
def getValidMoves(board, player):
    # Returns a list of [x,y] lists of valid moves for the given player on the given board.
    validMoves = []

    for x in xrange(8):
        for y in xrange(8):
            if isValidMove(board, player, x, y) != False:
                validMoves.append([x, y])
    return validMoves


# Return current score of board
def getScoreOfBoard(player, board):
    # Determine the score by counting the tiles. Returns a dictionary with keys 'X' and 'O'.
    opp = opponent(player)
    mine = 0
    their = 0
    for x in xrange(len(board)):
        for y in xrange(len(board)):
            if board[x][y] == player:
                mine += 1
            if board[x][y] == opp:
                their += 1
    return mine - their


# Make a move from current board
def makeMove(board, player, xstart, ystart):
    # Place the tile on the board at xstart, ystart, and flip any of the opponent's pieces.
    # Returns False if this is an invalid move, True if it is valid.
    tilesToFlip = isValidMove(board, player, xstart, ystart)

    if tilesToFlip == False:
        return False

    board[xstart][ystart] = player
    for x, y in tilesToFlip:
        board[x][y] = player
    return True


# Copy current board to a new board
def getBoardCopy(board):
    # Make a duplicate of the board list and return the duplicate.
    dupeBoard = board[:]
    return dupeBoard


# Check is current board is over state(no one can move)
def terminal_test(board, player):
    opp = opponent(player)
    # first find an empty square
    for i in xrange(len(board)):
        for j in xrange(len(board)):
            if board[i][j] != EMPTY:
                continue

            if isValidMove(board, player, i, j) != False:
                return False
            if isValidMove(board, opp, i, j) != False:
                return False

                # now we'll test if either player can put a piece in this square

    return True


# Evaluation function on algorithms
def calculateScore(board, player):
    score = 0
    for i in xrange(len(board)):
        for j in xrange(len(board)):
            if board[i][j] == player:
                score += 1
            else:
                score -= 1
    return score


######PLAY STRATEGY######

# Algorithms random
def random_strategy(player, board):
    return random.choice(getValidMoves(board, player))


# Algorithm minimax
def minimax(board, player, deepth, eval_fn=None):
    best = None
    validMove = []
    validMove = getValidMoves(board, player)
    # try each move
    for move in validMove:
        dupeBoard = getBoardCopy(board)
        makeMove(dupeBoard, player, move[0], move[1])
        # evaluate the position and choose the best move
        # NOTE: the minimax function computes the value for the current
        # player which is the opponent so we need to invert the value
        val = minimax_value(dupeBoard, player, deepth, eval_fn)
        if val is not None:
            val *= -1
        # update the best operator so far
        if best is None or val > best[0] and val is not None:
            best = (move[0], move[1], val)

    return best


# Calculate minimax value on minimax algorithm
def minimax_value(board, player, maxply, eval_fn=None):
    # if we have reached the maximum depth, the utility is approximated
    # with the evaluation function
    if maxply == 0 or terminal_test(board, player):
        if eval_fn:
            return eval_fn(board, player)
        else:
            return calculateScore(board, player)

    best = None

    # try each move
    for move in getValidMoves(board, player):
        dupeBoard = getBoardCopy(board)
        makeMove(dupeBoard, player, move[0], move[1])
        # evaluate the position and choose the best move
        # NOTE: the minimax function computes the value for the current
        # player which is the opponent so we need to invert the value
        val = minimax_value(dupeBoard, player, maxply - 1, eval_fn)
        if val is not None:
            val *= -1
        if best is None or val > best and val is not None:
            best = val

    return best


# Calculate minimax value on alphabeta cut off
def alphabeta_value(board, player, maxply, alpha, beta, eval_fn=None):
    # if we have reached the maximum depth, the utility is approximated
    # with the evaluation function
    if maxply == 0 or terminal_test(board, player):
        if eval_fn:
            return eval_fn(board, player)
        else:
            return calculateScore(board, player)

    # try each move
    for move in getValidMoves(board, player):
        dupeBoard = getBoardCopy(board)
        makeMove(dupeBoard, player, move[0], move[1])
        # evaluate the position and choose the best move
        # NOTE: the minimax function computes the value for the current
        # player which is the opponent so we need to invert the value
        # invert alpha beta values and meaning, think of the following
        #     alpha <=  my score <=  beta
        # => -alpha >= -my score >= -beta
        # => -alpha >= opp score >=  beta
        # => -beta  <= opp score <= -alpha
        if beta is not None:
            opp_alpha = -1 * beta
        else:
            opp_alpha = None
        if alpha is not None:
            opp_beta = -1 * alpha
        else:
            opp_beta = None
        val = alphabeta_value(dupeBoard, player, maxply - 1, opp_alpha, opp_beta, eval_fn)
        if val is not None:
            val *= -1
        # update alpha (current player's low bound)
        if alpha is None or val > alpha and val is not None:
            alpha = val
        # prune using the alpha-beta condition
        if (alpha is not None) and (beta is not None) and alpha >= beta:
            # I suppose we could return alpha here as well
            return beta

    # alpha is my best score
    return alpha


# Algorithm minimax use alphabeta cut off
def alphabeta(board, player, maxply, eval_fn=None):
    best_val, x, y = None, None, None
    validMove = []
    validMove = getValidMoves(board, player)
    # try each move    
    for move in validMove:
        dupeBoard = getBoardCopy(board)
        makeMove(dupeBoard, player, move[0], move[1])
        # evaluate the position and choose the best move
        # NOTE: the minimax function computes the value for the current
        # player which is the opponent so we need to invert the value
        # the -ve of my best val is the opponent's beta value
        if best_val is not None:
            opp_beta = -1 * best_val
        else:
            opp_beta = None
        val = alphabeta_value(dupeBoard, player, maxply, None, opp_beta, eval_fn)
        if val is not None:
            val *= -1
        # update the best operator so far
        if best_val is None or val > best_val and val is not None:
            (best_val, x, y) = (val, move[0], move[1])

    return (x, y, best_val)

# Algorithm Monte Carlo Tree Search


##########END ALGORITHMS##############


# print test case
init_board = initial_board();
board = print_board(init_board)
print(board)
# print(random_strategy(BLACK, init_board))
# print(getValidMoves(init_board,BLACK))
print(minimax(init_board, 2, 3))
print(alphabeta(initial_board(), 1, 3))
