from chess_game import (
    BLACK,
    BISHOP,
    FILES,
    KING,
    KNIGHT,
    PAWN,
    PIECE_VAL,
    QUEEN,
    ROOK,
    WHITE,
    do_move,
    in_check,
    legal_moves,
    update_castling,
)


PIECE_NAMES = {
    PAWN: "pawn",
    KNIGHT: "knight",
    BISHOP: "bishop",
    ROOK: "rook",
    QUEEN: "queen",
    KING: "king",
}

CENTER_SQUARES = {(3, 3), (3, 4), (4, 3), (4, 4)}
NEAR_CENTER_SQUARES = {
    (2, 2), (2, 3), (2, 4), (2, 5),
    (3, 2),                 (3, 5),
    (4, 2),                 (4, 5),
    (5, 2), (5, 3), (5, 4), (5, 5),
}


def square_name(row, col):
    return f"{FILES[col]}{8 - row}"


def _captured_piece(board, move, ep):
    r1, c1, r2, c2 = move
    target = board[r2][c2]
    mover = board[r1][c1]
    if mover is None:
        return None

    color, piece = mover
    if target is not None:
        return target

    if piece == PAWN and ep == (r2, c2):
        return board[r1][c2]

    return None


def _center_bonus(row, col):
    if (row, col) in CENTER_SQUARES:
        return 3
    if (row, col) in NEAR_CENTER_SQUARES:
        return 1
    return 0


def _development_bonus(piece, start_row, end_row, color):
    if piece not in (KNIGHT, BISHOP):
        return 0

    home_row = 7 if color == WHITE else 0
    if start_row == home_row and end_row != home_row:
        return 2
    return 0


def _forward_bonus(piece, start_row, end_row, color):
    if piece != PAWN:
        return 0

    if color == WHITE and end_row < start_row:
        return 1
    if color == BLACK and end_row > start_row:
        return 1
    return 0


def evaluate_move(board, move, turn, ep=None, cas=None):
    """
    Return a simple score and short reason list for one legal move.
    """
    r1, c1, r2, c2 = move
    moving_piece = board[r1][c1]
    if moving_piece is None:
        return -10**9, ["invalid move"]

    color, piece = moving_piece
    next_board, next_ep = do_move(board, move, ep)
    next_cas = update_castling(cas, board, move) if cas is not None else None

    score = 0
    reasons = []

    captured_piece = _captured_piece(board, move, ep)
    if captured_piece is not None:
        captured_value = PIECE_VAL[captured_piece[1]]
        score += captured_value * 10
        reasons.append(f"wins a {PIECE_NAMES[captured_piece[1]]}")

    if piece == PAWN and (r2 == 0 or r2 == 7):
        score += 8
        reasons.append("promotes a pawn")

    if piece == KING and abs(c2 - c1) == 2:
        score += 4
        reasons.append("improves king safety with castling")

    check_bonus = 0
    if in_check(next_board, -turn):
        opponent_moves = legal_moves(next_board, -turn, next_ep, next_cas)
        if not opponent_moves:
            score += 1000
            reasons.append("gives checkmate")
        else:
            check_bonus = 6
            score += check_bonus
            reasons.append("puts the opponent in check")

    center = _center_bonus(r2, c2)
    if center:
        score += center
        reasons.append("improves control of the center")

    develop = _development_bonus(piece, r1, r2, color)
    if develop:
        score += develop
        reasons.append("develops a piece")

    forward = _forward_bonus(piece, r1, r2, color)
    if forward:
        score += forward
        reasons.append("pushes a pawn forward")

    if not reasons:
        reasons.append("keeps the position moving")

    return score, reasons


def describe_move(board, move):
    r1, c1, r2, c2 = move
    cell = board[r1][c1]
    if cell is None:
        return "unknown move"

    _, piece = cell
    piece_name = PIECE_NAMES[piece].capitalize()
    return f"{piece_name} from {square_name(r1, c1)} to {square_name(r2, c2)}"


def suggest_next_move(board, turn, ep=None, cas=None):
    """
    Pick one simple move suggestion for the current side.

    Returns:
        dict with keys:
            move: tuple like (r1, c1, r2, c2)
            score: simple numeric score
            text: readable move text
            reason: short explanation string
            reasons: list of explanation fragments
        or None if there are no legal moves.
    """
    moves = legal_moves(board, turn, ep, cas)
    if not moves:
        return None

    best_move = None
    best_score = -10**9
    best_reasons = []

    for move in moves:
        score, reasons = evaluate_move(board, move, turn, ep, cas)
        if score > best_score:
            best_move = move
            best_score = score
            best_reasons = reasons

    return {
        "move": best_move,
        "score": best_score,
        "text": describe_move(board, best_move),
        "reason": best_reasons[0],
        "reasons": best_reasons,
    }


def get_help_message(board, turn, ep=None, cas=None):
    suggestion = suggest_next_move(board, turn, ep, cas)
    if suggestion is None:
        return "No legal move available."

    return f"Suggested move: {suggestion['text']} because it {suggestion['reason']}."


def suggest_for_game(game):
    """
    Convenience wrapper for the Game object from chess_game.py.
    """
    return suggest_next_move(game.board, game.turn, game.ep, game.cas)
