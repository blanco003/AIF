from connect_four import ConnectFour
from minmax import MinMax
from monte_carlo_tree_search import MCTS
from test.llm import get_llm_move
import time

def choose_game_mode():
    print("\n============== Connect Four ==============")
    print("Choose game mode:")
    print("1. MinMax vs Human")
    print("2. Monte Carlo Tree Search vs Human")
    print("3. MinMax vs Monte Carlo Tree Search")
    print("4. Symbolic AI vs Large Language Model")
    
    while True:
        choice = int(input("\nEnter you choice (1-4): "))
        if choice in [1, 2, 3, 4]:
            return int(choice)
        print("Invalid choice.")


def main():

    choice = choose_game_mode()
    
    if choice == 1:   # Minmax Alpha-Beta vs Human
        
        depth_alphabeta = int(input("\nInsert max depth of MinMax Alpha-Beta Pruning: "))
        game = ConnectFour()

        human_player = game.player1
        minmax_player = game.player2 

        while True:
            starter = input("\nWho starts? (M for MiMax, H for Human): ").upper()
            if starter in ["M", "H"]:
                break
            print("Enter M or H: ")

        if starter == "M":
            game.to_play = minmax_player
        else:
            game.to_play = human_player

        while not game.game_over():
            
            game.print_board()

            if game.to_play == minmax_player:
                print("\nMinimax thinking...")
                minmax = MinMax(game)
                start_time = time.perf_counter()
                minmax_move = minmax.get_best_move_alphabeta(depth_alphabeta, minmax_player, verbose=False)
                end_time = time.perf_counter()
                print(f"MinMax reasoned for {(end_time-start_time):.4f}s. Nodes explored: {minmax.nodes_explored}")
                print(f"MinMax chooses column {minmax_move}")
                game.make_move(minmax_move, minmax_player)
            else:
                print("\nYour turn...")
                while True:
                    try:
                        move = int(input("Enter your move (0-6): "))
                        if move in game.available_moves():
                            game.make_move(move, human_player)
                            break
                        else:
                            print("Illegal move.")
                    except ValueError:
                        print("Enter your move (0-6): ")

        winner = game.check_winner()
        
        if winner != None:  
            game.print_board_with_win()
        else:
            game.print_board()

        if winner == minmax_player:
            print("\nMinMax wins!\n")
        elif winner == human_player:
            print("\nYou win!\n")
        else:
            print("\nTie!\n")
    
    elif choice == 2:    # MCTS vs Human
        
        print("\nMCTS Limit: \n1. Time limit \n2. Num. rollouts")
    
        while True:
            limit = int(input("\nEnter the limit type of MCTS (1-2): "))
            if limit==1:
                time_MCTS = int(input("Insert time (seconds) limit for MCTS: "))
                break
            elif limit==2:
                max_rollout = int(input("Insert max rollout MCTS: "))
                break
            print("Invalid choice.")
    
        game = ConnectFour()

        mcts_player = game.player1
        human_player = game.player2

        mcts = MCTS(game, ai_player=mcts_player)

        while True:
            starter = input("\nWho starts? (M for MCTS, H for Human): ").upper()
            if starter in ["M", "H"]:
                break
            print("Enter M or H.")

        if starter == "M":
            game.to_play = mcts_player
        else:
            game.to_play = human_player

        while not game.game_over():

            game.print_board()

            if game.to_play == mcts_player:
                print("\nMCTS thinking...")
            
                if limit==1:
                    mcts.search_max_time(time_MCTS)
                else:
                    mcts.search_max_rollout(max_rollout)
                
                stats, num_rollouts, run_time = mcts.statistics()
                print(f"\nMCTS statistics ({num_rollouts} rollouts in {run_time:.2f}s):")

                for move, (wins, visits) in stats.items():
                    win_rate = wins / visits if visits > 0 else 0
                    print(f"Column {move}: {wins:.1f}/{visits} ({win_rate:.2%})")

                mcts_move = mcts.best_move()
                print(f"\nMCTS chooses column {mcts_move}")

                # apply the move via MCTS.move (updates state and MCTS root)
                mcts.move(mcts_move)

            else:
                print("\nYour turn...")
                user_move = int(input("Enter a move (0-6): "))
                while user_move not in game.available_moves():
                    print("Illegal move")
                    user_move = int(input("Enter a move (0-6): "))

                # Apply human move via MCTS.move (updates state and MCTS root)
                mcts.move(user_move)

        winner = game.check_winner()
        
        if winner != None:  
            game.print_board_with_win()
        else:
            game.print_board()

        if winner == mcts_player:
            print("\nMCTS wins!\n")
        elif winner == human_player:
            print("\nYou win!\n")
        else:
            print("\nTie!\n")


    elif choice == 3:  # Alpha-Beta vs MCTS
        
        game = ConnectFour()

        minmax_player = game.player1    
        mcts_player = game.player2 

        mcts = MCTS(game, mcts_player)        
        depth_alphabeta = int(input("\nInsert max depth of MinMax Alpha-Beta Pruning: "))


        print("\nChoose the stopping criteria of MCTS:")
        print("1. Time limit")
        print("2. Number of rollouts")
    
        while True:
            limit = int(input("\nEnter your choice (1-2): "))
            if limit==1:
                time_MCTS = int(input("Insert time (seconds) limit for MCTS: "))
                break
            elif limit==2:
                max_rollout = int(input("Insert max rollout MCTSS: "))
                break
            print("Invalid choice.")

        while True:
            starter = input("\nWho starts? (A for MinMax, M for MCTS): ").upper()
            if starter in ["A", "M"]:
                break
            print("Enter A or M.")

        if starter == "A":
            game.to_play = minmax_player
        else:
            game.to_play = mcts_player

        while not game.game_over():

            game.print_board()

            if game.to_play == mcts_player:
                print("\nMCTS thinking...")

                if limit==1:
                    mcts.search_max_time(time_MCTS)
                else:
                    mcts.search_max_rollout(max_rollout)

                stats, num_rollouts, run_time = mcts.statistics()
                print(f"\nMCTS statistics ({num_rollouts} rollouts in {run_time:.2f}s):")

                for move, (wins, visits) in stats.items():
                    win_rate = wins / visits if visits > 0 else 0
                    print(f"Column {move}: {wins:.1f}/{visits} ({win_rate:.2%})")

                mcts_move = mcts.best_move()
                print(f"\nMCTS chooses column {mcts_move}")
                mcts.move(mcts_move)  

            else:
                print("\nMinMax thinking...")
                minmax = MinMax(game)
                start_time = time.perf_counter()
                minmax_move = minmax.get_best_move_alphabeta(depth_alphabeta, minmax_player, verbose=True)
                end_time = time.perf_counter()
                print(f"MinMax reasoned {(end_time-start_time):.4f}s. Nodes explored: {minmax.nodes_explored}")
                print(f"MinMax chooses column {minmax_move}")
                mcts.move(minmax_move)  

        winner = game.check_winner()
        
        if winner != None:  
            game.print_board_with_win()
        else:
            game.print_board()

        if winner == mcts_player:
            print("\nMCTS wins!\n")
        elif winner == minmax_player:
            print("\nMinMax wins!\n")
        else:
            print("\nTie!\n")


    elif choice == 4:   # Symbolic AI vs GPT
        
        print("\n===================================")
        print("Choose the Symbolic AI:")
        print("1. Monte Carlo Tree Search")
        print("2. MinMax")

        while True:
            symbolic_ai_type = int(input("\nEnter your choice (1-2): "))
            if symbolic_ai_type in [1, 2]:
                break
            print("Invalid choice.")

        if symbolic_ai_type==1:
            print("\nChoose the stopping criteria of MCTS:")
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
            depth_alphabeta = int(input("\nInsert max depth of Alpha-Beta: "))


        print("\n===================================")
        print("Choose the Large Language Model: ")
        print("1. OpenAi : o4 mini high")
        print("2. Anthropic : Claude 3.7 thinking")
        print("3. Gemini : Gemini 3 pro")

        while True:
            llm_type = int(input("\nEnter your choice (1-3): "))
            if llm_type in [1, 2, 3]:
                break
            print("Invalid choice.")

        if llm_type == 1:
            llm = "openai"
        elif llm_type == 2:
            llm = "claude"
        else:
            llm = "gemini"

        game = ConnectFour()
        
        symbolic_ai_player = game.player1
        llm_player = game.player2

        mcts = MCTS(game, ai_player=symbolic_ai_player)

        invalid_gpt_moves = 0
        gpt_move_call_count = 0
        llm_costs = []
        llm_times = []

      
        while True:
            print("\n=====================================================")
            starter = input("Who starts? (S for Symbolic AI, L for LLM): ").upper()
            if starter in ["S", "L"]:
                break
            print("Enter S or L.")

        game.to_play = symbolic_ai_player if starter == "S" else llm_player

        while not game.game_over():

            game.print_board()

            if game.to_play == symbolic_ai_player:

                if symbolic_ai_type == 1:  # MCTS turns
                    
                    print("\nMCST thinking...")
                    mcts.search_max_time(time_MCTS)
                    stats, num_rollouts, run_time = mcts.statistics()
                    print(f"\nMCST statistics ({num_rollouts} rollouts in {run_time:.2f}s):")

                    for move, (wins, visits) in stats.items():
                        win_rate = wins / visits if visits > 0 else 0
                        print(f"Column {move}: {wins:.1f}/{visits} ({win_rate:.2%})")

                    mcts_move = mcts.best_move()
                    print(f"\nMCST muove in colonna {mcts_move}")
                    mcts.move(mcts_move)  

                else: # minimax turn
                    
                    print("\nMinMax thinking...")
                    minmax = MinMax(game)

                    start_time = time.perf_counter()
                    minmax_move = minmax.get_best_move_alphabeta(depth_alphabeta, ai_player=symbolic_ai_player, verbose=False)
                    end_time = time.perf_counter()
                
                    print(f"AB reasoned {(end_time-start_time):.4f}s. Nodes explored: {minmax.nodes_explored}")  
                    print(f"Alpha-Beta chooses column {minmax_move}")

                    game.make_move(minmax_move, symbolic_ai_player)                

                
            else:  # LLM turn

                print("\nLLM thinking...")
                while True:
                    try:
                        start_time = time.perf_counter()
                        move_data = get_llm_move(llm, game) 
                        end_time = time.perf_counter()
                        
                        llm_move = move_data["column"]
                        llm_reason = move_data["reason"]
                        cost = move_data["cost"]

                        llm_costs.append(cost)
                        gpt_move_call_count += 1

                        if llm_move in game.available_moves():
                            llm_times.append(end_time-start_time)

                            print(f"LLM chooses column {llm_move}")
                            print(f"Reason: {llm_reason}")
                            print(f"LLM reasoned {(end_time-start_time):.4f}s")
                            print(f"Cost: {cost}")

                            if symbolic_ai_type == 1:
                                mcts.move(llm_move)  
                            else: 
                                game.make_move(llm_move, game.to_play)
                            break
                        else:
                            invalid_gpt_moves += 1
                            print(f"LLM proposed illegal move: {llm_move}, retrying...")
                    except Exception as e:
                            print(f"Error during the LLM call: {e}, retrying...")

                    
                    

        winner = game.check_winner()
        
        if winner != None:  
            game.print_board_with_win()
        else:
            game.print_board()

        if winner == symbolic_ai_player:
            print("\nSymbolic AI wins!\n")
        elif winner == llm_player:
            print("\nLLM wins!\n")
        else:
            print("\nTie!\n")

        print("GPT move call count:", gpt_move_call_count)
        print("Invalid GPT moves:", invalid_gpt_moves)

main()
