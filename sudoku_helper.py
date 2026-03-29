"""
Sudoku Helper Module
Provides functionality to detect wrong moves and find the next correct move.
"""

import copy


def get_subgrid_size(board_size):
    return 3 if board_size == 9 else 2


def find_wrong_cells(start_board, answer_board, player_board, board_size=9):
    wrong_cells = []
    current_board = copy.deepcopy(player_board)

    for row in range(board_size):
        for col in range(board_size):
            if current_board[row][col] != 0:
                if start_board[row][col] == 0:
                    if current_board[row][col] != answer_board[row][col]:
                        wrong_cells.append((row, col))

    return wrong_cells


def is_safe_move(board, row, col, num, board_size=9):
    subgrid_size = get_subgrid_size(board_size)

    for check_col in range(board_size):
        if board[row][check_col] == num:
            return False

    for check_row in range(board_size):
        if board[check_row][col] == num:
            return False

    start_row = (row // subgrid_size) * subgrid_size
    start_col = (col // subgrid_size) * subgrid_size
    for r in range(start_row, start_row + subgrid_size):
        for c in range(start_col, start_col + subgrid_size):
            if board[r][c] == num:
                return False

    return True


def find_next_move(player_board, answer_board, board_size=9):
    current_board = copy.deepcopy(player_board)

    for row in range(board_size):
        for col in range(board_size):
            if current_board[row][col] == 0:
                return (row, col, answer_board[row][col])

    return (None, None, None)


def get_help_message(start_board, answer_board, player_board, board_size=9):
    wrong_cells = find_wrong_cells(start_board, answer_board, player_board, board_size)

    if wrong_cells:
        wrong_positions = ", ".join([f"({r + 1}, {c + 1})" for r, c in wrong_cells])
        return (f"Wrong moves at cells: {wrong_positions}", "wrong")

    row, col, num = find_next_move(player_board, answer_board, board_size)

    if row is None:
        return ("Puzzle is complete!", "complete")

    return (f"Next move: Put {num} at row {row + 1}, col {col + 1}", "next_move")


def get_all_remaining_moves(player_board, answer_board, board_size=9):
    current_board = copy.deepcopy(player_board)
    moves = []

    for row in range(board_size):
        for col in range(board_size):
            if current_board[row][col] == 0:
                moves.append((row, col, answer_board[row][col]))

    return moves
