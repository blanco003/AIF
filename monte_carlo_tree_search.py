import math
import random
import time

class Node:
    """Single Node of the Monte Carlo Tree Search"""

    def __init__(self, move=None, parent=None, player=None):
        self.move = move  # move that brought the parent to the current node
        self.parent = parent  # pointer to the parent node
        self.children = {}  # dictionary of children of the current node
        self.player = player  # player who made the move
        self.wins = 0   # how many times the node led to a good result for the player who moved
        self.visits = 0  # how many times the node was visited during the simulations

    
    def add_children(self, children):
        """
        Adds children to the current node
        - children: children to add to the current node
        """
        for child in children:
            self.children[child.move] = child
    
    
    def value(self, c=math.sqrt(2)):
        """Compute UCB1 value of the current node."""

        if self.visits == 0:
            return float('inf')
        
        if self.parent is None or self.parent.visits == 0:
            return float('inf')
        
        # UCB1 formula : exploitation + exploration
        exploitation = self.wins / self.visits
        exploration = c* math.sqrt(math.log(self.parent.visits) / self.visits)
        return exploitation + exploration


class MCTS:

    def __init__(self, state, ai_player):
        self.root_state = state #  root starting state for rollouts
        self.root = Node() # root node
        self.ai_player = ai_player # symbol of the player
        self.num_rollout = 0 # number of rollouts performed
        self.run_time = 0 # effective time

    """
    Selection: Starting from the root, we traverse the tree, choosing the child that maximizes the UCB1 value
    until we find a non-fully expanded node or a leaf.

    UCT is a very effective selection policy known as "upper confidence bounds applied to trees".
    The policy ranks each possible move based on an upper confidence bound formula UCT called UCB1.
    """
    
    def select_node(self):
        node = self.root
        state = self.root_state
        path_moves = []  # list of moves made during the selection so you can undo them after rollout.

        # going  down the tree
        while node.children:

            # selects among the children of the current node the one with the largest UCB1 value
            node = max(node.children.values(), key=lambda n: n.value())

            # applies the current node's move to the selected child
            row = state.make_temporary_move(node.move, node.player)  # store the row to undo the move later
            path_moves.append((node.move, row))  # store the move (column) to undo the move later

        # expansion of the current node
        expanded = self.expand(node, state) 

        # if the current node has been expanded and so it has children 
        if expanded:   

            # randomly choose one of the children for rollout 
            # idea: the children represent a new move not yet simulated
            child = random.choice(list(node.children.values()))

            # make the move of the new chosen child, and store the row and columns to undo it later
            row = state.make_temporary_move(child.move, child.player)
            path_moves.append((child.move, row))

            return child, path_moves  # the selected child is node to roll out 
        
        else:
            return node, path_moves   # return the current node


    def expand(self, parent, state):
        """
        Expansion: if the reached node is not terminal, its children are expanded (new possible moves).
        - parent: node after the selection and to which to add new moves (children)
        - state: current state of the game in the MCTS:
        """

        if state.game_over():
            # leaf node
            return False

        # non-leaf node: creates a child node for each available move
        children = []
        current_player = state.to_play
        for move in state.available_moves():
            children.append(Node(move, parent, current_player))

        # add all children to the current node
        parent.add_children(children)
        return True


    def roll_out(self, state, current_player):
        """
        Rollout: Runs a random simulation untill the end of the game.
        - state: e current state of the board from which starting the simulation 
        - current_player: point of view of the simulation 
        """

        played = []  # list of moves made during rollout, so that can be undone later

        while not state.game_over():

            moves = state.available_moves()
            # random choice among the available moves

            move = random.choice(moves)      
        
            # apply the random move
            row = state.make_temporary_move(move, current_player)
            played.append((move, row))  

            # switch player turn
            current_player = "O" if current_player == "X" else "X"

        # when the game is over get the outcome of the simulation
        winner = state.get_outcome()
        if winner == self.ai_player:
            outcome = 1.0
        elif winner == 0:  
            outcome = 0.5
        else:
            outcome = 0.0

        # restores the board to its initial state before the rollout
        for move, row in reversed(played):
            state.undo_move(move, row)

        # return the outcome of the simulation
        return outcome
 

    def back_propagate(self, node, outcome):   
        """
        Backpropagation: the rollout result is propagated up the visited nodes.
        - node: 
        - outcome: result of the simulation 
        """

        # node: node to start from (node ​​where the rollout was done)
        # outcome: risultato della simulazione

        # going back up to the root 
        while node is not None:

            # increases the number of visits to the current node (each rollout increases the number of visits by 1)
            node.visits += 1

            # if the node represents the player to be simulated with MCST, update the wins with the outcome: player MCTS wins
            if node.player == self.ai_player:
                node.wins += outcome
            else:
                # update wins from the point of view of defeat: MCTS player loses
                node.wins += (1 - outcome)

            # go up one level to the parent
            node = node.parent 

    def search_max_time(self, time_limit=10.0):
        """
        Perform the loop of MCTS. It does as many rollouts as time allows, updating the tree with win information.
        - time_limit =seconds for the MCTS to run rollouts
        """

        start_time = time.time()
        num_rollouts = 0

        while time.time() - start_time < time_limit:

            # each iteration performs:
            # selection -> expansion -> rollout -> backpropagation

            # 1-2) selection + expansion
            node, path_moves = self.select_node()

            # 3) rollout from the selected node
            outcome = self.roll_out(self.root_state, self.root_state.to_play)

            # 4) backpropagation after each rollout to propagate the result to all nodes along the selected path
            self.back_propagate(node, outcome)

            # restores the board to its initial state before selection
            for move, row in reversed(path_moves):
                self.root_state.undo_move(move, row)

            num_rollouts += 1

        self.num_rollout = num_rollouts
        self.run_time = time.time() - start_time


    def search_max_rollout(self, max_rollout=10000):
        """
        Perform the loop of MCTS. It does as many rollouts as specified, taking all the time needed,
        updating the tree with win information.
        - max_rollout = number of rollout to be done
        """

        start_time = time.process_time()
        num_rollouts = 0

        while num_rollouts < max_rollout:

            node, path_moves = self.select_node()
            outcome = self.roll_out(self.root_state, self.root_state.to_play)
            self.back_propagate(node, outcome)
            for move, row in reversed(path_moves):
                self.root_state.undo_move(move, row)

            num_rollouts += 1

        self.num_rollout = num_rollouts
        self.run_time = time.process_time() - start_time


    def best_move(self):
        """
        After performing the MCTS search with search_max_time / search_max_rollout (), 
        the root of the tree contains several children, which represents a possible move available at the current position.

        The method chooses the best move among those explored, using the number of visits as a criterion.
        More visits = better explored node; more statistically reliable.

        Win-rate with few visits is noisy. Example: 2/3 = 66%, 65/100 = 65% -> 2/3 is statistically much less reliable.

        UCB1 does exactly this: it initially explores nodes with few visits, then favors good win-rates,
        and over time, the stronger nodes win the "draw" and accumulate more visits.

        Tie-break using the win-rate between nodes with equal visits.
        """

        # if the game is already over there is no point in making a move
        if self.root_state.game_over():
            return -1
        
        # find the maximum visits between the children of the root
        max_visits = max(n.visits for n in self.root.children.values())

        # select nodes that have the same max visits value
        candidates = [n for n in self.root.children.values() if n.visits == max_visits]

        # tie-break with best win rate 
        best = max(candidates, key=lambda n: n.wins / n.visits if n.visits > 0 else 0)

        # returns the corresponding move 
        return best.move
    
    def move(self, move):
        """
        After a move is performed on the real board, with respect to any player, the MCTS recycles the part of the tree
        it has already explored so as not to have to start from scratch each time, keeping the MCTS synchronized with the real game state.
        """

        # apply the move on the actual state of the game
        self.root_state.make_move(move, self.root_state.to_play)

        # if the move had already been explored in the MCTS
        if move in self.root.children:
            # update the root to the corresponding node and cuts the reference to the parent node
            self.root = self.root.children[move]
            self.root.parent = None
        else:
            # in this case MCTS had never explored that move
            # build a new root and expand it 
            self.root = Node()
            self.expand(self.root, self.root_state)


    def statistics(self):
        """
        Statistics per debug/analisi.
        For each move print the wins, visits and the win rate.
        """ 
        stats = {move: (child.wins, child.visits) for move, child in self.root.children.items()}
        return stats, self.num_rollout, self.run_time

