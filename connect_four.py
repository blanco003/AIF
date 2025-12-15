class ConnectFour:
    
    def __init__(self, rows=6, columns=7):
        """Initialize empty board (7 columns x 6 rows)"""
        self.rows = rows
        self.columns = columns
        self.board = [[" " for _ in range(self.columns)] for _ in range(self.rows)] # empty pieces
        self.player1 = "O" 
        self.player2 = "X"  
        self.to_play = self.player2  # symbol of the player to move next

    def print_board(self):
        """Print the current state of the board"""

        print("\n" + " " + "-" * (self.columns * 4 - 1))
        for r in range(self.rows):
            print("| " + " | ".join(self.board[r]) + " |")
            if r != self.rows - 1:
                print("|" + "-" * (self.columns * 4 - 1) + "|")
        print(" " + "-" * (self.columns * 4 - 1))

    def available_moves(self):
        """Returns list of available moves (indices of non-full columns)"""
        moves = []
        for j in range(self.columns):
            if self.board[0][j] == " ":
                moves.append(j)
        return moves

    def make_move(self, column, player):
        """Place player's piece in the column and switch player to move next"""
        for i in range(self.rows - 1, -1, -1):
            if self.board[i][column] == " ":
                self.board[i][column] = player
                # swap turn
                self.to_play = self.player2 if self.to_play == self.player1 else self.player1
                return True
        return False

    def is_board_full(self):
        """Check if the board is full"""
        return all(self.board[0][j] != " " for j in range(self.columns))

    def check_winner(self):
        """Check if there is a winner."""

        # horizontal
        for i in range(self.rows):
            for j in range(self.columns - 3):
                player = self.board[i][j]
                if player != " " and all(player == self.board[i][j+k] for k in range(4)):
                    return player

        # vertical
        for j in range(self.columns):
            for i in range(self.rows - 3):
                player = self.board[i][j]
                if player != " " and all(player == self.board[i+k][j] for k in range(4)):
                    return player

        # diagonal (\)
        for i in range(self.rows - 3):
            for j in range(self.columns - 3):
                player = self.board[i][j]
                if player != " " and all(player == self.board[i+k][j+k] for k in range(4)):
                    return player

        # diagonal (/)
        for i in range(3, self.rows):
            for j in range(self.columns - 3):
                player = self.board[i][j]
                if player != " " and all(player == self.board[i-k][j+k] for k in range(4)):
                    return player

        return None

    def game_over(self):
        """Check if the game is over, either because there is a winner or is a tie."""
        return self.check_winner() is not None or self.is_board_full()
    
    def make_temporary_move(self, column, player):
        """
        Performs the specified move (column) and returns the row index corresponding to the height (row)
        where the token was placed.
        Useful together with undo_move to reason with Minmax/MCTS and make temporary moves that can
        be undone, to don't alter the actual game board, or create a deepcopy every time.
        """
        for i in range(self.rows - 1, -1, -1):
            if self.board[i][column] == " ":
                self.board[i][column] = player
                return i
            
        return None  # column full

    def undo_move(self, column, row):
        """
        Removes the token in the specified column and row.
        """
        if row is not None:
            self.board[row][column] = " "

    def get_outcome(self):
        """
        If the board is in a terminal state, it returns the winner or 0 if there is a tie.
        Otherwise, if the board is in an intermediate state, it returns None.
        """
        winner = self.check_winner()
        
        if winner is not None:
            return winner
        
        if self.is_board_full():
            return 0
        
        return None
    

    def print_board_with_win(self):
        """
        Print the board highlighting the winning pieces in green.
        """
        GREEN = '\033[92m'
        RESET = '\033[0m'
        
        winning_coords = [] 
        found = False
        
        # horizontal
        if not found:
            for i in range(self.rows):
                for j in range(self.columns - 3):
                    p = self.board[i][j]
                    if p != " " and all(p == self.board[i][j+k] for k in range(4)):
                        winning_coords = [(i, j+k) for k in range(4)]
                        found = True; break
                if found: break

        # vertical
        if not found:
            for j in range(self.columns):
                for i in range(self.rows - 3):
                    p = self.board[i][j]
                    if p != " " and all(p == self.board[i+k][j] for k in range(4)):
                        winning_coords = [(i+k, j) for k in range(4)]
                        found = True; break
                if found: break

        # diagonal (\)
        if not found:
            for i in range(self.rows - 3):
                for j in range(self.columns - 3):
                    p = self.board[i][j]
                    if p != " " and all(p == self.board[i+k][j+k] for k in range(4)):
                        winning_coords = [(i+k, j+k) for k in range(4)]
                        found = True; break
                if found: break

        # diagonal (/)
        if not found:
            for i in range(3, self.rows):
                for j in range(self.columns - 3):
                    p = self.board[i][j]
                    if p != " " and all(p == self.board[i-k][j+k] for k in range(4)):
                        winning_coords = [(i-k, j+k) for k in range(4)]
                        found = True; break
                if found: break

        
        print("\n" + " " + "-" * (self.columns * 4 - 1))
        for r in range(self.rows):
            row_str_list = []
            for c in range(self.columns):
                cell = self.board[r][c]
                
                if (r, c) in winning_coords:
                    row_str_list.append(f"{GREEN}{cell}{RESET}")
                else:
                    row_str_list.append(cell)
            
            print("| " + " | ".join(row_str_list) + " |")
            if r != self.rows - 1:
                print("|" + "-" * (self.columns * 4 - 1) + "|")
        print(" " + "-" * (self.columns * 4 - 1))

    
###################################################################################################################
# Heuristic evaluation

    def evaluate_board(self, player):
        """Return the heuristic evaluation of the current board from the specified player point of view."""

        opponent = self.player1 if player == self.player2 else self.player2
        score = 0

        """
        Positional Weighting: 
        Each token adds a score based on its column. Opposing pieces subtract the same score.
        Idea: Controlling the center gives you more chances of 4-in-a-row; the outer columns are less strategic.
        """ 
        col_weights = [40, 70, 120, 200, 120, 70, 40]

        for r in range(self.rows):
            for c in range(self.columns):
                if self.board[r][c] == player:
                    score += col_weights[c]
                elif self.board[r][c] == opponent:
                    score -= col_weights[c]
       
        """
        Pattern-based evaluation:
        The board is scanned for every possible set of 4 consecutive cells (windows) in horizontal, 
        vertical, and diagonal directions.
        """
        # horizontal
        for r in range(self.rows):
            for c in range(self.columns - 3):
                coords = [(r, c+i) for i in range(4)]
                score += self.evaluate_single_window(coords, player, opponent)

        # vertical
        for c in range(self.columns):
            for r in range(self.rows - 3):
                coords = [(r+i, c) for i in range(4)]
                score += self.evaluate_single_window(coords, player, opponent)

        # diagonal (\)
        for r in range(self.rows - 3):
            for c in range(self.columns - 3):
                coords = [(r+i, c+i) for i in range(4)]
                score += self.evaluate_single_window(coords, player, opponent)

        # diagonal (/)
        for r in range(3, self.rows):
            for c in range(self.columns - 3):
                coords = [(r-i, c+i) for i in range(4)]
                score += self.evaluate_single_window(coords, player, opponent)

        return score
    

    def evaluate_single_window(self, coords, player, opponent):
        """
        Evaluate a single window of 4 consecutive cell.
        - coords: coordinates of the 4 cell of the window : (r_i, c_i)
        """
        window = [self.board[r][c] for (r, c) in coords]   # get the corresponding tokens
        p = window.count(player)
        o = window.count(opponent)
        e = window.count(" ")
        score = 0
        """
        If a window has 4 consecutive player tokens it is an immediate win -> + infinite score
        If a window has 4 consecutive opponent's pieces of the player it is an immediate defeat -> - infinite score
        """
        if p == 4:
            return float("inf")
        if o == 4:
            return float("-inf")
        
        """
        If a window has 3 player tokens and one empty cell: count how many free ends.
        2 open ends -> double threat -> inevitable victory -> + inf
        1 open end -> high chance to win
        Same for the opponent player, with negative scores
        """
        if p == 3 and e == 1:
            open_sides = self.count_open_ends(coords)
            if open_sides == 2:
                return float("inf")
            score += 900000

        if o == 3 and e == 1:
            open_sides = self.count_open_ends(coords)
            if open_sides == 2:
                return float("-inf")
            score -= 900000

        """
        If a window has 2 player tokens and 2 empty cells: count how many free ends.
        If both ends are free -> good chance to win
        If only 1 end: count the  extendability and assigns a decreasing score.
        Same for the opponent with a negative sign.
        """
        if p == 2 and e == 2:
            open_sides = self.count_open_ends(coords)
            if open_sides == 2:
                score += 50000
            elif open_sides == 1:
                ext = self.extendability(coords)
                score += self.score_extendability(ext)

        if o == 2 and e == 2:
            open_sides = self.count_open_ends(coords)
            if open_sides == 2:
                score -= 50000
            elif open_sides == 1:
                ext = self.extendability(coords)
                score -= self.score_extendability(ext)

        return score
    
    def count_open_ends(self, coords):
        """
        Counts how many open sides a window of 4 consecutive cells has. 
        Returns 2 if both sides are open, 1 if only one side is open, 0 otherwise.
        """
        (r1, c1) = coords[0]  # first coord of the window 
        (r4, c4) = coords[-1] # second coord of the window

        # determine the direction of the window (horizontal/vertical/diagonal) regardless the distance

        # All the windows have 4 consecutive cells: the direction is given by the difference of the first and last one cell.
        # directional vector
        dr = r4 - r1
        dc = c4 - c1

        # horizontal : dr = 0, dc = 3 
        # vertical : dr = 3, dc = 0
        # diagonal \ : dr = 3, dc = 3
        # diagonal / : dr = -3, dc = 3

        # dr == 0 -> sequence on the same row
        # dr > 0 -> sequence pointing upwards
        # dr < 0 -> sequence pointing downwards

        # dc == 0 -> sequence on the same column
        # dc > 0 -> sequence pointing rightward
        # dc < 0 -> sequence pointing leftward

        # extract only the verse regardless of the length
        dr = (dr > 0) - (dr < 0)
        dc = (dc > 0) - (dc < 0)

        open_ends = 0

        # Check from initial point : 1 step backward from the direction of the sequence
        rr = r1 - dr
        cc =  c1 - dc
        # check if it is inside or outside the boarc
        if 0 <= rr < self.rows and 0 <= cc < self.columns:
            if self.board[rr][cc] == " ":
                open_ends += 1

        # Check from last point : 1 step forward from the direction of the sequence
        rr, cc = r4 + dr, c4 + dc
        if 0 <= rr < self.rows and 0 <= cc < self.columns:
            if self.board[rr][cc] == " ":
                open_ends += 1

        return open_ends

    def extendability(self, coords):
        """Count how many additional cells can be inserted in the same direction untill the end of the board."""

        # Normalize the direction  (dr,dc) as in count_open_ends
        (r1, c1) = coords[0]  # first coord of the window 
        (r4, c4) = coords[-1] # second coord of the window

        dr = r4 - r1
        dc = c4 - c1

        dr = (dr > 0) - (dr < 0)
        dc = (dc > 0) - (dc < 0)

        ext = 0

        rr = r4 + dr 
        cc = c4 + dc

        # explore 1 position forward at a time with respect to the direction of the window and count how many empty cells there are
        while 0 <= rr < self.rows and 0 <= cc < self.columns:
            if self.board[rr][cc] != " ":
                break
            ext += 1
            rr += dr
            cc += dc

        return ext
    
    def score_extendability(self, ext): 
        """Score corresponding to the extendability count. Higher extendability -> higher score."""
        if ext == 5: return 40000
        if ext == 4: return 30000
        if ext == 3: return 20000 
        if ext == 2: return 10000 
        return 0 
    