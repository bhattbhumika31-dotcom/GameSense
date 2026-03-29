import random
import pygame
import ctypes
import os
import sys
import math

WALL = "#"
PATH = " "

# Colors
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

def make_grid(width, height):
    return [[WALL for _ in range(width)] for _ in range(height)]

def carve_maze(grid, start_r, start_c):
    h = len(grid)
    w = len(grid[0])
    grid[start_r][start_c] = PATH
    dirs = [(2, 0), (-2, 0), (0, 2), (0, -2)]
    random.shuffle(dirs)
    for dr, dc in dirs:
        nr, nc = start_r + dr, start_c + dc
        if 1 <= nr < h - 1 and 1 <= nc < w - 1 and grid[nr][nc] == WALL:
            grid[start_r + dr // 2][start_c + dc // 2] = PATH
            carve_maze(grid, nr, nc)

class MazeSolverWrapper:
    def __init__(self):
        self.grid = None
        self.start = None
        self.goal = None
    
    def init(self, h, w):
        pass
    
    def set_grid(self, grid):
        self.grid = grid
    
    def set_positions(self, sr, sc, gr, gc):
        self.start = (sr, sc)
        self.goal = (gr, gc)
    
    def solve(self, algo):
        if algo == "bfs":
            return self._solve_bfs()
        else:
            return self._solve_dfs()
    
    def _solve_bfs(self):
        from collections import deque
        
        visited = set()
        parent = {}
        queue = deque([self.start])
        visited.add(self.start)
        parent[self.start] = None
        
        while queue:
            r, c = queue.popleft()
            
            if (r, c) == self.goal:
                path = []
                node = self.goal
                while node:
                    path.append(node)
                    node = parent[node]
                return list(reversed(path))
            
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = r + dr, c + dc
                if (0 <= nr < len(self.grid) and 0 <= nc < len(self.grid[0]) and
                    self.grid[nr][nc] == ' ' and (nr, nc) not in visited):
                    visited.add((nr, nc))
                    parent[(nr, nc)] = (r, c)
                    queue.append((nr, nc))
        
        return []
    
    def _solve_dfs(self):
        visited = set()
        path = []
        
        def dfs(r, c):
            visited.add((r, c))
            path.append((r, c))
            
            if (r, c) == self.goal:
                return True
            
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = r + dr, c + dc
                if (0 <= nr < len(self.grid) and 0 <= nc < len(self.grid[0]) and
                    self.grid[nr][nc] == ' ' and (nr, nc) not in visited):
                    if dfs(nr, nc):
                        return True
            
            path.pop()
            return False
        
        dfs(self.start[0], self.start[1])
        return path
    
    def cleanup(self):
        pass

class MazeGUI:
    def __init__(self):
        pygame.init()
        
        self.size = 21
        self.cell = 24
        self.grid = make_grid(self.size, self.size)
        carve_maze(self.grid, 1, 1)
        
        self.player = (1, 1)
        self.goal = (self.size - 2, self.size - 2)
        
        self.solver = MazeSolverWrapper()
        self.solver.init(self.size, self.size)
        self.solver.set_grid(self.grid)
        self.solver.set_positions(self.player[0], self.player[1], 
                                 self.goal[0], self.goal[1])
        
        self.algorithm = "bfs"
        self.show_hint = False
        self.hint_path = []
        self.won = False
        
        self.width = self.size * self.cell + 250
        self.height = self.size * self.cell + 150
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("🎮 Maze Game - BFS/DFS Solver")
        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.Font(None, 36)
        self.font = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 18)
        
        # Animation
        self.player_bob = 0
        self.hint_alpha = 0
        
        # Buttons
        self.buttons = {
            'bfs': {'rect': pygame.Rect(self.size * self.cell + 20, 20, 100, 50), 'label': 'BFS', 'key': 'b'},
            'dfs': {'rect': pygame.Rect(self.size * self.cell + 130, 20, 100, 50), 'label': 'DFS', 'key': 'd'},
            'hint': {'rect': pygame.Rect(self.size * self.cell + 20, 80, 100, 50), 'label': 'HINT', 'key': 'h'},
            'reset': {'rect': pygame.Rect(self.size * self.cell + 130, 80, 100, 50), 'label': 'RESET', 'key': 'r'},
        }
        
        self.draw()
    
    def reset(self):
        self.grid = make_grid(self.size, self.size)
        carve_maze(self.grid, 1, 1)
        self.player = (1, 1)
        self.goal = (self.size - 2, self.size - 2)
        self.won = False
        self.show_hint = False
        self.hint_path = []
        
        self.solver.set_grid(self.grid)
        self.solver.set_positions(self.player[0], self.player[1], 
                                 self.goal[0], self.goal[1])
        self.draw()
    
    def draw_button(self, key, hover):
        btn = self.buttons[key]
        rect = btn['rect']
        
        # Determine color
        if key == self.algorithm and key in ['bfs', 'dfs']:
            color = COLOR_BUTTON_ACTIVE
        elif hover:
            color = COLOR_BUTTON_HOVER
        else:
            color = COLOR_BUTTON
        
        # Draw button with rounded corners effect
        pygame.draw.rect(self.screen, color, rect, border_radius=8)
        pygame.draw.rect(self.screen, COLOR_TEXT, rect, 2, border_radius=8)
        
        # Draw text
        text_surf = self.font.render(btn['label'], True, COLOR_TEXT_DARK if color == COLOR_BUTTON_ACTIVE else COLOR_TEXT)
        text_rect = text_surf.get_rect(center=rect.center)
        self.screen.blit(text_surf, text_rect)
    
    def draw(self):
        self.screen.fill(COLOR_BG)
        
        # Draw maze
        for r in range(self.size):
            for c in range(self.size):
                x1 = c * self.cell
                y1 = r * self.cell
                x2 = x1 + self.cell
                y2 = y1 + self.cell
                color = COLOR_WALL if self.grid[r][c] == WALL else COLOR_PATH
                pygame.draw.rect(self.screen, color, (x1, y1, self.cell, self.cell))
        
        # Draw hint path with glow
        if self.show_hint and self.hint_path:
            for i, (r, c) in enumerate(self.hint_path):
                x = c * self.cell + self.cell // 2
                y = r * self.cell + self.cell // 2
                # Glow effect
                pygame.draw.circle(self.screen, COLOR_HINT, (x, y), 6, 1)
                pygame.draw.circle(self.screen, COLOR_HINT, (x, y), 3)
        
        # Draw goal with pulsing effect
        gr, gc = self.goal
        pulse = math.sin(pygame.time.get_ticks() / 300) * 2 + 8
        pygame.draw.circle(self.screen, COLOR_GOAL, 
                          (gc * self.cell + self.cell // 2, 
                           gr * self.cell + self.cell // 2), int(pulse))
        
        # Draw player with bobbing animation
        pr, pc = self.player
        bob_offset = math.sin(pygame.time.get_ticks() / 200) * 2
        pygame.draw.circle(self.screen, COLOR_PLAYER,
                          (pc * self.cell + self.cell // 2, 
                           pr * self.cell + self.cell // 2 + bob_offset), self.cell // 3)
        
        # Draw UI panel
        panel_rect = pygame.Rect(self.size * self.cell, 0, 250, self.height)
        pygame.draw.rect(self.screen, (20, 25, 40), panel_rect)
        pygame.draw.line(self.screen, COLOR_BUTTON, (self.size * self.cell, 0), 
                        (self.size * self.cell, self.height), 2)
        
        # Draw title
        title = self.font_large.render("🎮 MAZE", True, COLOR_BUTTON_ACTIVE)
        self.screen.blit(title, (self.size * self.cell + 30, 150))
        
        # Draw algorithm info
        algo_text = f"Algorithm: {self.algorithm.upper()}"
        algo_surf = self.font.render(algo_text, True, COLOR_BUTTON_ACTIVE)
        self.screen.blit(algo_surf, (self.size * self.cell + 20, 200))
        
        # Draw path length
        path_len = len(self.solver.solve(self.algorithm))
        path_text = f"Path: {path_len} steps"
        path_surf = self.font.render(path_text, True, COLOR_HINT)
        self.screen.blit(path_surf, (self.size * self.cell + 20, 240))
        
        # Draw buttons
        mouse_pos = pygame.mouse.get_pos()
        for key in self.buttons:
            hover = self.buttons[key]['rect'].collidepoint(mouse_pos)
            self.draw_button(key, hover)
        
        # Draw status
        if self.won:
            status = "YOU WON!"
            status_color = COLOR_GOAL
        else:
            status = "Reach the green goal!"
            status_color = COLOR_TEXT
        
        status_surf = self.font.render(status, True, status_color)
        self.screen.blit(status_surf, (20, self.size * self.cell + 20))
        
        # Draw controls hint
        controls = "Arrow Keys/WASD to move"
        controls_surf = self.font_small.render(controls, True, (150, 150, 180))
        self.screen.blit(controls_surf, (20, self.size * self.cell + 60))
        
        pygame.display.flip()
    
    def move(self, dr, dc):
        if self.won:
            return
        
        nr = self.player[0] + dr
        nc = self.player[1] + dc
        
        if self.grid[nr][nc] == WALL:
            return
        
        self.player = (nr, nc)
        self.show_hint = False
        
        if self.player == self.goal:
            self.won = True
        
        self.draw()
    
    def get_hint(self):
        if not self.won:
            self.hint_path = self.solver.solve(self.algorithm)
            self.show_hint = True
            self.draw()
    
    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        self.move(-1, 0)
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        self.move(1, 0)
                    elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        self.move(0, -1)
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        self.move(0, 1)
                    elif event.key == pygame.K_r:
                        self.reset()
                    elif event.key == pygame.K_b:
                        self.algorithm = "bfs"
                        self.show_hint = False
                        self.draw()
                    elif event.key == pygame.K_d:
                        self.algorithm = "dfs"
                        self.show_hint = False
                        self.draw()
                    elif event.key == pygame.K_h:
                        self.get_hint()
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = event.pos
                    for key, btn in self.buttons.items():
                        if btn['rect'].collidepoint(mouse_pos):
                            if key == 'bfs':
                                self.algorithm = "bfs"
                                self.show_hint = False
                            elif key == 'dfs':
                                self.algorithm = "dfs"
                                self.show_hint = False
                            elif key == 'hint':
                                self.get_hint()
                            elif key == 'reset':
                                self.reset()
                            self.draw()
            
            self.clock.tick(60)
        
        self.solver.cleanup()
        pygame.quit()

if __name__ == "__main__":
    game = MazeGUI()
    game.run()
