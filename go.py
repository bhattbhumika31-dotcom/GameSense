import pygame
import sys

SIZE = 9
CELL_SIZE = 60
MARGIN = 40
PANEL_WIDTH = 180
BOARD_SIZE = SIZE * CELL_SIZE + 2 * MARGIN
WINDOW_WIDTH = BOARD_SIZE + PANEL_WIDTH
WINDOW_HEIGHT = BOARD_SIZE

WOOD = (222, 184, 135)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
LINE = (0, 0, 0)
TEXT = (40, 20, 0)
PANEL_BG = (240, 220, 180)
BUTTON = (180, 120, 70)
BUTTON_HOVER = (200, 140, 90)

RESET_BUTTON = pygame.Rect(BOARD_SIZE + 30, 250, 120, 45)

pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Go Game - Basic")
font = pygame.font.Font(None, 32)
small_font = pygame.font.Font(None, 26)

board = [['.' for _ in range(SIZE)] for _ in range(SIZE)]
current_player = 'B'
black_moves = 0
white_moves = 0

def reset_game():
    global board, current_player, black_moves, white_moves
    board = [['.' for _ in range(SIZE)] for _ in range(SIZE)]
    current_player = 'B'
    black_moves = 0
    white_moves = 0

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
                         (BOARD_SIZE - MARGIN, MARGIN + i * CELL_SIZE))
        pygame.draw.line(screen, LINE,
                         (MARGIN + i * CELL_SIZE, MARGIN),
                         (MARGIN + i * CELL_SIZE, BOARD_SIZE - MARGIN))

    for r in range(SIZE):
        for c in range(SIZE):
            if board[r][c] != '.':
                color = BLACK if board[r][c] == 'B' else WHITE
                pygame.draw.circle(screen, color,
                                   (MARGIN + c * CELL_SIZE,
                                    MARGIN + r * CELL_SIZE),
                                   CELL_SIZE // 2 - 5)

    panel_rect = pygame.Rect(BOARD_SIZE, 0, PANEL_WIDTH, WINDOW_HEIGHT)
    pygame.draw.rect(screen, PANEL_BG, panel_rect)
    pygame.draw.line(screen, LINE, (BOARD_SIZE, 0), (BOARD_SIZE, WINDOW_HEIGHT), 2)

    title = font.render("Moves", True, TEXT)
    screen.blit(title, (BOARD_SIZE + 35, 40))

    black_text = small_font.render(f"Black: {black_moves}", True, TEXT)
    screen.blit(black_text, (BOARD_SIZE + 20, 100))

    white_text = small_font.render(f"White: {white_moves}", True, TEXT)
    screen.blit(white_text, (BOARD_SIZE + 20, 140))

    turn_label = "Black" if current_player == 'B' else "White"
    turn_text = small_font.render(f"Turn: {turn_label}", True, TEXT)
    screen.blit(turn_text, (BOARD_SIZE + 20, 200))

    mouse_pos = pygame.mouse.get_pos()
    button_color = BUTTON_HOVER if RESET_BUTTON.collidepoint(mouse_pos) else BUTTON
    pygame.draw.rect(screen, button_color, RESET_BUTTON, border_radius=8)
    pygame.draw.rect(screen, LINE, RESET_BUTTON, 2, border_radius=8)

    reset_text = small_font.render("Reset", True, WHITE)
    reset_rect = reset_text.get_rect(center=RESET_BUTTON.center)
    screen.blit(reset_text, reset_rect)

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
            mouse_pos = pygame.mouse.get_pos()
            if RESET_BUTTON.collidepoint(mouse_pos):
                reset_game()
                continue

            pos = get_position(mouse_pos)
            if pos:
                r, c = pos
                if board[r][c] == '.':
                    board[r][c] = current_player
                    opponent = 'W' if current_player == 'B' else 'B'

                    remove_captured(opponent)

                    if count_liberties(r, c) == 0:
                        board[r][c] = '.'
                        continue

                    if current_player == 'B':
                        black_moves += 1
                    else:
                        white_moves += 1

                    current_player = opponent

pygame.quit()
sys.exit()
