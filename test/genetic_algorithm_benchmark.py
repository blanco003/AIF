import time
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from genetic_algorithm import * 

n = int(input("Number of runs: "))

solutions = []
times = []

# configuration of hyper-parameters
pop_size = 250
mutation_rate = 0.001
selection_method_name = "Roulette"
crossover_rate = 0.6
max_gens = 600
tournament_k = 0

for i in range(n):
    print(f"\n----------------------Iteration {i+1}/{n}----------------------")

    gen_alg = GeneticAlgorithm(
                items=ITEMS,
                capacity=KNAPSACK_CAPACITY,
                population_size=pop_size,
                mutation_rate=mutation_rate,
                selection_method=selection_method_name,
                crossover_rate=crossover_rate,
                tournament_k=tournament_k)
    
    start = time.time()
    fitness_history, best_fitness = gen_alg.run_experiment_config(max_gens, plot=False)
    end = time.time()

    print(f"Best fitness : {best_fitness}")
    print(f"Time : {(end-start):.4f}s")

    times.append(end-start)
    solutions.append(best_fitness)

avg_time = sum(times)/n
avg_best_fitness = sum(solutions)/n

print("\n------------------Final Statistics-----------------------")
print(f"Avg Best fitness : {avg_best_fitness}")
print(f"Avg Time : {(avg_time):.4f}s")
