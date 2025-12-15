import sys
import time
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from connect_four import ConnectFour
from monte_carlo_tree_search import MCTS
from minmax import MinMax


def play_game_minmax_vs_mcts(time_limit, depth_minmax, starter, verbose=False):

    game = ConnectFour()
    mcts_player = game.player1
    minmax_player = game.player2

    game.to_play = starter

    count_ply = 0
    
    mcts = MCTS(game, ai_player=mcts_player)

    minmax_times = []
    mcts_times = []

    while not game.game_over():
        count_ply+=1
        game.print_board()
        if game.to_play == mcts_player:
            
            start = time.time()
            mcts.search_max_time(time_limit)
            end = time.time()
            mcts_times.append(end-start)
            move = mcts.best_move()
            mcts.move(move)
        else:
            minmax = MinMax(game)
            start = time.time()
            move = minmax.get_best_move_alphabeta(depth_minmax, minmax_player, heuristic=False)
            end = time.time()
            minmax_times.append(end-start)
            mcts.move(move)
            
    winner = game.check_winner()

    if winner!=None:
        game.print_board_with_win()
    else:
        game.print_board()

    avg_minmax_time = sum(minmax_times)/len(minmax_times)
    avg_mcts_time = sum(mcts_times)/len(mcts_times)

    return winner, count_ply, avg_minmax_time, avg_mcts_time


def grid_search_mcts_vs_minmax(time_limits, depths, n_games=10):

    results = {}

    total_games = len(depths) * len(time_limits) * n_games
    current_game = 0

    for depth in depths:
        for tmax in time_limits:
            

            print("\n===================================================")
            print(f" GRID SEARCH : depth={depth} | tmax={tmax}s | (Game {current_game}/{total_games})")
            print("=====================================================")

            key = (depth, tmax)
            results[key] = {"win": 0, "loss": 0, "draw": 0, "total_ply": 0}

            for g in range(n_games):
                current_game += 1
                tmp = ConnectFour()
                starter = tmp.player2 if g % 2 == 0 else tmp.player1
                
                winner, count_ply, avg_minmax_time, avg_mcts_time = play_game_minmax_vs_mcts(
                        time_limit=tmax,
                        depth_minmax=depth,
                        starter=starter,
                        verbose=False
                    )

                if winner == tmp.player1:
                    results[key]["win"] += 1
                elif winner == tmp.player2:
                    results[key]["loss"] += 1
                else:
                    results[key]["draw"] += 1

                results[key]["total_ply"] += count_ply

                winner_str = (
                        "MCTS" if winner == tmp.player1 else
                        "MinMax" if winner == tmp.player2 else
                        "Draw"
                    )

                print(f"Game {g+1}/{n_games}. Starter: {starter}. Winner: {winner_str}. Count ply: {count_ply}")
                print(f"Avg minmax time {avg_minmax_time}s . Avg mcts time {avg_mcts_time}s")

    return results


if __name__ == "__main__":
   
    TIME_LIMITS = [10]      
    DEPTHS = [6] 
    N_GAMES = 10                     

    stats = grid_search_mcts_vs_minmax(
        time_limits=TIME_LIMITS,
        depths=DEPTHS,
        n_games=N_GAMES
    )

    print("\n\n==================== Final Statistics ====================")

    for (depth, tmax), r in stats.items():
        print(f"\ndepth={depth}, t={tmax}s")

        total = r['win'] + r['loss'] + r['draw']
        win_p = r['win'] / total * 100
        loss_p = r['loss'] / total * 100
        draw_p = r['draw'] / total * 100
        avg_ply = r["total_ply"] / total if total > 0 else 0

        print(f"  Wins  (MCTS): {r['win']} ({win_p:.1f}%)")
        print(f"  Losses:       {r['loss']} ({loss_p:.1f}%)")
        print(f"  Draws:        {r['draw']} ({draw_p:.1f}%)")
        print(f"  Average ply:  {avg_ply:.2f}")
