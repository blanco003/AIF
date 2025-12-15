
import time
import sys
import os
from test.llm import get_llm_move
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from connect_four import ConnectFour
from minmax import MinMax
from monte_carlo_tree_search import MCTS 


def run_game(symbolic_ai_type, llm, starter, time_MCTS=None, depth_alphabeta=None):
       
        game = ConnectFour()
        symbolic_ai_player = game.player1
        llm_player = game.player2

        if symbolic_ai_type==1:
               symbolic_ai = "MCTS"
               mcts = MCTS(game, ai_player=symbolic_ai_player)
        else:
                symbolic_ai = "MinMax"
                
        invalid_gpt_moves = 0
        gpt_move_call_count = 0

        if starter == "S": 
               game.to_play = symbolic_ai_player 
        else: 
               game.to_play = llm_player

        costs = []
        symbolic_ai_times = []
        llm_times = []
        count_plies = 0

        while not game.game_over():

                print("\nCurrent state:")
                game.print_board()
                
                count_plies+=1

                if game.to_play == symbolic_ai_player:

                        if symbolic_ai_type == 1:
                                # MCTS turn
                                print("\nMCST thinking...")
                                mcts.search_max_time(time_MCTS)
                                stats, num_rollouts, run_time = mcts.statistics()
                                print(f"\nMCST statistics ({num_rollouts} rollouts in {run_time:.2f}s):")
                                for move, (wins, visits) in stats.items():
                                        win_rate = wins / visits if visits > 0 else 0
                                        print(f"Column {move}: {wins:.1f}/{visits} ({win_rate:.2%})")

                                mcts_move = mcts.best_move()
                                print(f"\nMCST chooses column {mcts_move}")
                                mcts.move(mcts_move) 

                                symbolic_ai_times.append(run_time)

                        else:
                                # MinMax turn
                                print("\nMinMax thinking...")
                                minmax = MinMax(game)

                                start_time = time.perf_counter()
                                minmax_move = minmax.get_best_move_alphabeta(depth_alphabeta, ai_player=symbolic_ai_player, verbose=False)
                                end_time = time.perf_counter()
                
                                print(f"MinMax reasoned {(end_time-start_time):.4f}s. Nodes explored: {minmax.nodes_explored}")  
                                print(f"MinMax chooses column {minmax_move}")

                                symbolic_ai_times.append(end_time-start_time)
                                game.make_move(minmax_move, symbolic_ai_player)                

                # LLM turn
                else:
                        print("\nLLM thinking...")
                        while True:
                                try:
                                        start_time = time.perf_counter()
                                        move_data = get_llm_move(llm, game)  
                                        end_time = time.perf_counter()
                                        llm_move = move_data["column"]
                                        #llm_reason = move_data["reason"]
                                        cost = move_data["cost"]
                                        costs.append(cost)
                                        gpt_move_call_count += 1

                                        if llm_move in game.available_moves():
                                                break
                                        else:
                                                invalid_gpt_moves += 1
                                                print(f"LLM proposed illegal move: {llm_move}, retrying...")
                                except Exception as e:
                                        print(f"Errore nella chiamata LLM: {e}, retrying...")

                
                        print(f"LLM chooses column {llm_move}")
                        #print(f"Reason: {llm_reason}")
                        print(f"LLM reasoned {(end_time-start_time):.4f}s")
                        print(f"Cost: {cost}")
                        llm_times.append(end_time-start_time)

                        if symbolic_ai_type == 1:
                                mcts.move(llm_move)  
                        else: 
                                game.make_move(llm_move, game.to_play)

        winner = game.check_winner()
        if winner != None:  
                game.print_board_with_win()
        else:
                game.print_board()
                
        if winner == symbolic_ai_player:
                winner_str = "symbolic"
                print(f"\n{symbolic_ai} wins!\n")
        elif winner == llm_player:
                winner_str = "llm"
                print("\nLLM wins!\n")
        else:
                winner_str = "tie"
                print("\nTie!\n")

        total_cost_llm = sum(costs) 
        avg_cost_llm = sum(costs)/len(costs)
        total_time_llm = sum(llm_times)
        avg_time_llm = sum(llm_times)/len(llm_times)

        total_time_symbolic_ai = sum(symbolic_ai_times)
        avg_time_symbolic_ai = sum(symbolic_ai_times)/len(symbolic_ai_times)

        print("Invalid GPT moves:", invalid_gpt_moves)
        print(f"Total cost: {total_cost_llm:.4f}$. Avg cost: {avg_cost_llm:.4f}$")
        print(f"Total time llm: {total_time_llm:.4f}s. Avg time: {avg_time_llm:.4f}s")
        print(f"Total time {symbolic_ai}: {total_time_symbolic_ai:.4f}s. Avg time: {avg_time_symbolic_ai:.4f}s")
        print(f"Number of plies: {count_plies}")

        result = {
                "winner": winner_str,
                "invalid_gpt_moves": invalid_gpt_moves,
                "total_cost": total_cost_llm,
                "avg_cost": avg_cost_llm,
                "total_llm_time": total_time_llm,
                "avg_llm_time": avg_time_llm,
                "total_symbolic_time": total_time_symbolic_ai,
                "avg_symbolic_time": avg_time_symbolic_ai,
                "llm_move_times": llm_times,
                "symbolic_move_times": symbolic_ai_times,
                "count_plies":count_plies
        }

        return result


def run_experiments():
       
        print("\n=====================================")
        print("Choose type of Symbolic AI:")
        print("1. Monte Carlo Tree Search")
        print("2. MinMax")

        time_MCTS = None
        depth_alphabeta = None

        symbolic_ai = ""
        while True:
                symbolic_ai_type = int(input("\nEnter your choice (1-2): "))
                if symbolic_ai_type in [1, 2]:
                        break
                print("Invalid choice.")

        if symbolic_ai_type==1:
                
                print("\nMCTS stopping criteria:")
                print("1. Time limit")
                print("2. Number of rollouts")

                while True:
                        limit = int(input("Enter your choice (1-2): "))
                        if limit==1:
                                time_MCTS = int(input("\nInsert time (seconds) limit: "))
                                break
                        elif limit==2:
                                max_rollout = int(input("\nInsert number of rollouts: "))
                                break
                        print("Invalid choice.")
            
        else:
                symbolic_ai = "MinMax"
                depth_alphabeta = int(input("\nInsert max depth of Alpha-Beta: "))


        print("\n===================================")
        print("Choose the LLM:")
        print("1. OpenAi : o4 mini high")
        print("2. Anthropic : clude 3.7 thinking")
        print("3. Gemini : gemini 3 pro")

        while True:
                llm_type = int(input("\nEnter your choice (1-3): "))
                if llm_type in [1, 2, 3]:
                        break
                print("Invalid choice")

        if llm_type == 1:
                llm = "openai"
        elif llm_type == 2:
                llm = "claude"
        else:
                llm = "gemini"

        print("\n===================================")
        n = int(input("\nNumber of games: "))

        results = []

        for i in range(n):
               print(f"\n================ GAME {i+1}/{n} ========================")
               # alternate who starts
               if i % 2 == 0:
                   starter = "S"  
               else:
                   starter = "G"
        
               result = run_game(symbolic_ai_type, llm, starter, time_MCTS, depth_alphabeta)
               results.append(result)


        print("\n=============== Final statistics  =================")

        wins_symbolic = sum(1 for r in results if r["winner"] == "symbolic")
        wins_llm = sum(1 for r in results if r["winner"] == "llm")
        ties = sum(1 for r in results if r["winner"] == "tie")

        avg_cost_game = sum(r["total_cost"] for r in results) / len(results)
        avg_cost_move = sum(r["avg_cost"] for r in results) / len(results)

        all_llm_times = [t for r in results for t in r["llm_move_times"]]
        all_symbolic_times = [t for r in results for t in r["symbolic_move_times"]]

        avg_llm_time_per_move = sum(all_llm_times) / len(all_llm_times)
        avg_symbolic_time_per_move = sum(all_symbolic_times) / len(all_symbolic_times)

        total_invalid_moves = sum(r["invalid_gpt_moves"] for r in results)
        avg_plies = sum(r["count_plies"] for r in results) / len(results)
   
        print(f"Symbolic AI  ({symbolic_ai}) wins: {wins_symbolic}/{n} ({wins_symbolic/n*100:.1f}%)")
        print(f"LLM ({llm}) wins: {wins_llm}/{n} ({wins_llm/n*100:.1f}%)")
        print(f"Ties: {ties}/{n} ({ties/n*100:.1f}%)")

        print(f"\nLLM avg time per move: {avg_llm_time_per_move:.4f}s")
        print(f"Symbolic AI avg time per move: {avg_symbolic_time_per_move:.4f}s")

        print(f"\nAverage LLM cost per game: {avg_cost_game:.4f}$")
        print(f"Average LLM cost per move: {avg_cost_move:.4f}$")

        print(f"\nAverage number of plies per game: {avg_plies:.2f}")
        print(f"Total invalid LLM moves across all games: {total_invalid_moves}")


run_experiments()


