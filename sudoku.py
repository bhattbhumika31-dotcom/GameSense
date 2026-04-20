import copy, random, sys, pygame
import sudoku_helper
from connectivity import GameSession

# Constants
WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
BOARD_SIZE = 9
SUBGRID_SIZE = 3 if BOARD_SIZE == 9 else 2

# Colors
BG_COLOR = (245, 239, 228)
GRID_COLOR, THICK_GRID_COLOR = (70, 70, 70), (25, 25, 25)
FIXED_TEXT_COLOR, USER_TEXT_COLOR = (30, 30, 30), (30, 86, 160)
SELECT_COLOR, WRONG_COLOR, SUCCESS_COLOR = (255, 220, 120), (205, 70, 70), (40, 140, 80)
BUTTON_COLOR, BUTTON_TEXT_COLOR = (55, 120, 190), (255, 255, 255)
RED_BG, GREEN_BG = (255, 200, 200), (200, 255, 200)

def set_board_size(size):
    global BOARD_SIZE, SUBGRID_SIZE
    BOARD_SIZE = size
    SUBGRID_SIZE = 3 if BOARD_SIZE == 9 else 2

def make_empty_board():
    return [[0] * BOARD_SIZE for _ in range(BOARD_SIZE)]

def find_empty(board):
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            if board[r][c] == 0:
                return r, c
    return None

def is_valid(board, r, c, num):
    if num in board[r] or any(board[i][c] == num for i in range(BOARD_SIZE)):
        return False
    sr, sc = (r // SUBGRID_SIZE) * SUBGRID_SIZE, (c // SUBGRID_SIZE) * SUBGRID_SIZE
    return not any(board[sr+i][sc+j] == num for i in range(SUBGRID_SIZE) for j in range(SUBGRID_SIZE))

def fill_board(board):
    cell = find_empty(board)
    if not cell:
        return True
    r, c = cell
    nums = list(range(1, BOARD_SIZE + 1))
    random.shuffle(nums)
    for num in nums:
        if is_valid(board, r, c, num):
            board[r][c] = num
            if fill_board(board):
                return True
            board[r][c] = 0
    return False

def count_solutions(board):
    cell = find_empty(board)
    if not cell:
        return 1
    r, c = cell
    count = 0
    for num in range(1, BOARD_SIZE + 1):
        if is_valid(board, r, c, num):
            board[r][c] = num
            count += count_solutions(board)
            board[r][c] = 0
            if count > 1:
                return count
    return count

def make_puzzle():
    solved = make_empty_board()
    fill_board(solved)
    puzzle = copy.deepcopy(solved)
    cells = [(r, c) for r in range(BOARD_SIZE) for c in range(BOARD_SIZE)]
    random.shuffle(cells)
    remove_target = 6 if BOARD_SIZE == 4 else 42
    removed = 0
    for r, c in cells:
        val = puzzle[r][c]
        puzzle[r][c] = 0
        test = copy.deepcopy(puzzle)
        if count_solutions(test) == 1:
            removed += 1
            if removed >= remove_target:
                break
        else:
            puzzle[r][c] = val
    return puzzle, solved


class SudokuGame:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Sudoku")
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        self.fonts = {
            'title': pygame.font.SysFont("arial", 34, bold=True),
            'number': pygame.font.SysFont("arial", 32, bold=True),
            'small': pygame.font.SysFont("arial", 22)
        }
        self.is_fullscreen = False
        self.layout = {}
        self.selected = None
        self.helper_cell = None
        self.wrong_cells = []
        self.move_count = 0
        self.auto_fill_moves = []
        self.auto_fill_index = 0
        self.last_fill_time = 0
        self.board_mode = 9
        self.game_won = False
        self.session = None
        self.new_game()

    def new_game(self):
        if self.session is not None:
            self.session.record_loss(self.move_count)
        self.puzzle, self.solution = make_puzzle()
        self.board = copy.deepcopy(self.puzzle)
        self.selected = None
        self.helper_cell = None
        self.wrong_cells = []
        self.move_count = 0
        self.auto_fill_moves = []
        self.auto_fill_index = 0
        self.last_fill_time = 0
        self.game_won = False
        self.session = GameSession("Sudoku")

    def is_fixed(self, r, c):
        return self.puzzle[r][c] != 0

    def start_auto_fill(self):
        self.wrong_cells = sudoku_helper.find_wrong_cells(self.puzzle, self.solution, self.board, BOARD_SIZE)
        if self.wrong_cells:
            return
        row, col, num = sudoku_helper.find_next_move(self.board, self.solution, BOARD_SIZE)
        self.helper_cell = (row, col, num) if row is not None else None

    def solve_board(self):
        self.wrong_cells = sudoku_helper.find_wrong_cells(self.puzzle, self.solution, self.board, BOARD_SIZE)
        if self.wrong_cells:
            return
        self.helper_cell = None
        self.auto_fill_moves = sudoku_helper.get_all_remaining_moves(self.board, self.solution, BOARD_SIZE)
        self.auto_fill_index = 0
        self.last_fill_time = pygame.time.get_ticks()
        # Fill first move immediately for instant feedback.
        if self.auto_fill_moves:
            r, c, num = self.auto_fill_moves[self.auto_fill_index]
            self.board[r][c] = num
            self.move_count += 1
            self.auto_fill_index += 1
            self.last_fill_time = pygame.time.get_ticks()

    def update_auto_fill(self):
        if self.auto_fill_moves and self.auto_fill_index < len(self.auto_fill_moves):
            current_time = pygame.time.get_ticks()
            if current_time - self.last_fill_time >= 500:  # 0.5 seconds
                r, c, num = self.auto_fill_moves[self.auto_fill_index]
                self.board[r][c] = num
                self.move_count += 1
                self.session.update_moves(self.move_count)
                self.auto_fill_index += 1
                self.last_fill_time = current_time
                self.check_win()

    def check_win(self):
        if not self.game_won and self.board == self.solution:
            self.game_won = True
            self.session.record_win(self.move_count)

    def update_layout(self):
        w, h = self.screen.get_size()
        btn_w = min(170, max(120, w // 4))
        btn_h = 42
        m = max(18, w // 36)
        board_px = min(w - 2*m, h - 150)
        cell_sz = board_px // BOARD_SIZE
        board_px = cell_sz * BOARD_SIZE
        board_l = (w - board_px) // 2
        board_t = 80 + (h - 150 - board_px) // 2
        btn_x = w - m - btn_w
        btn_y_start = 18
        v_gap = btn_h + m
        self.layout = {
            "w": w, "h": h, "left": board_l, "top": board_t, "sz": cell_sz, "px": board_px,
            "btn_new": pygame.Rect(btn_x, btn_y_start, btn_w, btn_h),
            "btn_help": pygame.Rect(btn_x, btn_y_start + v_gap, btn_w, btn_h),
            "btn_solve": pygame.Rect(btn_x, btn_y_start + 2*v_gap, btn_w, btn_h),
            "btn_fs": pygame.Rect(btn_x, btn_y_start + 3*v_gap, btn_w, btn_h),
            "btn_4x4": pygame.Rect(btn_x, btn_y_start + 4*v_gap, btn_w, btn_h),
            "btn_9x9": pygame.Rect(btn_x, btn_y_start + 5*v_gap, btn_w, btn_h),
            "msg_y": min(h - 40, board_t + board_px + 20),
        }

    def draw_button(self, rect, text):
        pygame.draw.rect(self.screen, BUTTON_COLOR, rect, border_radius=8)
        surf = self.fonts['small'].render(text, True, BUTTON_TEXT_COLOR)
        self.screen.blit(surf, surf.get_rect(center=rect.center))

    def solve_board(self):
        self.wrong_cells = sudoku_helper.find_wrong_cells(self.puzzle, self.solution, self.board, BOARD_SIZE)
        if self.wrong_cells:
            return
        self.auto_fill_moves = sudoku_helper.get_all_remaining_moves(self.board, self.solution, BOARD_SIZE)
        self.auto_fill_index = 0
        self.last_fill_time = pygame.time.get_ticks()

    def handle_click(self, pos):
        self.update_layout()
        if self.layout["btn_new"].collidepoint(pos):
            self.new_game()
        elif self.layout["btn_help"].collidepoint(pos):
            self.start_auto_fill()
        elif self.layout["btn_solve"].collidepoint(pos):
            self.solve_board()
        elif self.layout["btn_fs"].collidepoint(pos):
            self.is_fullscreen = not self.is_fullscreen
            info = pygame.display.Info()
            sz = (info.current_w, info.current_h) if self.is_fullscreen else (WINDOW_WIDTH, WINDOW_HEIGHT)
            flags = pygame.FULLSCREEN if self.is_fullscreen else 0
            self.screen = pygame.display.set_mode(sz, flags)
        elif self.layout["btn_4x4"].collidepoint(pos):
            self.board_mode = 4
            set_board_size(4)
            self.new_game()
        elif self.layout["btn_9x9"].collidepoint(pos):
            self.board_mode = 9
            set_board_size(9)
            self.new_game()
        else:
            l, t, sz, px = self.layout["left"], self.layout["top"], self.layout["sz"], self.layout["px"]
            if l <= pos[0] < l + px and t <= pos[1] < t + px:
                self.selected = ((pos[1] - t) // sz, (pos[0] - l) // sz)

    def put_digit(self, digit):
        if not self.selected:
            return
        r, c = self.selected
        if self.is_fixed(r, c):
            return
        self.helper_cell = None
        self.wrong_cells = []
        self.auto_fill_moves = []
        self.auto_fill_index = 0
        self.board[r][c] = digit if digit != 0 else 0
        if digit != 0:
            self.move_count += 1
            self.session.update_moves(self.move_count)
        self.check_win()

    def handle_key(self, event):
        if event.key == pygame.K_n:
            self.new_game()
        elif event.key == pygame.K_f:
            self.is_fullscreen = not self.is_fullscreen
            info = pygame.display.Info()
            sz = (info.current_w, info.current_h) if self.is_fullscreen else (WINDOW_WIDTH, WINDOW_HEIGHT)
            flags = pygame.FULLSCREEN if self.is_fullscreen else 0
            self.screen = pygame.display.set_mode(sz, flags)
        elif event.key in (pygame.K_BACKSPACE, pygame.K_DELETE, pygame.K_0, pygame.K_KP0):
            self.put_digit(0)
        else:
            key_map = {
                pygame.K_1: 1, pygame.K_2: 2, pygame.K_3: 3, pygame.K_4: 4, pygame.K_5: 5,
                pygame.K_6: 6, pygame.K_7: 7, pygame.K_8: 8, pygame.K_9: 9,
                pygame.K_KP1: 1, pygame.K_KP2: 2, pygame.K_KP3: 3, pygame.K_KP4: 4, pygame.K_KP5: 5,
                pygame.K_KP6: 6, pygame.K_KP7: 7, pygame.K_KP8: 8, pygame.K_KP9: 9
            }
            if event.key in key_map and key_map[event.key] <= BOARD_SIZE:
                self.put_digit(key_map[event.key])

    def draw(self):
        self.update_layout()
        self.screen.fill(BG_COLOR)
        
        # Buttons in right column
        self.draw_button(self.layout["btn_new"], "New Game")
        self.draw_button(self.layout["btn_help"], "Help")
        self.draw_button(self.layout["btn_solve"], "Solve Board")
        label = "Windowed" if self.is_fullscreen else "Fullscreen"
        self.draw_button(self.layout["btn_fs"], label)
        self.draw_button(self.layout["btn_4x4"], "4x4 Board")
        self.draw_button(self.layout["btn_9x9"], "9x9 Board")
        
        # Title
        title = self.fonts['title'].render(f"Sudoku {BOARD_SIZE}x{BOARD_SIZE}", True, THICK_GRID_COLOR)
        self.screen.blit(title, title.get_rect(center=(self.layout["w"] // 2, 38)))
        
        # Board
        l, t, sz, px = self.layout["left"], self.layout["top"], self.layout["sz"], self.layout["px"]
        pygame.draw.rect(self.screen, (255, 255, 255), (l, t, px, px))
        
        # Highlight cells
        if self.selected:
            r, c = self.selected
            pygame.draw.rect(self.screen, SELECT_COLOR, (l + c*sz, t + r*sz, sz, sz))
        for r, c in self.wrong_cells:
            pygame.draw.rect(self.screen, RED_BG, (l + c*sz, t + r*sz, sz, sz))
        if self.helper_cell:
            r, c, _ = self.helper_cell
            pygame.draw.rect(self.screen, GREEN_BG, (l + c*sz, t + r*sz, sz, sz))
        
        # Numbers
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if self.helper_cell and (r, c) == (self.helper_cell[0], self.helper_cell[1]):
                    helper_val = self.helper_cell[2]
                    surf = self.fonts['number'].render(str(helper_val), True, SUCCESS_COLOR)
                    self.screen.blit(surf, surf.get_rect(center=(l + c*sz + sz//2, t + r*sz + sz//2)))
                    continue

                val = self.board[r][c]
                if val == 0:
                    continue
                color = FIXED_TEXT_COLOR if self.is_fixed(r, c) else USER_TEXT_COLOR
                surf = self.fonts['number'].render(str(val), True, color)
                self.screen.blit(surf, surf.get_rect(center=(l + c*sz + sz//2, t + r*sz + sz//2)))
        
        # Grid lines
        for i in range(BOARD_SIZE + 1):
            w = 4 if i % SUBGRID_SIZE == 0 else 1
            col = THICK_GRID_COLOR if w == 4 else GRID_COLOR
            pygame.draw.line(self.screen, col, (l + i*sz, t), (l + i*sz, t + px), w)
            pygame.draw.line(self.screen, col, (l, t + i*sz), (l + px, t + i*sz), w)
        
        # Move counter
        moves = self.fonts['small'].render(f"Moves: {self.move_count}", True, (50, 50, 50))
        self.screen.blit(moves, (18, self.layout["msg_y"]))

        pygame.display.flip()

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.handle_click(event.pos)
                elif event.type == pygame.KEYDOWN:
                    self.handle_key(event)
            self.update_auto_fill()
            self.draw()
            self.clock.tick(60)

if __name__ == "__main__":
    game = SudokuGame()
    game.run()

