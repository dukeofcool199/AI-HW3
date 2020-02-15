import random
import numbers
import sys

sys.path.append("..")  # so other modules can be found in parent dir
from Player import *
from Constants import *
from Construction import CONSTR_STATS
from Ant import UNIT_STATS
from Move import Move
from GameState import *
from AIPlayerUtils import *
from pdb import set_trace


##
# AIPlayer
# Description: The responsibility of this class is to interact with the game by
# deciding a valid move based on a given game state. This class has methods that
# were implemented by students in Dr. Nuxoll's AI course. Cole, Qi, and Moses.
#
# Variables:
#   playerId - The id of the player.
##
class AIPlayer(Player):

    # __init__
    # Description: Creates a new Player
    #
    # Parameters:
    #   inputPlayerId - The id to give the new player (int)
    #   cpy           - whether the player is a copy (when playing itself)
    ##
    def __init__(self, inputPlayerId):
        super(AIPlayer, self).__init__(inputPlayerId, "Mitchell_Marsh")

    ##
    # getPlacement
    #
    # Description: called during setup phase for each Construction that
    #   must be placed by the player.  These items are: 1 Anthill on
    #   the player's side; 1 tunnel on player's side; 9 grass on the
    #   player's side; and 2 food on the enemy's side.
    #
    # Parameters:
    #   construction - the Construction to be placed.
    #   currentState - the state of the game at this point in time.
    #
    # Return: The coordinates of where the construction is to be placed
    ##
    def getPlacement(self, currentState):
        numToPlace = 0
        # implemented by students to return their next move
        if currentState.phase == SETUP_PHASE_1:  # stuff on my side
            numToPlace = 11
            moves = []
            for i in range(0, numToPlace):
                move = None
                while move == None:
                    # Choose any x location
                    x = random.randint(0, 9)
                    # Choose any y location on your side of the board
                    y = random.randint(0, 3)
                    # Set the move if this space is empty
                    if currentState.board[x][y].constr == None and (x, y) not in moves:
                        move = (x, y)
                        # Just need to make the space non-empty. So I threw whatever I felt like in there.
                        currentState.board[x][y].constr == True
                moves.append(move)
            return moves
        elif currentState.phase == SETUP_PHASE_2:  # stuff on foe's side
            numToPlace = 2
            moves = []
            for i in range(0, numToPlace):
                move = None
                while move == None:
                    # Choose any x location
                    x = random.randint(0, 9)
                    # Choose any y location on enemy side of the board
                    y = random.randint(6, 9)
                    # Set the move if this space is empty
                    if currentState.board[x][y].constr == None and (x, y) not in moves:
                        move = (x, y)
                        # Just need to make the space non-empty. So I threw whatever I felt like in there.
                        currentState.board[x][y].constr == True
                moves.append(move)
            return moves
        else:
            return [(0, 0)]

    ##
    # getMove
    # Description: Gets the next move from the Player.
    #
    # Parameters:
    #   currentState - The state of the current game waiting for the player's move (GameState)
    #
    # Return: The Move to be made
    ##
    def getMove(self, currentState):

        frontierNodes = [initNode(currentState)]
        expandedNodes = []

        # look less ahead when game is simple
        if len(getAntList(currentState, PLAYER_TWO, (WORKER,)))==0:
            numExpansions = 1
        else:
            numExpansions = 4

        for i in range(numExpansions):
            # best_node = min(frontierNodes, key=lambda node: node["eval"])
            best_node = frontierNodes[0]

            while len(frontierNodes)>30:
                del frontierNodes[-1]

            expandedNodes.append(best_node)
            frontierNodes.remove(best_node)
            newNodes = expandNode(best_node)
            for node in newNodes:
                if getWinner(node['state']) is not None:
                    return bestMove([node])
            frontierNodes.extend(newNodes)
            frontierNodes.sort(key=lambda node: node["eval"])


        # Evaluate the frontier nodes in order to find the best evaluated node,
        # then make the move that correlates.
        return bestMove(frontierNodes)

    ##
    # getAttack
    # Description: Gets the attack to be made from the Player
    #
    # Parameters:
    #   currentState - A clone of the current state (GameState)
    #   attackingAnt - The ant currently making the attack (Ant)
    #   enemyLocation - The Locations of the Enemies that can be attacked (Location[])
    ##
    def getAttack(self, currentState, attackingAnt, enemyLocations):
        # Attack a random enemy.
        return enemyLocations[random.randint(0, len(enemyLocations) - 1)]

    ##
    # registerWin
    #
    # This agent doesn't learn
    #
    def registerWin(self, hasWon):
        # method templaste, not implemented
        pass


FOOD_WEIGHT = None
CARRYING = None
CLOSEST_FOOD = None
CLOSEST_PLACE = None


##
# heuristicStepsToGoal
#
# Description: called to determine the utility of making a certain move.
# A state is passed in and certain conditions are rewarded or given
# negative rewards. These positive and negative values are added or subtracted
# from the score value.
#
# Parameters:
#   state - the state of the game at this point in time.
#
# Return: The "score" value, or how good the state is. The higher the score,
# the closer the state is deemed to being a win state.
##

def heuristicStepsToGoal(state):
    # winning handled by A* search
    if getWinner(state) is not None:
        return 0


    score = 0.0
    me = state.whoseTurn
    enemy = 1 - me
    global FOOD_WEIGHT
    global CARRYING
    global CLOSEST_FOOD
    global CLOSEST_PLACE
    # create targets
    hill = getConstrList(state, me, (ANTHILL,))[0]
    hillAndTunnel = getConstrList(state, me, (ANTHILL, TUNNEL))
    foods = getConstrList(state, None, (FOOD,))

    enemyAnts = getAntList(state, enemy)

    # Weight values for how much utility certain ants or statuses are worth
    WORKER_ANT_WEIGHT = 1
    if FOOD_WEIGHT == None or not any(CLOSEST_FOOD.coords == food.coords for food in foods):
        CARRYING, CLOSEST_FOOD, CLOSEST_PLACE = \
            min(((stepsToReach(state, food.coords, place.coords), food, place)
                 for food in foods for place in hillAndTunnel),
                key=lambda vals: vals[0])
        FOOD_WEIGHT = CARRYING * 2


    # Useful pointers
    myInv = state.inventories[me]
    score -= myInv.foodCount * FOOD_WEIGHT
    enemyInv = state.inventories[enemy]

    ants = getAntList(state, me, (WORKER, DRONE))

    numWorkers = 0
    numDrones=0
    numSoldiers=0

    for ant in ants:
        # Assign targets for workers
        if ant.type == WORKER:
            numWorkers += 1
            offset = CARRYING
            if ant.carrying:
                target = CLOSEST_PLACE
                score -= CARRYING
                score -= ant.coords[0] * .0001
            else:
                target = CLOSEST_FOOD
                score += ant.coords[0] * .0001

        # Assign targets for drones
        elif ant.type == DRONE:
            # Have worker attack drone first, then queen
            numDrones += 1
            workers = getAntList(state, enemy, (WORKER,))
            if len(workers) == 0:
                target = enemyInv.getQueen()
            else:
                target = workers[0]
            offset = stepsToReach(state, hill.coords, target.coords)

        # # Assign targets for soldiers
        elif ant.type == SOLDIER:
            # Have soldier go after the queen
            numSoldiers += 1
            target = enemyInv.getQueen()
            offset = stepsToReach(state, hill.coords, target.coords)

        # Keep the ants moving towards their targets by awarding
        # utility for proximity.
        score -= offset - stepsToReach(state, ant.coords, target.coords)

    if numWorkers >= 2:
        score += FOOD_WEIGHT * 3 * numWorkers
    elif numWorkers == 0:
        score += FOOD_WEIGHT * 11

    eneWorkers = getAntList(state, enemy, (WORKER,))
    if (numDrones != 0 and len(eneWorkers) > 0) or len(eneWorkers)==0:
        score -= FOOD_WEIGHT * 3

    # Award utility for killing enemy ants
    for ant in enemyAnts:
        if ant.type != QUEEN:
            score += UNIT_STATS[ant.type][COST]*FOOD_WEIGHT
        else:
            score += ant.health*FOOD_WEIGHT/UNIT_STATS[ant.type][HEALTH]*11


    return score


##
# initNode
#
# Description: helper function that creates an initial node in which to
# expand.
#
# Parameters:
#   state - the state of the game at this point in time.
#
# Return: A node that represents the root of the tree.
##
def initNode(state):
    return {"move": None,
            "state": state,
            "depth": 0,
            "eval": heuristicStepsToGoal(state),
            "ref": None}


##
# expandNode
#
# Description: called to determine the utility of making a certain move.
# A state is passed in and certain conditions are rewarded or given
# negative rewards. These positive and negative values are added or subtracted
# from the score value.
#
# Parameters:
#   node - the node that needs to be expanded. This will give all of the possible moves
#   and the the nodes that come from them.
#
# Return: A list of the nodes that are seen when expanding the parameter node.
##
def expandNode(node):
    moves = listAllLegalMoves(node["state"])

    new_nodes = []

    for move in moves:
        next_state = getNextStateAdversarial(node["state"], move)
        new_nodes.append(
            {"move": move,
             "state": next_state,
             "depth": node["depth"] + 1,
             "eval": heuristicStepsToGoal(next_state) + node["depth"] + 1,
             "ref": node})

    return new_nodes


##
# bestMove
#
# Description: helper function that searches through all of the frontier nodes and
# selects the node with the best utility.
#
# Parameters:
#   nodes - a list of nodes to search through.
#
# Return: The move value from the node with the highest utility evaluation.
#         This will be the next move performed.
##
def bestMove(nodes):
    best_node = min(nodes, key=lambda node: node["eval"])

    while best_node["ref"]["ref"] is not None:
        best_node = best_node["ref"]

    return best_node["move"]

##
# isNode
#
# Description: test function to make sure that any node being returned by a function
# is of the correct form and has the correct values.
#
# Parameters:
#   node - a node to be evaluated
#
##
def isNode(node):
    """check is the input object a valid node"""
    nodeKeys = {"move", "state", "depth", "eval", "ref"}
    return isinstance(node, dict) \
           and nodeKeys.issubset(set(node.keys())) \
           and (node['move'] is None or
                isinstance(node["move"], Move)) \
           and isinstance(node['state'], GameState) \
           and isinstance(node['depth'], int) \
           and isinstance(node['eval'], numbers.Number)


##
# runTest
#
# Description: test function to make sure all of the helper functions
# work as intended.
#
#
##
def runTest():
    basicState = GameState.getBasicState()

    basicState.inventories[2].constrs.append(Construction((6, 5), FOOD))

    basicNode = initNode(basicState)

    # Make sure initNode() creates a valid node
    if not isNode(basicNode):
        print("initNode create not a node")

    newNodes = expandNode(basicNode)
    # Make sure that expandNode() returns a list of valid nodes
    if not all(isNode(node) for node in newNodes):
        print("expandNode not create nodes")

    bm = bestMove(newNodes)
    # Make sure that bestMove() returns a move that is within the list of
    # valid moves.
    if not any(bm.moveType == move.moveType and
               bm.coordList == move.coordList and
               bm.buildType == move.buildType
               for move in \
               listAllLegalMoves(basicNode['state'])):
        print("bestMove not return valid move")

    # Make sure that  heuristicStepsToGoal() returns a valid utility
    testState = basicNode['state']
    for test in range(100):
        newMove = random.choice(listAllLegalMoves(testState))
        testState = getNextStateAdversarial(testState, newMove)

        heuy = heuristicStepsToGoal(testState)
        if not isinstance(heuy, numbers.Number):
            print("heuristicStepsToGoal not return float")


runTest()
FOOD_WEIGHT = None
