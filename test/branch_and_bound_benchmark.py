import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from branch_and_bound import *

n = int(input("Number of runs: "))

best_values, times = [], []

for i in range(n):
    print(f"\n----------------------Iteration {i+1}/{n}----------------------")
    a_star = BranchAndBound(ITEMS, KNAPSACK_CAPACITY)
    (best_value, best_path, nodes, time_run) = a_star.solve_knapsack()

    best_values.append(best_value)
    times.append(time_run)
    print(f"Total node expanded: {nodes}")
    print(f"Best optimal value found: {best_value}")
    print(f"Time: {time_run:.4f}s")

print("\n------------------Final Statistics-----------------------")

avg_best_value = (sum(best_values)/n)
avg_time = (sum(times)/n)

print(f"Avg Best value : {avg_best_value}")
print(f"Avg Time : {avg_time:.4f}s")
