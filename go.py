import pygame
import sys

SIZE = 9
CELL_SIZE = 60
MARGIN = 40
WINDOW_SIZE = SIZE * CELL_SIZE + 2 * MARGIN

WOOD = (222, 184, 135)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
LINE = (0, 0, 0)

pygame.init()
screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
pygame.display.set_caption("Go Game - Basic")

board = [['.' for _ in range(SIZE)] for _ in range(SIZE)]
current_player = 'B'

def neighbors(r, c):
    dirs = [(1,0), (-1,0), (0,1), (0,-1)]
    return [(r+dr, c+dc) for dr, dc in dirs if 0 <= r+dr < SIZE and 0 <= c+dc < SIZE]

def dfs(r, c, visited):
    stack = [(r, c)]
    color = board[r][c]
    group = []
    has_liberty = False

    while stack:
        sr, sc = stack.pop()
        if (sr, sc) in visited:
            continue
        visited.add((sr, sc))
        group.append((sr, sc))

        for nr, nc in neighbors(sr, sc):
            if board[nr][nc] == '.':
                has_liberty = True
            elif board[nr][nc] == color:
                stack.append((nr, nc))

    return group, has_liberty

def remove_captured(opponent):
    visited = set()
    for r in range(SIZE):
        for c in range(SIZE):
            if board[r][c] == opponent and (r, c) not in visited:
                group, liberty = dfs(r, c, visited)
                if not liberty:
                    for gr, gc in group:
                        board[gr][gc] = '.'

def count_liberties(r, c):
    visited = set()
    group, _ = dfs(r, c, visited)

    liberties = set()
    for gr, gc in group:
        for nr, nc in neighbors(gr, gc):
            if board[nr][nc] == '.':
                liberties.add((nr, nc))

    return len(liberties)

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

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = get_position(pygame.mouse.get_pos())
            if pos:
                r, c = pos
                if board[r][c] == '.':
                    board[r][c] = current_player
                    opponent = 'W' if current_player == 'B' else 'B'

                    remove_captured(opponent)

                    if count_liberties(r, c) == 0:
                        board[r][c] = '.'
                        continue

                    current_player = opponent

pygame.quit()
sys.exit()