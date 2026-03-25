import pygame
import sys
import copy

SIZE = 9
CELL_SIZE = 60
MARGIN = 40
WINDOW_SIZE = SIZE * CELL_SIZE + 2 * MARGIN

WOOD = (222, 184, 135)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
LINE = (0, 0, 0)
GREEN = (0, 255, 0)

pygame.init()
screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
pygame.display.set_caption("Go Game - 9x9")

font = pygame.font.SysFont(None, 28)

board = [['.' for _ in range(SIZE)] for _ in range(SIZE)]
current_player = 'B'
show_best_move = False

black_stones = 100
white_stones = 100


def neighbors(r, c):
    dirs = [(1,0), (-1,0), (0,1), (0,-1)]
    return [(r+dr, c+dc) for dr, dc in dirs if 0 <= r+dr < SIZE and 0 <= c+dc < SIZE]

def dfs(r, c, visited, board_ref):
    stack = [(r, c)]
    color = board_ref[r][c]
    group = []
    has_liberty = False

    while stack:
        sr, sc = stack.pop()
        if (sr, sc) in visited:
            continue
        visited.add((sr, sc))
        group.append((sr, sc))

        for nr, nc in neighbors(sr, sc):
            if board_ref[nr][nc] == '.':
                has_liberty = True
            elif board_ref[nr][nc] == color:
                stack.append((nr, nc))

    return group, has_liberty

def remove_captured(board_ref, opponent):
    visited = set()
    for r in range(SIZE):
        for c in range(SIZE):
            if board_ref[r][c] == opponent and (r, c) not in visited:
                group, liberty = dfs(r, c, visited, board_ref)
                if not liberty:
                    for gr, gc in group:
                        board_ref[gr][gc] = '.'

def count_liberties(r, c, board_ref):
    visited = set()
    group, _ = dfs(r, c, visited, board_ref)

    liberties = set()
    for gr, gc in group:
        for nr, nc in neighbors(gr, gc):
            if board_ref[nr][nc] == '.':
                liberties.add((nr, nc))

    return len(liberties)

def evaluate_move(r, c, player):
    opponent = 'W' if player == 'B' else 'B'
    temp_board = copy.deepcopy(board)

    temp_board[r][c] = player

    before = sum(row.count(opponent) for row in temp_board)
    remove_captured(temp_board, opponent)
    after = sum(row.count(opponent) for row in temp_board)

    captured = before - after

    if count_liberties(r, c, temp_board) == 0 and captured == 0:
        return -999

    libs = count_liberties(r, c, temp_board)

    return captured * 10 + libs

def find_best_move(player):
    best_score = -999
    best_move = None

    for r in range(SIZE):
        for c in range(SIZE):
            if board[r][c] == '.':
                score = evaluate_move(r, c, player)
                if score > best_score:
                    best_score = score
                    best_move = (r, c)

    return best_move

def draw_board():
    screen.fill(WOOD)

    for i in range(SIZE):
        pygame.draw.line(screen, LINE,
                         (MARGIN, MARGIN + i * CELL_SIZE),
                         (WINDOW_SIZE - MARGIN, MARGIN + i * CELL_SIZE))
        pygame.draw.line(screen, LINE,
                         (MARGIN + i * CELL_SIZE, MARGIN),
                         (MARGIN + i * CELL_SIZE, WINDOW_SIZE - MARGIN))

    for r in range(SIZE):
        for c in range(SIZE):
            if board[r][c] != '.':
                color = BLACK if board[r][c] == 'B' else WHITE
                pygame.draw.circle(screen, color,
                                   (MARGIN + c * CELL_SIZE,
                                    MARGIN + r * CELL_SIZE),
                                   CELL_SIZE // 2 - 5)

    if show_best_move:
        best = find_best_move(current_player)
        if best:
            r, c = best
            pygame.draw.circle(screen, GREEN,
                               (MARGIN + c * CELL_SIZE,
                                MARGIN + r * CELL_SIZE),
                               8)

    status = "Best Move: ON (B)" if show_best_move else "Best Move: OFF (B)"
    text = font.render(status, True, (0, 0, 0))
    screen.blit(text, (10, 10))

    stones_text = f"Black: {black_stones}   White: {white_stones}"
    text2 = font.render(stones_text, True, (0, 0, 0))
    screen.blit(text2, (10, 35))

def get_position(pos):
    x, y = pos
    col = int((x - MARGIN + CELL_SIZE // 2) // CELL_SIZE)
    row = int((y - MARGIN + CELL_SIZE // 2) // CELL_SIZE)
    if 0 <= row < SIZE and 0 <= col < SIZE:
        return row, col
    return None

running = True
while running:
    draw_board()
    pygame.display.flip()

    if black_stones == 0 and white_stones == 0:
        print("Game Over!")
        running = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_b:
                show_best_move = not show_best_move

        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = get_position(pygame.mouse.get_pos())
            if pos:
                r, c = pos

                if board[r][c] == '.':

                    if current_player == 'B' and black_stones == 0:
                        continue
                    if current_player == 'W' and white_stones == 0:
                        continue

                    board[r][c] = current_player
                    opponent = 'W' if current_player == 'B' else 'B'

                    remove_captured(board, opponent)

                    if count_liberties(r, c, board) == 0:
                        board[r][c] = '.'
                        continue

                    if current_player == 'B':
                        black_stones -= 1
                    else:
                        white_stones -= 1

                    current_player = opponent

pygame.quit()
sys.exit()