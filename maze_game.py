import math
import random
from collections import deque

import pygame
from connectivity import GameSession

WALL = "#"
PATH = " "

COLOR_BG = (10, 10, 20)
COLOR_WALL = (30, 40, 60)
COLOR_PATH = (240, 245, 250)
COLOR_PLAYER = (100, 200, 255)
COLOR_GOAL = (50, 255, 100)
COLOR_HINT = (255, 200, 50)
COLOR_BUTTON = (60, 100, 200)
COLOR_BUTTON_HOVER = (100, 150, 255)
COLOR_BUTTON_ACTIVE = (50, 255, 100)
COLOR_TEXT = (240, 245, 250)
COLOR_TEXT_DARK = (50, 50, 80)

DIFFICULTY_SETTINGS = {
    "easy": {"size": 21, "cell": 24},
    "medium": {"size": 31, "cell": 16},
    "hard": {"size": 41, "cell": 12},
}

PANEL_WIDTH = 250
EXTRA_HEIGHT = 150


def make_grid(width, height):
    return [[WALL for _ in range(width)] for _ in range(height)]


def carve_maze(grid, start_r, start_c):
    height = len(grid)
    width = len(grid[0])
    grid[start_r][start_c] = PATH
    directions = [(2, 0), (-2, 0), (0, 2), (0, -2)]
    random.shuffle(directions)

    for dr, dc in directions:
        nr, nc = start_r + dr, start_c + dc
        if 1 <= nr < height - 1 and 1 <= nc < width - 1 and grid[nr][nc] == WALL:
            grid[start_r + dr // 2][start_c + dc // 2] = PATH
            carve_maze(grid, nr, nc)


def solve_bfs(grid, start, goal):
    visited = {start}
    parent = {start: None}
    queue = deque([start])

    while queue:
        r, c = queue.popleft()
        if (r, c) == goal:
            path = []
            node = goal
            while node is not None:
                path.append(node)
                node = parent[node]
            return list(reversed(path))

        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if (
                0 <= nr < len(grid)
                and 0 <= nc < len(grid[0])
                and grid[nr][nc] == PATH
                and (nr, nc) not in visited
            ):
                visited.add((nr, nc))
                parent[(nr, nc)] = (r, c)
                queue.append((nr, nc))

    return []


def solve_dfs(grid, start, goal):
    visited = set()
    path = []

    def dfs(r, c):
        visited.add((r, c))
        path.append((r, c))

        if (r, c) == goal:
            return True

        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if (
                0 <= nr < len(grid)
                and 0 <= nc < len(grid[0])
                and grid[nr][nc] == PATH
                and (nr, nc) not in visited
            ):
                if dfs(nr, nc):
                    return True

        path.pop()
        return False

    dfs(start[0], start[1])
    return path


def solve_path(state):
    if state["algorithm"] == "bfs":
        return solve_bfs(state["grid"], state["player"], state["goal"])
    return solve_dfs(state["grid"], state["player"], state["goal"])


def make_buttons():
    return {
        "easy": {"rect": pygame.Rect(20, 20, 65, 40), "label": "EASY"},
        "medium": {"rect": pygame.Rect(92, 20, 65, 40), "label": "MED"},
        "hard": {"rect": pygame.Rect(164, 20, 65, 40), "label": "HARD"},
        "dfs": {"rect": pygame.Rect(20, 70, 100, 45), "label": "DFS"},
        "hint": {"rect": pygame.Rect(130, 70, 100, 45), "label": "HINT"},
        "reset": {"rect": pygame.Rect(75, 125, 100, 45), "label": "RESET"},
    }


def create_state():
    pygame.init()

    state = {
        "difficulty": "easy",
        "algorithm": "dfs",
        "show_hint": False,
        "hint_path": [],
        "won": False,
        "move_count": 0,
        "size": 0,
        "cell": 0,
        "grid": [],
        "player": (1, 1),
        "goal": (1, 1),
        "width": 0,
        "height": 0,
        "screen": None,
        "clock": pygame.time.Clock(),
        "font_large": pygame.font.Font(None, 36),
        "font": pygame.font.Font(None, 24),
        "font_small": pygame.font.Font(None, 18),
        "buttons": make_buttons(),
        "session": None,
    }

    apply_difficulty(state, state["difficulty"])
    pygame.display.set_caption("Maze Game - DFS Solver")
    return state


def get_button_rect(state, key):
    return state["buttons"][key]["rect"].move(state["size"] * state["cell"], 0)


def reset_game(state):
    if state["session"] is not None:
        state["session"].record_loss(state["move_count"])
    state["grid"] = make_grid(state["size"], state["size"])
    carve_maze(state["grid"], 1, 1)
    state["player"] = (1, 1)
    state["goal"] = (state["size"] - 2, state["size"] - 2)
    state["won"] = False
    state["move_count"] = 0
    state["show_hint"] = False
    state["hint_path"] = []
    state["session"] = GameSession("Maze Game")


def apply_difficulty(state, difficulty):
    settings = DIFFICULTY_SETTINGS[difficulty]
    state["difficulty"] = difficulty
    state["size"] = settings["size"]
    state["cell"] = settings["cell"]
    state["width"] = state["size"] * state["cell"] + PANEL_WIDTH
    state["height"] = state["size"] * state["cell"] + EXTRA_HEIGHT
    state["screen"] = pygame.display.set_mode((state["width"], state["height"]))
    reset_game(state)


def draw_button(state, key, hover):
    button = state["buttons"][key]
    rect = get_button_rect(state, key)

    if key == state["algorithm"] and key == "dfs":
        color = COLOR_BUTTON_ACTIVE
    elif key == state["difficulty"]:
        color = COLOR_BUTTON_ACTIVE
    elif hover:
        color = COLOR_BUTTON_HOVER
    else:
        color = COLOR_BUTTON

    pygame.draw.rect(state["screen"], color, rect, border_radius=8)
    pygame.draw.rect(state["screen"], COLOR_TEXT, rect, 2, border_radius=8)

    text_color = COLOR_TEXT_DARK if color == COLOR_BUTTON_ACTIVE else COLOR_TEXT
    text_surface = state["font"].render(button["label"], True, text_color)
    text_rect = text_surface.get_rect(center=rect.center)
    state["screen"].blit(text_surface, text_rect)


def draw_game(state):
    screen = state["screen"]
    screen.fill(COLOR_BG)

    for r in range(state["size"]):
        for c in range(state["size"]):
            x = c * state["cell"]
            y = r * state["cell"]
            color = COLOR_WALL if state["grid"][r][c] == WALL else COLOR_PATH
            pygame.draw.rect(screen, color, (x, y, state["cell"], state["cell"]))

    if state["show_hint"] and state["hint_path"]:
        for r, c in state["hint_path"]:
            x = c * state["cell"] + state["cell"] // 2
            y = r * state["cell"] + state["cell"] // 2
            pygame.draw.circle(screen, COLOR_HINT, (x, y), 6, 1)
            pygame.draw.circle(screen, COLOR_HINT, (x, y), 3)

    gr, gc = state["goal"]
    pulse = math.sin(pygame.time.get_ticks() / 300) * 2 + 8
    pygame.draw.circle(
        screen,
        COLOR_GOAL,
        (gc * state["cell"] + state["cell"] // 2, gr * state["cell"] + state["cell"] // 2),
        int(pulse),
    )

    pr, pc = state["player"]
    bob_offset = math.sin(pygame.time.get_ticks() / 200) * 2
    pygame.draw.circle(
        screen,
        COLOR_PLAYER,
        (pc * state["cell"] + state["cell"] // 2, pr * state["cell"] + state["cell"] // 2 + bob_offset),
        state["cell"] // 3,
    )

    panel_rect = pygame.Rect(state["size"] * state["cell"], 0, PANEL_WIDTH, state["height"])
    pygame.draw.rect(screen, (20, 25, 40), panel_rect)
    pygame.draw.line(
        screen,
        COLOR_BUTTON,
        (state["size"] * state["cell"], 0),
        (state["size"] * state["cell"], state["height"]),
        2,
    )

    title = state["font_large"].render("MAZE", True, COLOR_BUTTON_ACTIVE)
    screen.blit(title, (state["size"] * state["cell"] + 70, 185))

    mode_text = f"Mode: {state['difficulty'].upper()}"
    mode_surface = state["font"].render(mode_text, True, COLOR_TEXT)
    screen.blit(mode_surface, (state["size"] * state["cell"] + 20, 150))

    algo_text = f"Algorithm: {state['algorithm'].upper()}"
    algo_surface = state["font"].render(algo_text, True, COLOR_BUTTON_ACTIVE)
    screen.blit(algo_surface, (state["size"] * state["cell"] + 20, 230))

    path_text = f"Path: {len(solve_path(state))} steps"
    path_surface = state["font"].render(path_text, True, COLOR_HINT)
    screen.blit(path_surface, (state["size"] * state["cell"] + 20, 270))

    moves_text = f"Moves: {state['move_count']}"
    moves_surface = state["font"].render(moves_text, True, COLOR_TEXT)
    screen.blit(moves_surface, (state["size"] * state["cell"] + 20, 310))

    mouse_pos = pygame.mouse.get_pos()
    for key in state["buttons"]:
        hover = get_button_rect(state, key).collidepoint(mouse_pos)
        draw_button(state, key, hover)

    if state["won"]:
        status = "YOU WON!"
        status_color = COLOR_GOAL
    else:
        status = "Reach the green goal!"
        status_color = COLOR_TEXT

    status_surface = state["font"].render(status, True, status_color)
    screen.blit(status_surface, (20, state["size"] * state["cell"] + 20))

    controls = "Move: Arrows/WASD | Modes: 1/2/3"
    controls_surface = state["font_small"].render(controls, True, (150, 150, 180))
    screen.blit(controls_surface, (20, state["size"] * state["cell"] + 60))

    pygame.display.flip()


def move_player(state, dr, dc):
    if state["won"]:
        return

    nr = state["player"][0] + dr
    nc = state["player"][1] + dc

    if state["grid"][nr][nc] == WALL:
        return

    state["player"] = (nr, nc)
    state["move_count"] += 1
    state["session"].update_moves(state["move_count"])
    state["show_hint"] = False

    if state["player"] == state["goal"]:
        state["won"] = True
        state["session"].record_win(state["move_count"])


def show_hint(state):
    if state["won"]:
        return
    state["hint_path"] = solve_path(state)
    state["show_hint"] = True


def handle_keydown(state, key):
    if key == pygame.K_UP or key == pygame.K_w:
        move_player(state, -1, 0)
    elif key == pygame.K_DOWN or key == pygame.K_s:
        move_player(state, 1, 0)
    elif key == pygame.K_LEFT or key == pygame.K_a:
        move_player(state, 0, -1)
    elif key == pygame.K_RIGHT or key == pygame.K_d:
        move_player(state, 0, 1)
    elif key == pygame.K_r:
        reset_game(state)
    elif key == pygame.K_1:
        apply_difficulty(state, "easy")
    elif key == pygame.K_2:
        apply_difficulty(state, "medium")
    elif key == pygame.K_3:
        apply_difficulty(state, "hard")
    elif key == pygame.K_h:
        show_hint(state)


def handle_mouse_click(state, mouse_pos):
    for key in state["buttons"]:
        if get_button_rect(state, key).collidepoint(mouse_pos):
            if key in DIFFICULTY_SETTINGS:
                apply_difficulty(state, key)
            elif key == "dfs":
                state["algorithm"] = "dfs"
                state["show_hint"] = False
            elif key == "hint":
                show_hint(state)
            elif key == "reset":
                reset_game(state)
            break


def run_game():
    state = create_state()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                handle_keydown(state, event.key)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                handle_mouse_click(state, event.pos)

        draw_game(state)
        state["clock"].tick(60)

    pygame.quit()


if __name__ == "__main__":
    run_game()
