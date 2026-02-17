import random
import tkinter as tk


WALL = "#"
PATH = " "


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


class MazeGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Maze")

        self.size = 21
        self.cell = 24
        self.grid = make_grid(self.size, self.size)
        carve_maze(self.grid, 1, 1)

        self.player = (1, 1)
        self.goal = (self.size - 2, self.size - 2)

        self.info = tk.Label(root, text="Use arrow keys or WASD. Press R to reset.")
        self.info.pack(fill="x", padx=8, pady=6)

        self.canvas = tk.Canvas(
            root,
            width=self.size * self.cell,
            height=self.size * self.cell,
            bg="#111111",
            highlightthickness=0,
        )
        self.canvas.pack(padx=8, pady=8)

        self.status = tk.Label(root, text="Reach the green goal.", anchor="w")
        self.status.pack(fill="x", padx=8, pady=(0, 8))

        self.root.bind("<Key>", self.on_key)
        self.draw()

    def reset(self):
        self.grid = make_grid(self.size, self.size)
        carve_maze(self.grid, 1, 1)
        self.player = (1, 1)
        self.goal = (self.size - 2, self.size - 2)
        self.status.configure(text="New maze.")
        self.draw()

    def draw(self):
        self.canvas.delete("all")
        for r in range(self.size):
            for c in range(self.size):
                x1 = c * self.cell
                y1 = r * self.cell
                x2 = x1 + self.cell
                y2 = y1 + self.cell
                if self.grid[r][c] == WALL:
                    color = "#2f3640"
                else:
                    color = "#f5f6fa"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline=color)

        pr, pc = self.player
        gr, gc = self.goal
        self.canvas.create_rectangle(
            gc * self.cell,
            gr * self.cell,
            (gc + 1) * self.cell,
            (gr + 1) * self.cell,
            fill="#44bd32",
            outline="#44bd32",
        )
        self.canvas.create_oval(
            pc * self.cell + 3,
            pr * self.cell + 3,
            (pc + 1) * self.cell - 3,
            (pr + 1) * self.cell - 3,
            fill="#273c75",
            outline="#273c75",
        )

    def move(self, dr, dc):
        nr = self.player[0] + dr
        nc = self.player[1] + dc
        if self.grid[nr][nc] == WALL:
            self.status.configure(text="Blocked.")
            return
        self.player = (nr, nc)
        if self.player == self.goal:
            self.status.configure(text="You reached the goal. Press R to reset.")
        else:
            self.status.configure(text="Keep going.")
        self.draw()

    def on_key(self, event):
        key = event.keysym.lower()
        if key in {"r"}:
            self.reset()
            return
        if key in {"up", "w"}:
            self.move(-1, 0)
        elif key in {"down", "s"}:
            self.move(1, 0)
        elif key in {"left", "a"}:
            self.move(0, -1)
        elif key in {"right", "d"}:
            self.move(0, 1)


def main():
    root = tk.Tk()
    MazeGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
