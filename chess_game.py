from hints import print_hints, parse_square

FILES = "abcdefgh"
RANKS = "12345678"


def make_board():
    return [
        list("rnbqkbnr"),
        list("pppppppp"),
        list("........"),
        list("........"),
        list("........"),
        list("........"),
        list("PPPPPPPP"),
        list("RNBQKBNR"),
    ]


def piece_color(p):
    if p == ".":
        return None
    return "w" if p.isupper() else "b"


def print_board(board):
    print()
    for i, row in enumerate(board):
        print(8 - i, " ".join(row))
    print("  a b c d e f g h")
    print()


def path_clear(board, src, dst):
    sr, sc = src
    dr, dc = dst
    r_step = 0 if dr == sr else (1 if dr > sr else -1)
    c_step = 0 if dc == sc else (1 if dc > sc else -1)

    r, c = sr + r_step, sc + c_step

    while (r, c) != (dr, dc):
        if board[r][c] != ".":
            return False
        r += r_step
        c += c_step

    return True


def valid_pawn(board, src, dst, color):
    sr, sc = src
    dr, dc = dst

    direction = -1 if color == "w" else 1
    start_rank = 6 if color == "w" else 1

    if sc == dc and board[dr][dc] == ".":
        if dr == sr + direction:
            return True

        if sr == start_rank and dr == sr + 2 * direction:
            if board[sr + direction][sc] == ".":
                return True

    if abs(dc - sc) == 1 and dr == sr + direction:
        if board[dr][dc] != "." and piece_color(board[dr][dc]) != color:
            return True

    return False


def valid_move(board, src, dst, turn):
    sr, sc = src
    dr, dc = dst

    piece = board[sr][sc]

    if piece == ".":
        return False, "No piece at source."

    if piece_color(piece) != turn:
        return False, "Not your piece."

    if piece_color(board[dr][dc]) == turn:
        return False, "Destination occupied."

    p = piece.lower()

    if p == "p":
        if valid_pawn(board, src, dst, turn):
            return True, ""
        return False, "Illegal pawn move."

    if p == "n":
        if (abs(dr - sr), abs(dc - sc)) in [(1, 2), (2, 1)]:
            return True, ""
        return False, "Illegal knight move."

    if p == "b":
        if abs(dr - sr) == abs(dc - sc) and path_clear(board, src, dst):
            return True, ""
        return False, "Illegal bishop move."

    if p == "r":
        if (dr == sr or dc == sc) and path_clear(board, src, dst):
            return True, ""
        return False, "Illegal rook move."

    if p == "q":
        if ((dr == sr or dc == sc) or abs(dr - sr) == abs(dc - sc)) and path_clear(board, src, dst):
            return True, ""
        return False, "Illegal queen move."

    if p == "k":
        if max(abs(dr - sr), abs(dc - sc)) == 1:
            return True, ""
        return False, "Illegal king move."

    return False, "Unknown piece"


def apply_move(board, src, dst):
    sr, sc = src
    dr, dc = dst

    board[dr][dc] = board[sr][sc]
    board[sr][sc] = "."


def king_captured(board):
    flat = "".join("".join(r) for r in board)
    return "K" not in flat or "k" not in flat


def main():
    board = make_board()
    turn = "w"

    while True:
        print_board(board)

        print("White to move" if turn == "w" else "Black to move")
        move = input("Enter move (e2 e4) or 'hint e2': ")

        # HINT COMMAND
        if move.startswith("hint"):
            try:
                _, sq = move.split()
                src = parse_square(sq)
                print_hints(board, src, turn, valid_move)
            except:
                print("Use: hint e2")
            continue

        # NORMAL MOVE
        try:
            s, d = move.split()
            src = parse_square(s)
            dst = parse_square(d)
        except:
            print("Invalid input. Use: e2 e4")
            continue

        ok, msg = valid_move(board, src, dst, turn)

        if not ok:
            print(msg)
            continue

        apply_move(board, src, dst)

        if king_captured(board):
            print_board(board)
            print("White wins!" if turn == "w" else "Black wins!")
            break

        turn = "b" if turn == "w" else "w"


if __name__ == "__main__":
    main()