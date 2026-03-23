import tkinter as tk


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
        if sr == start_rank and dr == sr + 2 * direction and board[sr + direction][sc] == ".":
            return True

    if abs(dc - sc) == 1 and dr == sr + direction:
        if board[dr][dc] != "." and piece_color(board[dr][dc]) != color:
            return True

    return False


def valid_move(board, src, dst, turn):
    sr, sc = src
    dr, dc = dst

    if src == dst:
        return False, "Source and destination are the same."

    piece = board[sr][sc]

    if piece == ".":
        return False, "No piece at source."

    if piece_color(piece) != turn:
        return False, "That is not your piece."

    if piece_color(board[dr][dc]) == turn:
        return False, "Destination occupied by your piece."

    p = piece.lower()

    if p == "p":
        if valid_pawn(board, src, dst, turn):
            return True, ""
        return False, "Illegal pawn move."

    if p == "n":
        if (abs(dr - sr), abs(dc - sc)) in {(1, 2), (2, 1)}:
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
        if ((dr == sr or dc == sc) or (abs(dr - sr) == abs(dc - sc))) and path_clear(
            board, src, dst
        ):
            return True, ""
        return False, "Illegal queen move."

    if p == "k":
        if max(abs(dr - sr), abs(dc - sc)) == 1:
            return True, ""
        return False, "Illegal king move."

    return False, "Unknown piece."


def apply_move(board, src, dst):
    sr, sc = src
    dr, dc = dst
    piece = board[sr][sc]
    board[sr][sc] = "."
    board[dr][dc] = piece


def maybe_promote(board, dst):
    dr, dc = dst
    piece = board[dr][dc]

    if piece == "P" and dr == 0:
        board[dr][dc] = "Q"
    elif piece == "p" and dr == 7:
        board[dr][dc] = "q"


def king_captured(board):
    flat = "".join("".join(r) for r in board)
    return "K" not in flat or "k" not in flat


def find_valid_moves(board, src, turn):
    moves = []
    for r in range(8):
        for c in range(8):
            ok, _ = valid_move(board, src, (r, c), turn)
            if ok:
                moves.append((r, c))
    return moves


PIECE_MAP = {
    "K": "♔",
    "Q": "♕",
    "R": "♖",
    "B": "♗",
    "N": "♘",
    "P": "♙",
    "k": "♚",
    "q": "♛",
    "r": "♜",
    "b": "♝",
    "n": "♞",
    "p": "♟",
    ".": "",
}


class ChessGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Chess")

        self.board = make_board()
        self.turn = "w"
        self.selected = None
        self.valid_moves = []

        self.info = tk.Label(root, text="White to move", anchor="w")
        self.info.pack(fill="x", padx=8, pady=6)

        self.frame = tk.Frame(root)
        self.frame.pack(padx=8, pady=8)

        self.buttons = []
        for r in range(8):
            row = []
            for c in range(8):
                btn = tk.Button(
                    self.frame,
                    width=4,
                    height=2,
                    command=lambda rr=r, cc=c: self.on_square(rr, cc),
                    font=("Segoe UI Symbol", 18),
                    relief="flat",
                )
                btn.grid(row=r, column=c, sticky="nsew")
                row.append(btn)
            self.buttons.append(row)

        for i in range(8):
            self.frame.grid_rowconfigure(i, weight=1)
            self.frame.grid_columnconfigure(i, weight=1)

        self.status = tk.Label(root, text="Click a piece to move it.", anchor="w")
        self.status.pack(fill="x", padx=8, pady=(0, 8))

        self.render()

    def render(self):
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                text = PIECE_MAP.get(piece, "")

                btn = self.buttons[r][c]

                bg = "#f0d9b5" if (r + c) % 2 == 0 else "#b58863"

                if self.selected == (r, c):
                    bg = "#f7ec77"
                elif (r, c) in self.valid_moves:
                    bg = "#a9dfbf"

                btn.configure(text=text, bg=bg, activebackground=bg)

        self.info.configure(text=f"{'White' if self.turn == 'w' else 'Black'} to move")

    def on_square(self, r, c):
        if self.selected is None:
            piece = self.board[r][c]

            if piece == ".":
                self.status.configure(text="Select a piece.")
                return

            if piece_color(piece) != self.turn:
                self.status.configure(text="That is not your piece.")
                return

            self.selected = (r, c)
            self.valid_moves = find_valid_moves(self.board, (r, c), self.turn)

            self.status.configure(text="Select a destination.")
            self.render()
            return

        src = self.selected
        dst = (r, c)

        ok, reason = valid_move(self.board, src, dst, self.turn)

        if not ok:
            self.status.configure(text=reason)
            self.selected = None
            self.valid_moves = []
            self.render()
            return

        apply_move(self.board, src, dst)
        maybe_promote(self.board, dst)

        self.selected = None
        self.valid_moves = []

        if king_captured(self.board):
            self.render()
            self.status.configure(
                text=f"{'White' if self.turn == 'w' else 'Black'} wins by capture."
            )
            self.disable_board()
            return

        self.turn = "b" if self.turn == "w" else "w"
        self.status.configure(text="Move made.")
        self.render()

    def disable_board(self):
        for r in range(8):
            for c in range(8):
                self.buttons[r][c].configure(state="disabled")


def main():
    root = tk.Tk()
    ChessGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()