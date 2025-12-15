import random
import matplotlib.pyplot as plt
import numpy as np

class GeneticAlgorithm:

    def __init__(self, items, capacity, population_size, mutation_rate, selection_method, crossover_rate, tournament_k=None):
        
        # knapsack problem data
        self.items = items
        self.capacity = capacity

        # hyper parameters of the genetic algorithm
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.selection_method = selection_method
        self.crossover_rate = crossover_rate
        self.tournament_k = tournament_k

        self.population = []
        self.fitness_scores = []
        self.best_solution = 0
        self.history = []


    def inizialize_population(self):
        """Initialize the population of population_size number of individuals."""
        self.population = []
        PROB_TO_TAKE = 0.015   # probability of a gene of the individual to be 1

        for _ in range(self.population_size):
            individual = [1 if random.random() < PROB_TO_TAKE else 0 for _ in range(len(self.items))]
            self.population.append(individual)


    def calculate_fitness(self, individual):
        """
        Calculate the fitness of a given individual as the sum of the value of the corresponding items picked.
        If the fitness exceeds the knapsack capacity the fitness is set to 0 so that the individual gets discarded.
        """
        total_value = 0
        total_weight = 0

        for i in range(len(individual)):
            if individual[i] == 1:
                total_value += self.items[i][1]
                total_weight += self.items[i][0]

        if total_weight > self.capacity:
            return 0
        
        return total_value


    def parent_selection_roulette(self):
        """
        Perform a Roulette Selection, returning the elected individual, which will be a parent.
        """

        total_fitness_sum = sum(self.fitness_scores)

        # if the total fitness of the population is 0 just return a random individual
        if total_fitness_sum == 0:
            return self.population[random.randint(0, len(self.population) - 1)]
        
        pick = random.uniform(0, total_fitness_sum) 
        current_sum = 0

        for i in range(len(self.population)):
            current_sum += self.fitness_scores[i]
            if current_sum > pick:
                return self.population[i]
            
        # fallback
        return self.population[-1]


    def parent_selection_tournament(self):
        """
        Perform a Tournament Selection, returning the elected individual, which will be a parent.
        """

        # select randomly the k individual which will compete in the tournament
        tournament_indices = random.sample(range(len(self.population)), self.tournament_k)

        best_idx = -1
        best_fit = -1
        
        # find the individual with the best fitness
        for idx in tournament_indices:
            if self.fitness_scores[idx] > best_fit:
                best_fit = self.fitness_scores[idx]
                best_idx = idx

        return self.population[best_idx]

    def crossover(self, parent_one, parent_two):
        """
        Perform the crossover operation. Given the two parents, perform a 1-point random crossover 
        and return the two offsprings.
        """
        k = random.randint(0, len(self.items) - 2)
        offspring_one = parent_one[0:k] + parent_two[k:]
        offspring_two = parent_two[0:k] + parent_one[k:]
        return (offspring_one, offspring_two)


    def mutation(self, individual):
        """
        Perform the mutation of the given individual. Each gene of the individual has a probability to switch.
        """

        new_ind = individual[:] 

        for i in range(len(new_ind)):
            if random.random() < self.mutation_rate:
                new_ind[i] = 1 - new_ind[i]

        return new_ind


    def run_experiment_config(self, max_generation, plot=False):
        """
        Perform the genetic algorithm.
        """

        # 1) initialize population 
        self.inizialize_population()

        # 2) compute the fitness of the population
        self.fitness_scores = [self.calculate_fitness(individual) for individual in self.population]
        best_global_fitness = max(self.fitness_scores)
        best_idx = self.fitness_scores.index(best_global_fitness)
        best_global_solution = self.population[best_idx][:]

        fitness_history = []

        # until reaching the max generation
        for generation in range(max_generation):

            fitness_history.append(best_global_fitness)

            new_population = []

            # elitism: copy the best individual of the previous generartion directly in to the new one
            new_population.append(best_global_solution[:]) 

            # untill fully filling the new population
            while len(new_population) < self.population_size:

                # 3) select 2 parents
                if self.selection_method == "Roulette":
                    p1 = self.parent_selection_roulette()
                    p2 = self.parent_selection_roulette()
                else: 
                    p1 = self.parent_selection_tournament()
                    p2 = self.parent_selection_tournament()

                # 4) crossover to generate the offsprings
                if random.random() < self.crossover_rate:
                    o1, o2 = self.crossover(p1, p2)
                else:
                    o1, o2 = p1.copy(), p2.copy()

                # 5) mutation of the offsprings
                o1 = self.mutation(o1)
                o2 = self.mutation(o2)

                new_population.append(o1)
                if len(new_population) < self.population_size:
                    new_population.append(o2)
        
            self.population = new_population[:self.population_size]
        
            self.fitness_scores = [self.calculate_fitness(individual) for individual in self.population]
            current_best = max(self.fitness_scores)

            # update the best solution found so far
            if current_best > best_global_fitness:
                best_global_fitness = current_best
                best_idx = self.fitness_scores.index(current_best)
                best_global_solution = self.population[best_idx][:]
                self.best_solution = best_global_solution[:]

        self.best_solution = best_global_solution[:]

        if plot:
            self.plot_single_run(fitness_history)

        return fitness_history, best_global_fitness
    
    
    def plot_single_run(self, fitness_history):
        """
        Plot the fitness history of the genetic algorithm through the generations.
        """
        gens = np.arange(len(fitness_history))
    
        plt.figure(figsize=(10,6))
        plt.plot(gens, fitness_history, label='Fitness for generation', linewidth=2)
    
        plt.title("Fitness Convergence")
        plt.xlabel("Generation")
        plt.ylabel("Fitness")
        plt.grid(True)
        plt.legend()
        plt.show()


# knapsack problem instance
ITEMS = [(485, 585), (94, 194), (326, 426), (506, 606), (248, 348), (416, 516), (421, 521), (992, 1092), (322, 422), (649, 749), (795, 895), (237, 337), (43, 143), (457, 557), (845, 945), (815, 915), (955, 1055), (446, 546), (252, 352), (422, 522), (9, 109), (791, 891), (901, 1001), (359, 459), (122, 222), (667, 767), (94, 194), (598, 698), (738, 838), (7, 107), (574, 674), (544, 644), (715, 815), (334, 434), (882, 982), (766, 866), (367, 467), (994, 1094), (984, 1084), (893, 993), (299, 399), (633, 733), (433, 533), (131, 231), (682, 782), (428, 528), (72, 172), (700, 800), (874, 974), (617, 717), (138, 238), (874, 974), (856, 956), (720, 820), (145, 245), (419, 519), (995, 1095), (794, 894), (529, 629), (196, 296), (199, 299), (997, 1097), (277, 377), (116, 216), (97, 197), (908, 1008), (719, 819), (539, 639), (242, 342), (707, 807), (107, 207), (569, 669), (122, 222), (537, 637), (70, 170), (931, 1031), (98, 198), (726, 826), (600, 700), (487, 587), (645, 745), (772, 872), (267, 367), (513, 613), (972, 1072), (81, 181), (895, 995), (943, 1043), (213, 313), (58, 158), (748, 848), (303, 403), (487, 587), (764, 864), (923, 1023), (536, 636), (29, 129), (724, 824), (674, 774), (789, 889), (540, 640), (479, 579), (554, 654), (142, 242), (467, 567), (339, 439), (46, 146), (641, 741), (710, 810), (196, 296), (553, 653), (494, 594), (191, 291), (66, 166), (724, 824), (824, 924), (730, 830), (208, 308), (988, 1088), (711, 811), (90, 190), (800, 900), (340, 440), (314, 414), (549, 649), (289, 389), (196, 296), (401, 501), (865, 965), (466, 566), (678, 778), (689, 789), (570, 670), (833, 933), (936, 1036), (225, 325), (722, 822), (244, 344), (651, 751), (849, 949), (123, 223), (113, 213), (431, 531), (379, 479), (508, 608), (361, 461), (585, 685), (65, 165), (853, 953), (486, 586), (642, 742), (686, 786), (992, 1092), (286, 386), (725, 825), (889, 989), (286, 386), (24, 124), (812, 912), (491, 591), (859, 959), (891, 991), (663, 763), (90, 190), (88, 188), (181, 281), (179, 279), (214, 314), (187, 287), (17, 117), (619, 719), (472, 572), (261, 361), (418, 518), (846, 946), (419, 519), (192, 292), (356, 456), (261, 361), (682, 782), (514, 614), (306, 406), (886, 986), (201, 301), (530, 630), (385, 485), (849, 949), (952, 1052), (294, 394), (500, 600), (799, 899), (194, 294), (391, 491), (737, 837), (330, 430), (324, 424), (298, 398), (992, 1092), (790, 890), (224, 324), (275, 375), (260, 360), (826, 926), (97, 197), (72, 172), (210, 310), (866, 966), (649, 749), (951, 1051), (919, 1019), (748, 848), (63, 163), (685, 785), (958, 1058), (956, 1056), (804, 904), (564, 664), (518, 618), (183, 283), (428, 528), (400, 500), (537, 637), (721, 821), (346, 446), (207, 307), (153, 253), (323, 423), (971, 1071), (611, 711), (662, 762), (116, 216), (197, 297), (109, 209), (91, 191), (795, 895), (529, 629), (343, 443), (126, 226), (862, 962), (747, 847), (685, 785), (469, 569), (10, 110), (770, 870), (881, 981), (934, 1034), (984, 1084), (723, 823), (403, 503), (895, 995), (360, 460), (568, 668), (449, 549), (172, 272), (541, 641), (958, 1058), (272, 372), (383, 483), (877, 977), (308, 408), (359, 459), (970, 1070), (707, 807), (583, 683), (308, 408), (48, 148), (770, 870), (930, 1030), (30, 130), (569, 669), (208, 308), (3, 103), (311, 411), (20, 120), (100, 200), (609, 709), (939, 1039), (887, 987), (422, 522), (825, 925), (785, 885), (930, 1030), (370, 470), (904, 1004), (989, 1089), (241, 341), (969, 1069), (379, 479), (143, 243), (376, 476), (972, 1072), (962, 1062), (28, 128), (889, 989), (61, 161), (443, 543), (638, 738), (216, 316), (348, 448), (338, 438), (347, 447), (160, 260), (66, 166), (406, 506), (391, 491), (159, 259), (638, 738), (31, 131), (295, 395), (204, 304), (826, 926), (420, 520), (196, 296), (153, 253), (449, 549), (425, 525), (855, 955), (331, 431), (143, 243), (565, 665), (487, 587), (838, 938), (140, 240), (9, 109), (564, 664), (918, 1018), (615, 715), (533, 633), (135, 235), (232, 332), (564, 664), (957, 1057), (360, 460), (591, 691), (793, 893), (576, 676), (163, 263), (746, 846), (859, 959), (377, 477), (760, 860), (858, 958), (711, 811), (86, 186), (662, 762), (434, 534), (159, 259), (558, 658), (660, 760), (279, 379), (268, 368), (840, 940), (948, 1048), (735, 835), (315, 415), (574, 674), (676, 776), (126, 226), (341, 441), (912, 1012), (689, 789), (739, 839), (894, 994), (821, 921), (706, 806), (625, 725), (490, 590), (917, 1017), (478, 578), (201, 301), (671, 771), (993, 1093), (932, 1032), (149, 249), (899, 999), (52, 152), (237, 337), (759, 859), (187, 287), (267, 367), (472, 572), (256, 356), (772, 872), (783, 883), (98, 198), (117, 217), (906, 1006), (516, 616), (911, 1011), (180, 280), (635, 735), (25, 125), (225, 325), (380, 480), (823, 923), (712, 812), (164, 264), (266, 366), (343, 443), (216, 316), (732, 832), (448, 548), (502, 602), (541, 641), (740, 840), (664, 764), (576, 676), (954, 1054), (612, 712), (726, 826), (902, 1002), (772, 872), (454, 554), (531, 631), (411, 511), (943, 1043), (973, 1073), (750, 850), (703, 803), (327, 427), (850, 950), (917, 1017), (77, 177), (5, 105), (220, 320), (113, 213), (802, 902), (913, 1013), (403, 503), (791, 891), (181, 281), (998, 1098), (10, 110), (859, 959), (525, 625), (345, 445), (919, 1019), (431, 531), (668, 768), (675, 775), (527, 627), (833, 933), (462, 562), (438, 538), (291, 391), (523, 623), (605, 705), (916, 1016), (457, 557), (420, 520), (405, 505), (115, 215), (417, 517), (660, 760), (279, 379), (261, 361), (685, 785), (772, 872), (596, 696), (388, 488), (307, 407), (764, 864), (224, 324), (843, 943), (322, 422), (206, 306), (840, 940), (407, 507), (975, 1075), (639, 739), (401, 501), (852, 952), (91, 191), (542, 642), (327, 427), (60, 160), (330, 430), (757, 857), (182, 282), (82, 182), (603, 703), (637, 737), (793, 893), (93, 193), (615, 715), (614, 714), (733, 833), (136, 236), (864, 964), (187, 287), (16, 116), (102, 202), (863, 963), (972, 1072), (987, 1087), (163, 263), (306, 406), (501, 601), (34, 134), (477, 577)]
KNAPSACK_CAPACITY = 2517
OPTIMAL_FITNESS = 7117
NUM_ITEMS = 500

if __name__ == "__main__":

    print(f"======== Starting Grid Search (Pop, Mut, Sel, Cross, Tourn_K) ========")
    
    # perform a grid search to find the best configuration of hyper-parameters

    GRID_PARAMETERS = {
        "pop_size": [100, 250],
        "mutation_rate": [0.001, 0.01],
        "selection_method": ["Roulette", "Tournament"],
        "crossover_rate": [0.6, 0.9],
        "tournament_k": [3, 5, 10] 
    }
    
    NUM_REPEATS_PER_CONFIG = 3 
    MAX_GENS_PER_RUN = 600     
    
    
    all_results = []
    run_counter = 0

    for pop in GRID_PARAMETERS["pop_size"]:
        for mut in GRID_PARAMETERS["mutation_rate"]:
            for cross in GRID_PARAMETERS["crossover_rate"]:
                for sel in GRID_PARAMETERS["selection_method"]:
                    
                    # if selection method is Roluette -> k = None
                    # otherwise iterate on k values
                    current_k_values = [None] if sel == "Roulette" else GRID_PARAMETERS["tournament_k"]
                    
                    for k_val in current_k_values:
                        
                        if sel == "Roulette":
                            config_key = f"P={pop}, M={mut}, C={cross}, S={sel}"
                            current_k_arg = None
                        else:
                            config_key = f"P={pop}, M={mut}, C={cross}, S={sel}(k={k_val})"
                            current_k_arg = k_val

                        run_counter += 1
                        print(f"Run {run_counter}: {config_key}")
                        
                        histories = []
                        final_scores = []
                        
                        for i in range(NUM_REPEATS_PER_CONFIG):

                            gen_alg = GeneticAlgorithm(
                                items=ITEMS,
                                capacity=KNAPSACK_CAPACITY,
                                population_size=pop,
                                mutation_rate=mut,
                                selection_method=sel,
                                crossover_rate=cross,
                                tournament_k=current_k_arg)

                            hist, final_fit = gen_alg.run_experiment_config(MAX_GENS_PER_RUN)

                            histories.append(hist)
                            final_scores.append(final_fit)
                        
                        avg_history = np.mean(histories, axis=0)
                        std_history = np.std(histories, axis=0)     
                        avg_final_score = np.mean(final_scores)
                        std_final_score = np.std(final_scores)

                        all_results.append({
                            "config": config_key,
                            "history_mean": avg_history,
                            "history_std": std_history,             
                            "score": avg_final_score,
                            "std": std_final_score
                        })

    print("\n======== Grid search completed ========")
    
    # sort configs in descending based on score
    all_results.sort(key=lambda x: x["score"], reverse=True)

    # create a markdown report to save the results
    print("Creating 'grid_search_report.md'...")

    report_content = f""
    "# Report Grid Search Estesa (con Tournament K)"
    "**Known optimum:** {OPTIMAL_FITNESS}"
    "## Ranking ({len(all_results)} configs)"
    "| Rank | Configurazione | Fitness Media | Dev. Std |"
    "| :--- | :--- | :--- | :--- |"

    for i, res in enumerate(all_results):
        report_content += f"| {i+1} | {res['config']} | **{res['score']:.2f}** | {res['std']:.2f} |\n"
        
    with open("grid_search_report.md", "w", encoding='utf-8') as f:
        f.write(report_content)

    print("Creating 'convergence_lines.png'...")
    
    plt.figure(figsize=(14, 8))
    
    # plot top 5 configs
    for i in range(min(5, len(all_results))):
        res = all_results[i]
        mean = res['history_mean']
        std  = res['history_std']
        gens = np.arange(len(mean))

        plt.plot(gens, mean, linewidth=2, label=f"Rank {i+1}: {res['config']}")
        plt.fill_between(gens, mean - std, mean + std, alpha=0.2)   
        

    # known optimum line
    plt.axhline(y=OPTIMAL_FITNESS, color='r', linestyle=':', linewidth=2, label='Known Optimum')

    plt.title(f'Convergence curves: Top 5 Config (Avg on {NUM_REPEATS_PER_CONFIG} run)', fontsize=16)
    plt.xlabel('Generations', fontsize=12)
    plt.ylabel('Avg. Fitness', fontsize=12)
    plt.legend(loc='lower right', fontsize='small') 
    plt.grid(True)
    plt.savefig("convergence_lines.png")
