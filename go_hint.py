import copy

def find_hints(player):
    hint_moves = []
    opponent = 'W' if player == 'B' else 'B'

    for r in range(SIZE):
        for c in range(SIZE):
            if board[r][c] == '.':
                temp_board = copy.deepcopy(board)
                temp_board[r][c] = player

                # count opponent stones before
                before = sum(row.count(opponent) for row in temp_board)

                # simulate capture
                remove_captured(temp_board, opponent)

                # count after
                after = sum(row.count(opponent) for row in temp_board)

                # if stones reduced → good move
                if after < before:
                    hint_moves.append((r, c))

    return hint_moves