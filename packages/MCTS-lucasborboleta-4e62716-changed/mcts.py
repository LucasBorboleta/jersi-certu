from __future__ import division

import time
import math
import random


def randomPolicy(state):
    while not state.isTerminal():
        try:
            action = random.choice(state.getPossibleActions())
        except IndexError:
            raise Exception("Non-terminal state has no possible actions: " + str(state))
        state = state.takeAction(action)
    return state.getReward()


class treeNode():
    def __init__(self, state, parent):
        self.state = state
        self.isTerminal = state.isTerminal()
        self.isFullyExpanded = self.isTerminal
        self.parent = parent
        self.numVisits = 0
        self.totalReward = 0
        self.children = {}


class mcts():
    def __init__(self, timeLimit=None, iterationLimit=None, explorationConstant=math.sqrt(2),
                 rolloutPolicy=randomPolicy):
        if timeLimit != None:
            if iterationLimit != None:
                raise ValueError("Cannot have both a time limit and an iteration limit")
            # time taken for each MCTS search in milliseconds
            self.timeLimit = timeLimit
            self.limitType = 'time'
        else:
            if iterationLimit == None:
                raise ValueError("Must have either a time limit or an iteration limit")
            # number of iterations of the search
            if iterationLimit < 1:
                raise ValueError("Iteration limit must be greater than one")
            self.searchLimit = iterationLimit
            self.limitType = 'iterations'
        self.explorationConstant = explorationConstant
        self.rollout = rolloutPolicy

    def search(self, initialState):
        self.root = treeNode(initialState, None)

        if self.limitType == 'time':
            timeLimit = time.time() + self.timeLimit / 1000
            while time.time() < timeLimit:
                self.executeRound()
        else:
            for i in range(self.searchLimit):
                self.executeRound()

        bestChild = self.getBestChild(self.root, 0)
        return self.getAction(self.root, bestChild)

    def searchInit(self, initialState):
        self.root = treeNode(initialState, None)
        if self.limitType == 'time':
            self.__searchTimeBegin = time.time()
            self.__searchTimeCurrent = self.__searchTimeBegin
            self.__searchTimeEnd = self.__searchTimeBegin + self.timeLimit / 1000
            self.__searchTimeSlice = 1000
        else:
            self.__searchIterationBegin = 0
            self.__searchIterationCurrent = self.__searchIterationBegin
            self.__searchIterationEnd = self.searchLimit
            self.__searchIterationSlice = 50
        self.__searchEnded = False

    def searchEnded(self):
        if not self.__searchEnded:
            if self.limitType == 'time':
                self.__searchTimeCurrent = time.time()
                self.__searchEnded = self.__searchTimeCurrent >= self.__searchTimeEnd
            else:
                self.__searchEnded = self.__searchIterationCurrent >= self.__searchIterationEnd
        return self.__searchEnded

    def searchRun(self):
        if not self.searchEnded():
            if self.limitType == 'time':
                self.__searchTimeSliceEnd = min(self.__searchTimeCurrent + self.__searchTimeSlice / 1000,
                                                self.__searchTimeEnd)
                while time.time() < self.__searchTimeSliceEnd:
                    self.executeRound()
            else:
                self.__searchIterationSliceEnd = min(self.__searchIterationCurrent + self.__searchIterationSlice,
                                                     self.__searchIterationEnd)
                while self.__searchIterationCurrent < self.__searchIterationSliceEnd:
                    self.executeRound()
                    self.__searchIterationCurrent += 1


    def searchGetProgression(self):
        if self.searchEnded():
            progression = 100
        else:
            if self.limitType == 'time':
                progression = 100 * ((self.__searchTimeCurrent - self.__searchTimeBegin)/
                                     (self.__searchTimeEnd - self.__searchTimeBegin))
            else:
                progression = 100 * ((self.__searchIterationCurrent - self.__searchIterationBegin)/
                                     (self.__searchIterationEnd - self.__searchIterationBegin))

        return progression

    def searchGetAction(self):
        bestChild = self.getBestChild(self.root, 0)
        return self.getAction(self.root, bestChild)

    def getStatistics(self, action=None):
        statistics = {}
        statistics['rootNumVisits'] = self.root.numVisits
        statistics['rootTotalReward'] = self.root.totalReward
        if action is not None:
            statistics['actionNumVisits'] = self.root.children[action].numVisits
            statistics['actionTotalReward'] = self.root.children[action].totalReward
        return statistics

    def executeRound(self):
        node = self.selectNode(self.root)
        reward = self.rollout(node.state)
        self.backpropogate(node, reward)

    def selectNode(self, node):
        while not node.isTerminal:
            if node.isFullyExpanded:
                node = self.getBestChild(node, self.explorationConstant)
            else:
                return self.expand(node)
        return node

    def expand(self, node):
        actions = node.state.getPossibleActions()
        random.shuffle(actions)
        for action in actions:
            if action not in node.children:
                newNode = treeNode(node.state.takeAction(action), node)
                node.children[action] = newNode
                if len(actions) == len(node.children):
                    node.isFullyExpanded = True
                return newNode

        raise Exception("Should never reach here")

    def backpropogate(self, node, reward):
        while node is not None:
            node.numVisits += 1
            node.totalReward += reward
            node = node.parent

    def getBestChild(self, node, explorationValue):
        bestValue = float("-inf")
        bestNodes = []
        for child in node.children.values():
            nodeValue = (node.state.getCurrentPlayer() * child.totalReward / child.numVisits +
                         explorationValue * math.sqrt(math.log(node.numVisits) / child.numVisits))
            if nodeValue > bestValue:
                bestValue = nodeValue
                bestNodes = [child]
            elif nodeValue == bestValue:
                bestNodes.append(child)
        return random.choice(bestNodes)

    def getAction(self, root, bestChild):
        for action, node in root.children.items():
            if node is bestChild:
                return action