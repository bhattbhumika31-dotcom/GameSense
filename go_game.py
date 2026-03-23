import pygame
import sys

# Board settings
SIZE = 9
CELL_SIZE = 60
MARGIN = 40
WINDOW_SIZE = SIZE * CELL_SIZE + 2 * MARGIN

# Colors
WOOD = (222, 184, 135)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
LINE = (0, 0, 0)

pygame.init()
screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
pygame.display.set_caption("Go Game - 9x9")

board = [['.' for _ in range(SIZE)] for _ in range(SIZE)]
current_player = 'B'

# Draw board
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

# Get board position from mouse
def get_position(pos):
    x, y = pos
    col = round((x - MARGIN) / CELL_SIZE)
    row = round((y - MARGIN) / CELL_SIZE)
    if 0 <= row < SIZE and 0 <= col < SIZE:
        return row, col
    return None

# Get neighbors
def neighbors(r, c):
    dirs = [(1,0), (-1,0), (0,1), (0,-1)]
    result = []
    for dr, dc in dirs:
        nr, nc = r + dr, c + dc
        if 0 <= nr < SIZE and 0 <= nc < SIZE:
            result.append((nr, nc))
    return result

# DFS to find group + liberties
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

# Remove captured stones
def remove_captured(opponent):
    visited = set()
    for r in range(SIZE):
        for c in range(SIZE):
            if board[r][c] == opponent and (r, c) not in visited:
                group, liberty = dfs(r, c, visited)
                if not liberty:
                    for gr, gc in group:
                        board[gr][gc] = '.'

# Main loop
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
                    current_player = opponent

pygame.quit()
sys.exit()
