import heapq
import time


class Node:
    """Single node of the decision tree for the Knapsack problem."""

    def __init__(self, level, weight, value, path):
        self.level = level    # index of the item we are considering
        self.weight = weight  # accumulated weight
        self.value = value    # accumulated value : g(n)
        self.path = path      # list of decision [0, 1, ...] 
        self.f_cost = 0       # cost: f = g + h 

    
    def __lt__(self, other):
        """
        MAX-HEAP (sort by highest f_cost), so it returns True if self is "greater" than other.
        How the Priority Queue (heapq) sorts nodes
        """
        return self.f_cost > other.f_cost 


class BranchAndBound:

    def __init__(self, items, capacity):
        self.items = items  # list of items, where each item is (value, weight)
        self.capacity = capacity  # max capacity of the knapsack
        

    def calculate_heuristic(self, node):
        """
        Heuristic function (h): Fractional Knapsack 
        Compute the upper (optimistic) estimate of the value that can be obtained from the remaining objects.
        - node: current node with respect to compute the heuristic
        """
    
        # define the remaining_capacity of the knapsack
        remaining_capacity = self.capacity - node.weight
        h_value = 0
    
        # define for all remaining items their V/W ratio
        remaining_items_with_ratio = []
        for i in range(node.level, len(self.items)):
            weight, value = self.items[i]
            if weight > 0:
                ratio = value / weight
                remaining_items_with_ratio.append((weight, value, ratio))
    
        # sort them in decreasing order based on the ratio 
        remaining_items_with_ratio.sort(key=lambda x: x[2], reverse=True)
    
        # take all the possible whole items, and if there isn't enough space to take the whole item
        # take a fractional part of it to fully fill the knapsack
        for weight, value, ratio in remaining_items_with_ratio:
            if remaining_capacity == 0:
                break
            
            if weight <= remaining_capacity:
                # take the whole item 
                h_value += value
                remaining_capacity -= weight
            else:
                # take a fraction part of the item and set the remaining capacity to 0
                fraction = remaining_capacity / weight
                h_value += fraction * value
                remaining_capacity = 0
            
        return h_value

   
    def solve_knapsack(self):
        """Solve the Knapsack problem."""
    
        start_time = time.time()
        
        open_list = []  # priority queue: will contain the nodes not explored yet, ordered by f 
    
        best_value_found = 0
        best_solution_path = []

        nodes_expanded = 0
        
        # Root node: level 0, weight 0, value 0
        start_node = Node(level=0, weight=0, value=0, path=[])

        # Compute the f of the root:
        # it is only given by the heuristic h, since g is 0 at the start
        start_node.f_cost = self.calculate_heuristic(start_node)
    
        # push the root node in the priority queue
        heapq.heappush(open_list, start_node)
    
        # while there are nodes to be explored
        while open_list:

            # pop the most promising node (the one with higher f)
            current = heapq.heappop(open_list)

            nodes_expanded += 1


            # if the optimistic estimate f is worst than an already better solution found -> pruning
            if current.f_cost < best_value_found:
                continue  # don't explore this branch
            
            # if we have already considered all the items of the knapsack problem
            # so if we are at a leaf node
            if current.level == len(self.items):
                if current.value > best_value_found:
                    best_value_found = current.value
                    best_solution_path = current.path
                continue # there are no children to be explored

        
            item_weight, item_value = self.items[current.level]

            # branching : add 2 children, 1 considering taking the item, 1 leaving it

            # child 1: take the item 
            weight_with = current.weight + item_weight  # accumulate the total weight
             
            # if the new total weight is still below the max capacity add the node to the priority queue if it is promising
            if weight_with <= self.capacity:  

                path_with = current.path + [1]  
                node_with = Node(level=current.level + 1, 
                                weight=weight_with, 
                                value=current.value + item_value,   # accumulate the total value
                                path=path_with)
            
                # compute f = g + h
                g_cost = node_with.value
                h_cost = self.calculate_heuristic(node_with)
                node_with.f_cost = g_cost + h_cost
            
                # if the estimate is still promising, add it to the priority queue
                if node_with.f_cost > best_value_found:
                    heapq.heappush(open_list, node_with)

            # Child 2: leave the item
            # don't update the total weight and value, just go one level deep in the tree
            
            path_without = current.path + [0]
            node_without = Node(level=current.level + 1, 
                            weight=current.weight,   
                            value=current.value, 
                            path=path_without)
        
            # compute f = g + h
            g_cost = node_without.value
            h_cost = self.calculate_heuristic(node_without)
            node_without.f_cost = g_cost + h_cost
        
            # if the estimate is still promising, add it to the priority queue
            if node_without.f_cost > best_value_found:
                heapq.heappush(open_list, node_without)

        end_time = time.time()
        time_run = (end_time-start_time)

        return best_value_found, best_solution_path, nodes_expanded, time_run


# knapsack problem instance
ITEMS = [(485, 585), (94, 194), (326, 426), (506, 606), (248, 348), (416, 516), (421, 521), (992, 1092), (322, 422), (649, 749), (795, 895), (237, 337), (43, 143), (457, 557), (845, 945), (815, 915), (955, 1055), (446, 546), (252, 352), (422, 522), (9, 109), (791, 891), (901, 1001), (359, 459), (122, 222), (667, 767), (94, 194), (598, 698), (738, 838), (7, 107), (574, 674), (544, 644), (715, 815), (334, 434), (882, 982), (766, 866), (367, 467), (994, 1094), (984, 1084), (893, 993), (299, 399), (633, 733), (433, 533), (131, 231), (682, 782), (428, 528), (72, 172), (700, 800), (874, 974), (617, 717), (138, 238), (874, 974), (856, 956), (720, 820), (145, 245), (419, 519), (995, 1095), (794, 894), (529, 629), (196, 296), (199, 299), (997, 1097), (277, 377), (116, 216), (97, 197), (908, 1008), (719, 819), (539, 639), (242, 342), (707, 807), (107, 207), (569, 669), (122, 222), (537, 637), (70, 170), (931, 1031), (98, 198), (726, 826), (600, 700), (487, 587), (645, 745), (772, 872), (267, 367), (513, 613), (972, 1072), (81, 181), (895, 995), (943, 1043), (213, 313), (58, 158), (748, 848), (303, 403), (487, 587), (764, 864), (923, 1023), (536, 636), (29, 129), (724, 824), (674, 774), (789, 889), (540, 640), (479, 579), (554, 654), (142, 242), (467, 567), (339, 439), (46, 146), (641, 741), (710, 810), (196, 296), (553, 653), (494, 594), (191, 291), (66, 166), (724, 824), (824, 924), (730, 830), (208, 308), (988, 1088), (711, 811), (90, 190), (800, 900), (340, 440), (314, 414), (549, 649), (289, 389), (196, 296), (401, 501), (865, 965), (466, 566), (678, 778), (689, 789), (570, 670), (833, 933), (936, 1036), (225, 325), (722, 822), (244, 344), (651, 751), (849, 949), (123, 223), (113, 213), (431, 531), (379, 479), (508, 608), (361, 461), (585, 685), (65, 165), (853, 953), (486, 586), (642, 742), (686, 786), (992, 1092), (286, 386), (725, 825), (889, 989), (286, 386), (24, 124), (812, 912), (491, 591), (859, 959), (891, 991), (663, 763), (90, 190), (88, 188), (181, 281), (179, 279), (214, 314), (187, 287), (17, 117), (619, 719), (472, 572), (261, 361), (418, 518), (846, 946), (419, 519), (192, 292), (356, 456), (261, 361), (682, 782), (514, 614), (306, 406), (886, 986), (201, 301), (530, 630), (385, 485), (849, 949), (952, 1052), (294, 394), (500, 600), (799, 899), (194, 294), (391, 491), (737, 837), (330, 430), (324, 424), (298, 398), (992, 1092), (790, 890), (224, 324), (275, 375), (260, 360), (826, 926), (97, 197), (72, 172), (210, 310), (866, 966), (649, 749), (951, 1051), (919, 1019), (748, 848), (63, 163), (685, 785), (958, 1058), (956, 1056), (804, 904), (564, 664), (518, 618), (183, 283), (428, 528), (400, 500), (537, 637), (721, 821), (346, 446), (207, 307), (153, 253), (323, 423), (971, 1071), (611, 711), (662, 762), (116, 216), (197, 297), (109, 209), (91, 191), (795, 895), (529, 629), (343, 443), (126, 226), (862, 962), (747, 847), (685, 785), (469, 569), (10, 110), (770, 870), (881, 981), (934, 1034), (984, 1084), (723, 823), (403, 503), (895, 995), (360, 460), (568, 668), (449, 549), (172, 272), (541, 641), (958, 1058), (272, 372), (383, 483), (877, 977), (308, 408), (359, 459), (970, 1070), (707, 807), (583, 683), (308, 408), (48, 148), (770, 870), (930, 1030), (30, 130), (569, 669), (208, 308), (3, 103), (311, 411), (20, 120), (100, 200), (609, 709), (939, 1039), (887, 987), (422, 522), (825, 925), (785, 885), (930, 1030), (370, 470), (904, 1004), (989, 1089), (241, 341), (969, 1069), (379, 479), (143, 243), (376, 476), (972, 1072), (962, 1062), (28, 128), (889, 989), (61, 161), (443, 543), (638, 738), (216, 316), (348, 448), (338, 438), (347, 447), (160, 260), (66, 166), (406, 506), (391, 491), (159, 259), (638, 738), (31, 131), (295, 395), (204, 304), (826, 926), (420, 520), (196, 296), (153, 253), (449, 549), (425, 525), (855, 955), (331, 431), (143, 243), (565, 665), (487, 587), (838, 938), (140, 240), (9, 109), (564, 664), (918, 1018), (615, 715), (533, 633), (135, 235), (232, 332), (564, 664), (957, 1057), (360, 460), (591, 691), (793, 893), (576, 676), (163, 263), (746, 846), (859, 959), (377, 477), (760, 860), (858, 958), (711, 811), (86, 186), (662, 762), (434, 534), (159, 259), (558, 658), (660, 760), (279, 379), (268, 368), (840, 940), (948, 1048), (735, 835), (315, 415), (574, 674), (676, 776), (126, 226), (341, 441), (912, 1012), (689, 789), (739, 839), (894, 994), (821, 921), (706, 806), (625, 725), (490, 590), (917, 1017), (478, 578), (201, 301), (671, 771), (993, 1093), (932, 1032), (149, 249), (899, 999), (52, 152), (237, 337), (759, 859), (187, 287), (267, 367), (472, 572), (256, 356), (772, 872), (783, 883), (98, 198), (117, 217), (906, 1006), (516, 616), (911, 1011), (180, 280), (635, 735), (25, 125), (225, 325), (380, 480), (823, 923), (712, 812), (164, 264), (266, 366), (343, 443), (216, 316), (732, 832), (448, 548), (502, 602), (541, 641), (740, 840), (664, 764), (576, 676), (954, 1054), (612, 712), (726, 826), (902, 1002), (772, 872), (454, 554), (531, 631), (411, 511), (943, 1043), (973, 1073), (750, 850), (703, 803), (327, 427), (850, 950), (917, 1017), (77, 177), (5, 105), (220, 320), (113, 213), (802, 902), (913, 1013), (403, 503), (791, 891), (181, 281), (998, 1098), (10, 110), (859, 959), (525, 625), (345, 445), (919, 1019), (431, 531), (668, 768), (675, 775), (527, 627), (833, 933), (462, 562), (438, 538), (291, 391), (523, 623), (605, 705), (916, 1016), (457, 557), (420, 520), (405, 505), (115, 215), (417, 517), (660, 760), (279, 379), (261, 361), (685, 785), (772, 872), (596, 696), (388, 488), (307, 407), (764, 864), (224, 324), (843, 943), (322, 422), (206, 306), (840, 940), (407, 507), (975, 1075), (639, 739), (401, 501), (852, 952), (91, 191), (542, 642), (327, 427), (60, 160), (330, 430), (757, 857), (182, 282), (82, 182), (603, 703), (637, 737), (793, 893), (93, 193), (615, 715), (614, 714), (733, 833), (136, 236), (864, 964), (187, 287), (16, 116), (102, 202), (863, 963), (972, 1072), (987, 1087), (163, 263), (306, 406), (501, 601), (34, 134), (477, 577)]
KNAPSACK_CAPACITY = 2517
OPTIMAL_FITNESS = 7117
NUM_ITEMS = 500

if __name__ == "__main__":

    print("Starting A* (Branch and Bound) ...")

    a_star = BranchAndBound(ITEMS, KNAPSACK_CAPACITY)
    
    (best_value, best_path, nodes, time_run) = a_star.solve_knapsack()
    
    print("\n======================= Result A* =======================")
    print(f"Total node expanded: {nodes}")
    print(f"Best solution found: {best_value}")
    print(f"Time: {time_run:.4f}s")
    
    full_solution_path = best_path + [0] * (NUM_ITEMS - len(best_path))
    
    #print(f"Solution (cromosome): {full_solution_path}")