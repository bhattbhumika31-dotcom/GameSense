import subprocess
import sys
from pathlib import Path

import pygame

WINDOW_WIDTH = 900
WINDOW_HEIGHT = 600

BG_COLOR = (241, 234, 220)
PANEL_COLOR = (255, 250, 242)
TITLE_COLOR = (45, 45, 45)
SUBTITLE_COLOR = (90, 90, 90)
BUTTON_COLOR = (61, 122, 196)
BUTTON_HOVER = (88, 148, 220)
BUTTON_TEXT = (255, 255, 255)
BORDER_COLOR = (210, 198, 180)

BASE_DIR = Path(__file__).resolve().parent

MENU_ITEMS = [
    ("Sudoku", "sudoku.py"),
    ("Maze Game", "maze_game.py"),
    ("Go Game", "go.py"),
    ("Chess", "chess_game.py"),
    ("Host Multiplayer", "server.py"),
    ("Join Multiplayer", "client.py"),
]


def build_buttons():
    buttons = []
    button_width = 280
    button_height = 50
    gap = 12
    start_x = (WINDOW_WIDTH - button_width) // 2
    start_y = 160

    for index, (label, filename) in enumerate(MENU_ITEMS):
        rect = pygame.Rect(
            start_x,
            start_y + index * (button_height + gap),
            button_width,
            button_height,
        )
        buttons.append({"label": label, "file": filename, "rect": rect})

    return buttons


def launch_game(filename):
    kwargs = {"cwd": BASE_DIR}
    if filename in {"server.py", "client.py"} and sys.platform == "win32":
        kwargs["creationflags"] = subprocess.CREATE_NEW_CONSOLE
    subprocess.Popen([sys.executable, str(BASE_DIR / filename)], **kwargs)


def draw_menu(screen, fonts, buttons):
    screen.fill(BG_COLOR)

    panel = pygame.Rect(150, 35, 600, 530)
    pygame.draw.rect(screen, PANEL_COLOR, panel, border_radius=18)
    pygame.draw.rect(screen, BORDER_COLOR, panel, 2, border_radius=18)

    title = fonts["title"].render("Game Sense", True, TITLE_COLOR)
    subtitle = fonts["body"].render("Choose a game or multiplayer mode", True, SUBTITLE_COLOR)

    screen.blit(title, title.get_rect(center=(WINDOW_WIDTH // 2, 90)))
    screen.blit(subtitle, subtitle.get_rect(center=(WINDOW_WIDTH // 2, 125)))

    mouse_pos = pygame.mouse.get_pos()
    for button in buttons:
        color = BUTTON_HOVER if button["rect"].collidepoint(mouse_pos) else BUTTON_COLOR
        pygame.draw.rect(screen, color, button["rect"], border_radius=12)
        text = fonts["button"].render(button["label"], True, BUTTON_TEXT)
        screen.blit(text, text.get_rect(center=button["rect"].center))

    footer = fonts["small"].render("Press Esc to close the menu", True, SUBTITLE_COLOR)
    screen.blit(footer, footer.get_rect(center=(WINDOW_WIDTH // 2, 545)))

    pygame.display.flip()


def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Main Menu")

    fonts = {
        "title": pygame.font.SysFont("arial", 42, bold=True),
        "button": pygame.font.SysFont("arial", 28, bold=True),
        "body": pygame.font.SysFont("arial", 24),
        "small": pygame.font.SysFont("arial", 20),
    }
    buttons = build_buttons()
    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for button in buttons:
                    if button["rect"].collidepoint(event.pos):
                        launch_game(button["file"])
                        break

        draw_menu(screen, fonts, buttons)
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
