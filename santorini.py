# coding: utf-8
import unittest
import pandas as pd
import numpy as np


SHAPE = (5,5)

# Data structure
## Board is  5x5 matrix [ [],[],... ]
## Workers is dictionnary with keys A / B and object with two keys of positions {'A': { 0: [3, 1] , 1: [0, 0] } , 'B': {0:[3, 2], 1:[4, 4]] }}
## Move is a dictionnary with key A or B with contains a dictionary with indice of worker moved its new position {'B': { 0: [4,3]}}
## Construction is a sparse matrix 5x5 [ [],[],... ] with only one 1 and then 0

def createRandomBoard(low, high):
  return pd.DataFrame(np.random.random_integers(low, high, SHAPE))

def createEmptyBoard():
  return createRandomBoard(0,0 )

def getMovePosition(move):
  player = 'A' if 'A' in move else 'B'
  worker = 1 if 1 in move[player] else 0
  new_position = move[player][worker]
  return player, worker, new_position

def getConstructionMatrixForMove(move, workers, board):
  player, worker, new_position = getMovePosition(move)
  #generate allowable constructions aounrd worker
  i = new_position[0]
  j = new_position[1]
  allowable_constructions = createEmptyBoard()
  for ii in range(-1,2):
    for jj in range(-1,2):
      new_i = i + ii
      new_j = j + jj
      if new_j < 0 :
        new_j = 0
      if new_i < 0 :
        new_i = 0
      if new_j > 4 :
        new_j = 4
      if new_i > 4 :
        new_i = 4
      allowable_constructions[new_i][new_j] = 1

  # can't build on worker's position
  new_workers = updateWorkersPosition(move, workers)
  for player in new_workers:
    for worker in new_workers[player]:
      allowable_constructions[new_workers[player][worker][0]][new_workers[player][worker][1]] = 0
  return (allowable_constructions * (board != 4))



def getMoveMatrixForWorker(player, worker, workers, board):
  #generate allowable moves aounrd worker
  actual_position = workers[player][worker]
  i = actual_position[0]
  j = actual_position[1]
  allowable_moves = createEmptyBoard()
  for ii in range(-1,2):
    for jj in range(-1,2):
      new_i = i + ii
      new_j = j + jj
      if new_j < 0 :
        new_j = 0
      if new_i < 0 :
        new_i = 0
      if new_j > 4 :
        new_j = 4
      if new_i > 4 :
        new_i = 4
      allowable_moves[new_i][new_j] = 1

  # can't move on worker's position
  for player in workers:
    for worker in workers[player]:
      allowable_moves[workers[player][worker][0]][workers[player][worker][1]] = 0

  actual_level = board[i][j]
  return (allowable_moves * (board != 4) * (board <= (actual_level +1)) )


def constructionIsValid(move, construction, workers, board):
  allowable_constructions = getConstructionMatrixForMove(move, workers, board)
  return (allowable_constructions * construction ).sum().sum() > 0


def moveIsValid(move, workers, board):

  player = 'A' if 'A' in move else 'B'
  worker = 1 if 1 in move[player] else 0
  move_matrix = createEmptyBoard()
  move_matrix[move[player][worker][0]][move[player][worker][1]] = 1
  allowable_moves = getMoveMatrixForWorker(player, worker, workers, board)

  return (move_matrix * allowable_moves ).sum().sum() > 0



def generateMovesFromMatrix(player, worker, move_matrix):
  moves = []
  for i in range(0, SHAPE[0]):
    for j in range(0, SHAPE[0]):
      if move_matrix[i][j] > 0:
        move = {}
        move[player] = {}
        move[player][worker] = [i, j]
        moves.append(move)
  return moves

def generateConstructionsFromMatrix( construction_matrix):
  constructions = []
  for i in range(0, SHAPE[0]):
    for j in range(0, SHAPE[0]):
      if construction_matrix[i][j] > 0:
        construction = createEmptyBoard()
        construction[i][j] = 1
        constructions.append(construction)
  return constructions

def isWinningMove( move, board):
  player, worker, new_position = getMovePosition(move)
  return board[new_position[0]][new_position[1]] == 3


def updateWorkersPosition( move, workers):
  updates_workers = workers.copy()
  player, worker, new_position = getMovePosition(move)
  updates_workers[player][worker] = new_position
  return updates_workers

class SantoriniTests(unittest.TestCase):
    def testConstructionValidity(self):
        board = createEmptyBoard()
        move = {'A': { 0: [ 3,4] }}
        workers = {'A': { 0: [3, 1] , 1: [0, 0] } , 'B': {0:[3, 2], 1:[4, 4] }}
        #must build next to worker
        construction = pd.DataFrame([[0, 0, 0, 0, 0],
                                  [0, 0, 0, 0, 0],
                                  [0, 1, 0, 0, 0],
                                  [0, 0, 0, 0, 0],
                                  [0, 0, 0, 0, 0]])
        self.assertEqual(constructionIsValid(move, construction, workers, board) , False)
        #can't build on worker
        construction = pd.DataFrame([[0, 0, 0, 0, 0],
                                  [0, 0, 0, 0, 0],
                                  [0, 0, 0, 0, 0],
                                  [0, 0, 0, 0, 0],
                                  [0, 0, 0, 1, 0]])
        self.assertEqual(constructionIsValid(move, construction, workers, board) , False)
        #shoul be ok to build here
        construction = pd.DataFrame([[0, 0, 0, 0, 0],
                                  [0, 0, 0, 0, 0],
                                  [0, 0, 0, 0, 0],
                                  [0, 0, 0, 0, 0],
                                  [0, 0, 1, 0, 0]])
        self.assertEqual(constructionIsValid(move, construction, workers, board) , True)
        #can't build on level 4
        construction = pd.DataFrame([[0, 0, 0, 0, 0],
                                  [0, 0, 0, 0, 0],
                                  [0, 0, 0, 0, 0],
                                  [0, 0, 0, 0, 0],
                                  [0, 0, 1, 0, 0]])
        board = pd.DataFrame([[1, 1, 2, 0, 3],
                           [4, 2, 0, 4, 4],
                           [4, 2, 1, 4, 4],
                           [0, 4, 1, 0, 0],
                           [3, 4, 4, 2, 1]])
        self.assertEqual(constructionIsValid(move, construction, workers, board) , False)


    def testMoveValidity(self):
        board = pd.DataFrame([[1, 1, 2, 4, 3],
                              [4, 2, 0, 0, 4],
                              [4, 2, 1, 2, 4],
                              [0, 4, 1, 0, 0],
                              [3, 4, 0, 0, 1]])
        workers = {'A': { 0: [3, 1] , 1: [0, 0] } , 'B': {0:[3, 2], 1:[4, 4] }}
        move = {'A': { 0: [ 3, 4] }}
        #has to move around 1 case
        self.assertEqual(moveIsValid(move,  workers, board) , False)
        #can't stay in place
        move = {'A': { 0: [ 3, 1] }}
        self.assertEqual(moveIsValid(move,  workers, board) , False)
        #can't move on other workers
        move = {'A': { 0: [ 3, 2] }}
        self.assertEqual(moveIsValid(move,  workers, board) , False)
        #can't move on level 4
        move = {'A': { 0: [ 3, 0] }}
        self.assertEqual(moveIsValid(move,  workers, board) , False)
        #can't climb more than 1 level
        move = {'A': { 0: [ 2, 0] }}
        self.assertEqual(moveIsValid(move,  workers, board) , False)
        #but can get down from 2 levels
        workers = {'A': { 0: [2, 0] , 1: [0, 0] } , 'B': {0:[3, 2], 1:[4, 4] }}
        move = {'A': { 0: [ 2, 1] }}
        self.assertEqual(moveIsValid(move,  workers, board) , True)

    def testGenerateMoves(self):
        board = pd.DataFrame([[1, 1, 2, 4, 3],
                              [4, 2, 0, 0, 4],
                              [4, 2, 1, 2, 4],
                              [0, 4, 1, 0, 0],
                              [3, 4, 0, 0, 1]])
        workers = {'A': { 0: [3, 1] , 1: [0, 0] } , 'B': {0:[3, 2], 1:[4, 4] }}
        player = 'A'
        worker = 1
        move_matrix = getMoveMatrixForWorker(player, worker, workers, board)
        self.assertEqual(generateMovesFromMatrix(player, worker, move_matrix) , [{'A': {1:[ 1,0]}} , {'A': {1:[ 1,1]}} ] )
        player = 'A'
        worker = 0
        move_matrix = getMoveMatrixForWorker(player, worker, workers, board)
        self.assertEqual(generateMovesFromMatrix(player, worker, move_matrix) , [{'A': {0:[ 2,1]}} , {'A': {0:[ 2,2]}} ] )

    def testGenerateConstructions(self):
        board = pd.DataFrame([[1, 1, 2, 4, 3],
                              [4, 2, 0, 0, 4],
                              [4, 2, 1, 2, 4],
                              [0, 4, 1, 0, 0],
                              [3, 4, 0, 0, 1]])
        workers = {'A': { 0: [3, 1] , 1: [0, 0] } , 'B': {0:[3, 2], 1:[4, 4] }}
        move = {'A': {1:[ 1,1]}}
        construction_matrix = getConstructionMatrixForMove(move, workers, board)
        constructions = generateConstructionsFromMatrix(construction_matrix)
        self.assertEqual(len(constructions) , 6)
        for construction in constructions:
          self.assertEqual(construction.sum().sum() , 1)

    def testMoveIsWinning(self):
        board = pd.DataFrame([[1, 1, 2, 4, 3],
                              [4, 2, 0, 0, 4],
                              [4, 2, 3, 2, 4],
                              [0, 4, 1, 0, 0],
                              [3, 4, 0, 0, 1]])
        workers = {'A': { 0: [3, 2] , 1: [0, 0] } , 'B': {0:[3, 2], 1:[4, 4] }}
        move = {'A': {1:[ 1,1]}}
        self.assertEqual(isWinningMove(move, board), False)
        move = {'A': {0:[ 2,2]}}
        self.assertEqual(isWinningMove(move, board), True)

    def testUpdateWorkersPosition(self):
        workers = {'A': { 0: [3, 2] , 1: [0, 0] } , 'B': {0:[3, 2], 1:[4, 4] }}
        move = {'A': {0:[ 1,1]}}
        updates_workers = updateWorkersPosition(move, workers)
        self.assertEqual(updates_workers['A'][0], [1,1])


board = pd.DataFrame([[1, 1, 2, 4, 3],
                      [4, 2, 0, 0, 4],
                      [4, 2, 1, 2, 4],
                      [0, 4, 1, 0, 0],
                      [3, 4, 0, 0, 1]])
workers = {'A': { 0: [3, 1] , 1: [0, 0] } , 'B': {0:[3, 2], 1:[4, 4] }}
player = 'A'
worker = 1
move_matrix = getMoveMatrixForWorker(player, worker, workers, board)
moves = generateMovesFromMatrix(player, worker, move_matrix)
for move in moves:
  construction_matrix = getConstructionMatrixForMove(move, workers, board)
  #print('---')
  #print(move)
  #print(construction_matrix)


def main():
    unittest.main()

if __name__ == '__main__':
    main()
