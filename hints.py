def find_valid_moves(board, src, turn, valid_move):
    moves = []
    for r in range(8):
        for c in range(8):
            ok, _ = valid_move(board, src, (r, c), turn)
            if ok:
                moves.append((r, c))
    return moves


def print_hints(board, src, turn, valid_move):
    moves = find_valid_moves(board, src, turn, valid_move)

    if not moves:
        print("No valid moves.")
        return

    print("Possible moves:")
    for r, c in moves:
        file = chr(ord('a') + c)
        rank = 8 - r
        print(f"{file}{rank}", end=" ")

    print()


def parse_square(s):
    file = ord(s[0]) - ord('a')
    rank = 8 - int(s[1])
    return (rank, file)