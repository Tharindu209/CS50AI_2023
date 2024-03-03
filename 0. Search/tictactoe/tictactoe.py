
"""
Tic Tac Toe Player
"""

import math
from copy import deepcopy

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    Xcount = 0
    Ocount = 0
    
    for row in board:
        Xcount += row.count(X)
        Ocount += row.count(O)
    
    if Xcount <= Ocount:
        return X
    return O


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    action = []
    
    for row in range(3):
        for col in range(3):
            if board[row][col] == None:
                action.append([row, col])
    return action


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    row, col = action
    new_board = deepcopy(board)
    
    if board[row][col] != None:
        raise Exception
    
    new_board[row][col] = player(board)
    return new_board


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    for player in (X,O):
        
        for row in board:
            if row == [player]*3:
                return player
            
        for row in range(3):
            column = [board[row][col] for col in range(3)]
            if column == [player]*3:
                return player
            
        if [board[i][i] for i in range(3)] == [player]*3:
            return player
        elif [board[i][~i] for i in range(3)] == [player]*3:
            return player
    
    return None
    

def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board) != None:
        return True
    
    for row in board:
        if EMPTY in row:
            return False
    
    return True


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    if winner(board) == X:
        return 1
    elif winner(board) == O:
        return -1
    else:
        return 0


#start of min-max functions

def minValue(board):
    optimal_move = []
    if (terminal(board)):
        return utility(board), optimal_move
        
    minimum = 8
    for action in actions(board):
        min_val = maxValue(result(board, action))[0]
        if min_val < minimum:
            minimum = min_val
            optimal_move = action
    return minimum, optimal_move
        

def maxValue(board):
    optimal_move = []
    if (terminal(board)):
        return utility(board), optimal_move
    
    maximum = -8
    for action in actions(board):
        min_val = minValue(result(board, action))[0]
        if min_val > maximum:
            maximum = min_val
            optimal_move = action
    return maximum, optimal_move

# end of min-max functions

def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    players = player(board)
    
    if terminal(board):
        return None
    
    if players == X:
        return maxValue(board)[1]
    else:
        return minValue(board)[1]
