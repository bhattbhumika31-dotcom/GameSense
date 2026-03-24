"""
Sudoku Helper Module
Provides functionality to detect wrong moves and find the next correct move.
"""

import copy


class SudokuHelper:
    def __init__(self, start_board, answer_board, player_board, board_size=9):
        """
        Initialize the helper with the game boards.
        
        Args:
            start_board: The initial puzzle board (with fixed cells)
            answer_board: The complete solved board
            player_board: The current player's progress
            board_size: Size of the board (4 or 9)
        """
        self.start_board = start_board
        self.answer_board = answer_board
        self.player_board = copy.deepcopy(player_board)
        self.board_size = board_size
        self.subgrid_size = 3 if board_size == 9 else 2
    
    def find_wrong_cells(self):
        """
        Find all cells where the player has entered wrong numbers.
        
        Returns:
            List of tuples (row, col) containing wrong moves
        """
        wrong_cells = []
        for row in range(self.board_size):
            for col in range(self.board_size):
                # Check if cell was entered by player (not from start board)
                if self.player_board[row][col] != 0:
                    if self.start_board[row][col] == 0:  # Player entered this
                        if self.player_board[row][col] != self.answer_board[row][col]:
                            wrong_cells.append((row, col))
        return wrong_cells
    
    def is_safe_move(self, board, row, col, num):
        """
        Check if placing a number is valid according to Sudoku rules.
        
        Args:
            board: The board to check
            row: Row index
            col: Column index
            num: Number to place
            
        Returns:
            True if the move is safe, False otherwise
        """
        # Check row
        for check_col in range(self.board_size):
            if board[row][check_col] == num:
                return False
        
        # Check column
        for check_row in range(self.board_size):
            if board[check_row][col] == num:
                return False
        
        # Check subgrid
        start_row = (row // self.subgrid_size) * self.subgrid_size
        start_col = (col // self.subgrid_size) * self.subgrid_size
        for r in range(start_row, start_row + self.subgrid_size):
            for c in range(start_col, start_col + self.subgrid_size):
                if board[r][c] == num:
                    return False
        
        return True
    
    def find_next_move(self):
        """
        Find the next empty cell and the correct number to place there.
        
        Returns:
            Tuple (row, col, correct_number) or (None, None, None) if board is complete
        """
        # Find first empty cell in player's current board
        for row in range(self.board_size):
            for col in range(self.board_size):
                if self.player_board[row][col] == 0:
                    # This cell is empty, return the correct number
                    correct_num = self.answer_board[row][col]
                    return (row, col, correct_num)
        
        # No empty cells found
        return (None, None, None)
    
    def get_help_message(self):
        """
        Generate a comprehensive help message about the current game state.
        
        Returns:
            Tuple (message_text, message_type)
            message_type: 'wrong', 'correct', 'next_move', 'complete'
        """
        # Check for wrong moves first
        wrong_cells = self.find_wrong_cells()
        
        if wrong_cells:
            wrong_positions = ", ".join([f"({r+1}, {c+1})" for r, c in wrong_cells])
            message = f"Wrong moves at cells: {wrong_positions}"
            return (message, 'wrong')
        
        # Find the next correct move
        row, col, num = self.find_next_move()
        
        if row is None:
            # All cells filled
            return ("Puzzle is complete!", 'complete')
        else:
            message = f"Next move: Put {num} at row {row+1}, col {col+1}"
            return (message, 'next_move')
    
    def get_all_remaining_moves(self):
        """
        Get all remaining empty cells with their correct numbers.
        
        Returns:
            List of tuples (row, col, correct_number) for all empty cells
        """
        moves = []
        for row in range(self.board_size):
            for col in range(self.board_size):
                if self.player_board[row][col] == 0:
                    moves.append((row, col, self.answer_board[row][col]))
        return moves
