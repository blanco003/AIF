import random

class MinMax:

    """
    Minimax is a recursive algorithm that simulates all possible future moves and attempts to choose the best move for
    a player, assuming the opponent always plays the optimal move.
    - AI (maximizing player): attempts to maximize the score
    - Opponent (minimizing player): attempts to minimize the AI's score
    """

    def __init__(self, game):
        self.game = game  # current state of the game 
        self.nodes_explored = 0  # number of nodes explored during the minimax search for the best move


    def minmax(self, depth, is_maximizing, max_depth=1, ai_player=None):
        """
        Performs the recursive search of the best move.
        - depth: current depth of the recursion
        - is_maximizing: flag which indicates whether the current player is maximizing or minimizing 
        - max_depth: maximum search depth 
        - ai_player: player with respect to maximize the score
        """

        if ai_player is None:
            ai_player = self.game.player2
        opponent_player = self.game.player1 if ai_player == self.game.player2 else self.game.player2

        self.nodes_explored += 1
        
        # check if the recursion is in a terminal state of the game
        winner = self.game.check_winner()

        if winner == opponent_player:
            return float("-inf")
        if winner == ai_player:
            return float("inf")
        if self.game.is_board_full() or depth >= max_depth:  # Depth limited version
            #return 0     # with depth limited a score = 0 is not useful to discriminate between bad/good moves
            score = self.game.evaluate_board(ai_player)    # heuristic evaluation 
            return score  


        if is_maximizing:

            # for each avaible move: 
            # apply the move, call minmax recursively passing the turn to the opponent player, and lastly undo the move
            # then return the best score (maximum score) found

            best_score = float("-inf")
            
            for move in self.game.available_moves():
                row = self.game.make_temporary_move(move, ai_player)
                score = self.minmax(depth + 1, False, max_depth, ai_player)
                self.game.undo_move(move, row)
                best_score = max(best_score, score)

            return best_score
        
        else:

            # similar to the maximizing case, but now it's the opponent's turn
            # so we look for the minimum score found, because the opponent tries to beat the AI

            best_score = float("inf")

            for move in self.game.available_moves():
                row = self.game.make_temporary_move(move, opponent_player)
                score = self.minmax(depth + 1, True, max_depth, ai_player)
                self.game.undo_move(move, row)
                best_score = min(best_score, score)

            return best_score
        

    def get_best_move(self, max_depth=1, ai_player=None, verbose=False):
        """
        Returns the best move for the AI's turn, calling minimax to evaluate all possible moves
        and returning the one with the highest score.
        - max_depth: maximum search depth 
        - ai_player: player with respect to maximize the score
        - verbose: flag to print the selected move with the corresponding score
        """

        if ai_player is None:
            ai_player = self.game.player2

        self.nodes_explored = 0  

        best_score = float("-inf")
        best_move = None

        # for each avaible move: 
        # apply the move, call minmax recursively passing the turn to the opponent player, and lastly undo the move
        # then return the best score (maximum score) found

        for move in self.game.available_moves():
            row = self.game.make_temporary_move(move, ai_player)
            score = self.minmax(0, False, max_depth, ai_player)  # start of the recursion: depth 0, and minimizing player (False)
            self.game.undo_move(move, row)

            # update the best score and corresponding move
            if score > best_score:
                best_score = score
                best_move = move
        
        if verbose:
            print(f"Selected move for '{ai_player}' : column {best_move} with final score {best_score}")

        # fallback : all the avaible move have score -inf (inevitable defeat)
        # just return a random move and then lose...
        if best_score == float("-inf"):
            best_move = random.choice(self.game.available_moves())

        return best_move

 
    """
    Minimax with Alpha-Beta pruning: like minmax, it evaluates all possible moves,
    but Alpha-Beta Pruning version introduces two new values:
    - alpha: best score found so far by the maximizer along the path
    - beta: best score found so far by the minimizer along the path

    If during exploration it turns out that alpha >= beta, the path can be pruned,
    since it makes no sense to continue exploring that branch, because the opposing player
    would never allow that situation. This drastically reduces the number of nodes evaluated.
    """

    def minmax_alphabeta_pruning(self, depth, is_maximizing, alpha, beta, max_depth=1, ai_player=None, heuristic=True):
        """
        Performs the recursive search of the best move.
        - depth: current depth of the recursion
        - is_maximizing: flag which indicates whether the current player is maximizing or minimizing 
        - alpha: best score found so far by the maximizer along the path
        - beta: best score found so far by the minimizer along the path
        - max_depth: maximum search depth 
        - ai_player: player with respect to maximize the score
        - heuristic: flag which indicates whether to use the heuristic evaluation
        """
        
        if ai_player is None:
            ai_player = self.game.player2
        opponent_player = self.game.player1 if ai_player == self.game.player2 else self.game.player2
        
        self.nodes_explored += 1

        # check if the recursion is in a terminal state of the game
        winner = self.game.check_winner()

        if winner == opponent_player:
            return float("-inf")
        if winner == ai_player:
            return float("inf")
        if self.game.is_board_full() or depth >= max_depth:  # Depth limited version
               
            if not heuristic:
                score = 0   # with depth limited a score = 0 is not useful to discriminate between bad/good moves
            else: 
                score = self.game.evaluate_board(ai_player)  # heuristic evaluation 
    
            return score  

        if is_maximizing:

            best_score = float("-inf")

            for move in self.game.available_moves():
                row = self.game.make_temporary_move(move, ai_player)
                score = self.minmax_alphabeta_pruning(depth + 1, False, alpha, beta, max_depth, ai_player)
                self.game.undo_move(move, row)
                best_score = max(best_score, score)
                alpha = max(alpha, best_score) # update alpha : best score found for the maximizing player

                if alpha >= beta:
                    break  # pruning : the current situation is already better than anything the minimizer can achieve

            return best_score
        
        else:

            best_score = float("inf")

            for move in self.game.available_moves():
                row = self.game.make_temporary_move(move, opponent_player)
                score = self.minmax_alphabeta_pruning(depth + 1, True, alpha, beta, max_depth, ai_player)
                self.game.undo_move(move, row)
                best_score = min(best_score, score)
                beta = min(beta, best_score)  # update alpha : best score found for the minimizing player

                # if the minimum that the minimizer can achieve (beta) is worse than or equal to the maximum that 
                # the AI ​​can achieve (alpha) elsewhere - > all subsequent moves are useless there is no point in continuing to explore

                if beta <= alpha:
                    break  # pruning : the current situation is already worse than anything the maximizer can achieve elsewhere

            return best_score

    
    def get_best_move_alphabeta(self, max_depth=1, ai_player=None, heuristic=True, verbose=False):
        """
        Returns the best move for the AI's turn, calling minmax + alpha beta pruning to evaluate
        all possible moves and returning the one with the highest score.
        - max_depth: maximum search depth 
        - ai_player: player with respect to maximize the score
        - heuristic: flag which indicates whether to use the heuristic evaluation
        - verbose: flag to print the selected move with the corresponding score       
        """
        
        if ai_player is None:
            ai_player = self.game.player2    

        self.nodes_explored = 0

        best_score = float("-inf")
        best_move = None

        for move in self.game.available_moves():
            row = self.game.make_temporary_move(move, ai_player)

            # start of the recursion:
            # depth 0 and minimizing player (False)
            # alpha starts from - inf and increases along the way
            # beta starts from + inf and decreases along the way
            score = self.minmax_alphabeta_pruning(0, False, float("-inf"), float("inf"), max_depth, ai_player, heuristic)

            self.game.undo_move(move, row)

            # update the best score and corresponding move
            if score > best_score:
                best_score = score
                best_move = move

        if verbose:
            print(f"Selected move for '{ai_player}' : column {best_move} with final score {best_score}")

        # fallback : all the avaible move have score -inf (inevitable defeat)
        # just return a random move and then lose...
        if best_score == float("-inf"):
            best_move = random.choice(self.game.available_moves())

        return best_move