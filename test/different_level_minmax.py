import time
from copy import deepcopy
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from connect_four import ConnectFour
from minmax import MinMax


depth_levels = [1,2,4,6]
depth_levels_pruning = [1,2,4,6, 8]

scenarios = ['Start Game', 'Mid Game', 'Late Game']

def benchmark_minmax_alphabeta(depth_levels=depth_levels, pruning=False):

    results = {}
    boards = {}

    boards['Start Game'] = ConnectFour()

    mid_board = ConnectFour()
    mid_board.board = [
        [" ", " ", " ", " ", " ", " ", " "],
        [" ", " ", " ", " ", " ", " ", " "],
        [" ", " ", " ", "O", " ", " ", " "],
        [" ", " ", "X", "O", " ", "O", " "],
        [" ", "O", "X", "X", "O", "X", " "],
        [" ", "X", "O", "O", "X", "X", " "]
    ]
    mid_board.to_play = mid_board.player1
    boards['Mid Game'] = mid_board
    

    late_board = ConnectFour()
    late_board.board = [
        [" ", " ", " ", " ", " ", " ", " "],
        ["O", " ", "X", " ", " ", "O", " "],
        ["X", "O", "O", "O", "X", "X", "X"],
        ["O", "X", "X", "O", "X", "O", "O"],
        ["X", "O", "X", "X", "O", "X", "X"],
        ["X", "X", "O", "O", "X", "X", "O"]
    ]
    late_board.to_play = late_board.player1
    boards['Late Game'] = late_board

  
    for scenario_name, board in boards.items():

        print(f"\n====== {scenario_name} ======")
        results[scenario_name] = {}

        for depth in depth_levels:
            print(f"Depth {depth}: ", end='')

            game_copy = deepcopy(board)
            mm = MinMax(game_copy)

            start = time.process_time()
            if pruning:
                best_move = mm.get_best_move_alphabeta(max_depth=depth, ai_player=board.player2, verbose=False)
            else:
                best_move = mm.get_best_move(max_depth=depth, ai_player=board.player2, verbose=False)
            elapsed = time.process_time() - start

            results[scenario_name][depth] = {
                'time': elapsed,
                'nodes': mm.nodes_explored,
                'best_move': best_move
            }

            print(f"{elapsed:.8f}s, nodes explored: {mm.nodes_explored}, choosen move: {best_move}")

    return results


print("\n========== Minimax without a-b pruning ==========")
results_minmax = benchmark_minmax_alphabeta(depth_levels, pruning=False)

print("\n========== Minimax with a-b pruning ==========")
results_minmax_alfa_beta = benchmark_minmax_alphabeta(depth_levels_pruning, pruning=True)
