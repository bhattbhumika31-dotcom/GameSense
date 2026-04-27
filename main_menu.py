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
TABLE_HEADER = (229, 220, 206)
TABLE_ROW = (252, 248, 241)
TABLE_ALT_ROW = (244, 237, 225)
TABLE_TEXT = (52, 52, 52)
SECONDARY_BUTTON = (235, 227, 213)
SECONDARY_HOVER = (225, 215, 198)
SECONDARY_TEXT = (55, 55, 55)
ERROR_COLOR = (165, 55, 55)

BASE_DIR = Path(__file__).resolve().parent
PANEL_RECT = pygame.Rect(80, 35, 740, 530)
ROWS_PER_PAGE = 8

MENU_ITEMS = [
    ("Sudoku", "launch", "sudoku.py"),
    ("Maze Game", "launch", "maze_game.py"),
    ("Go Game", "launch", "go.py"),
    ("Chess", "launch", "chess_game.py"),
    ("Host Multiplayer", "launch", "server.py"),
    ("Join Multiplayer", "launch", "client.py"),
    ("View History", "history", None),
]


def build_buttons():
    buttons = []
    button_width = 300
    button_height = 44
    gap = 8
    start_x = (WINDOW_WIDTH - button_width) // 2
    start_y = 150

    for index, (label, action, target) in enumerate(MENU_ITEMS):
        rect = pygame.Rect(
            start_x,
            start_y + index * (button_height + gap),
            button_width,
            button_height,
        )
        buttons.append({"label": label, "action": action, "target": target, "rect": rect})

    return buttons


def build_history_buttons():
    bottom = PANEL_RECT.bottom - 56
    return {
        "back": pygame.Rect(PANEL_RECT.left + 36, bottom, 140, 40),
        "refresh": pygame.Rect(PANEL_RECT.right - 176, bottom, 140, 40),
    }


def launch_game(filename):
    kwargs = {"cwd": BASE_DIR}
    if filename in {"server.py", "client.py"} and sys.platform == "win32":
        kwargs["creationflags"] = subprocess.CREATE_NEW_CONSOLE
    subprocess.Popen([sys.executable, str(BASE_DIR / filename)], **kwargs)


def fetch_history_rows():
    from connectivity import fetch_history

    try:
        return fetch_history(), ""
    except Exception as exc:
        return [], f"Could not load history: {exc}"


def format_history_value(value):
    if value is None:
        return "-"
    if hasattr(value, "strftime"):
        return value.strftime("%H:%M:%S")
    return str(value)


def fit_text(text, font, max_width):
    if font.size(text)[0] <= max_width:
        return text

    trimmed = text
    while trimmed and font.size(f"{trimmed}...")[0] > max_width:
        trimmed = trimmed[:-1]
    return f"{trimmed.rstrip()}..."


def wrap_text(text, font, max_width):
    words = text.split()
    if not words:
        return [""]

    lines = []
    current = words[0]
    for word in words[1:]:
        candidate = f"{current} {word}"
        if font.size(candidate)[0] <= max_width:
            current = candidate
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def clamp_scroll(scroll, rows):
    max_scroll = max(0, len(rows) - ROWS_PER_PAGE)
    return max(0, min(scroll, max_scroll))


def draw_button(screen, font, button, mouse_pos, secondary=False):
    idle_color = SECONDARY_BUTTON if secondary else BUTTON_COLOR
    hover_color = SECONDARY_HOVER if secondary else BUTTON_HOVER
    text_color = SECONDARY_TEXT if secondary else BUTTON_TEXT
    color = hover_color if button["rect"].collidepoint(mouse_pos) else idle_color
    pygame.draw.rect(screen, color, button["rect"], border_radius=12)
    text = font.render(button["label"], True, text_color)
    screen.blit(text, text.get_rect(center=button["rect"].center))


def draw_menu(screen, fonts, buttons):
    screen.fill(BG_COLOR)

    panel = PANEL_RECT
    pygame.draw.rect(screen, PANEL_COLOR, panel, border_radius=18)
    pygame.draw.rect(screen, BORDER_COLOR, panel, 2, border_radius=18)

    title = fonts["title"].render("Game Sense", True, TITLE_COLOR)
    subtitle = fonts["body"].render("Choose a game, multiplayer mode, or saved history", True, SUBTITLE_COLOR)

    screen.blit(title, title.get_rect(center=(WINDOW_WIDTH // 2, 90)))
    screen.blit(subtitle, subtitle.get_rect(center=(WINDOW_WIDTH // 2, 125)))

    mouse_pos = pygame.mouse.get_pos()
    for button in buttons:
        secondary = button["action"] == "history"
        draw_button(screen, fonts["button"], button, mouse_pos, secondary=secondary)

    footer = fonts["small"].render("Press Esc to close the menu", True, SUBTITLE_COLOR)
    screen.blit(footer, footer.get_rect(center=(WINDOW_WIDTH // 2, 545)))

    pygame.display.flip()


def draw_history(screen, fonts, rows, error_message, scroll_offset, buttons):
    screen.fill(BG_COLOR)

    panel = PANEL_RECT
    pygame.draw.rect(screen, PANEL_COLOR, panel, border_radius=18)
    pygame.draw.rect(screen, BORDER_COLOR, panel, 2, border_radius=18)

    title = fonts["title"].render("Game History", True, TITLE_COLOR)
    subtitle = fonts["body"].render("Records fetched from the database", True, SUBTITLE_COLOR)
    screen.blit(title, title.get_rect(center=(WINDOW_WIDTH // 2, 90)))
    screen.blit(subtitle, subtitle.get_rect(center=(WINDOW_WIDTH // 2, 125)))

    table_rect = pygame.Rect(panel.left + 30, panel.top + 120, panel.width - 60, 290)
    header_rect = pygame.Rect(table_rect.left, table_rect.top, table_rect.width, 36)
    pygame.draw.rect(screen, TABLE_HEADER, header_rect, border_radius=10)
    pygame.draw.rect(screen, BORDER_COLOR, table_rect, 1, border_radius=10)

    columns = [
        ("Time", 160),
        ("Game", 240),
        ("Outcome", 140),
        ("Moves", 110),
    ]

    x = table_rect.left + 14
    for header, width in columns:
        text = fonts["table_header"].render(header, True, TITLE_COLOR)
        screen.blit(text, (x, header_rect.y + 8))
        x += width

    if error_message:
        lines = wrap_text(error_message, fonts["body"], table_rect.width - 40)
        for index, line in enumerate(lines[:4]):
            text = fonts["body"].render(line, True, ERROR_COLOR)
            screen.blit(text, (table_rect.left + 20, table_rect.top + 70 + index * 30))
    elif not rows:
        empty_text = fonts["body"].render("No history records found yet.", True, SUBTITLE_COLOR)
        screen.blit(empty_text, empty_text.get_rect(center=table_rect.center))
    else:
        visible_rows = rows[scroll_offset : scroll_offset + ROWS_PER_PAGE]
        row_height = 31
        for index, row in enumerate(visible_rows):
            row_rect = pygame.Rect(
                table_rect.left + 1,
                table_rect.top + 37 + index * row_height,
                table_rect.width - 2,
                row_height,
            )
            row_color = TABLE_ROW if index % 2 == 0 else TABLE_ALT_ROW
            pygame.draw.rect(screen, row_color, row_rect)

            values = [
                format_history_value(row.get("play_time")),
                format_history_value(row.get("game")),
                format_history_value(row.get("outcome")).title(),
                format_history_value(row.get("moves")),
            ]

            x = table_rect.left + 14
            for value, (_, width) in zip(values, columns):
                text_value = fit_text(value, fonts["table"], width - 18)
                text = fonts["table"].render(text_value, True, TABLE_TEXT)
                screen.blit(text, (x, row_rect.y + 7))
                x += width

    mouse_pos = pygame.mouse.get_pos()
    for button in buttons.values():
        draw_button(screen, fonts["small"], button, mouse_pos, secondary=True)

    pygame.display.flip()


def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Main Menu")

    fonts = {
        "title": pygame.font.SysFont("arial", 42, bold=True),
        "button": pygame.font.SysFont("arial", 24, bold=True),
        "body": pygame.font.SysFont("arial", 24),
        "small": pygame.font.SysFont("arial", 20),
        "table_header": pygame.font.SysFont("arial", 20, bold=True),
        "table": pygame.font.SysFont("arial", 19),
    }
    buttons = build_buttons()
    history_buttons = {
        key: {"label": key.title(), "rect": rect}
        for key, rect in build_history_buttons().items()
    }
    clock = pygame.time.Clock()
    view = "menu"
    history_rows = []
    history_error = ""
    history_scroll = 0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif view == "menu":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for button in buttons:
                        if not button["rect"].collidepoint(event.pos):
                            continue
                        if button["action"] == "launch":
                            launch_game(button["target"])
                        else:
                            history_rows, history_error = fetch_history_rows()
                            history_scroll = 0
                            view = "history"
                        break
            else:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        view = "menu"
                    elif event.key in (pygame.K_UP, pygame.K_w):
                        history_scroll = clamp_scroll(history_scroll - 1, history_rows)
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        history_scroll = clamp_scroll(history_scroll + 1, history_rows)
                elif event.type == pygame.MOUSEWHEEL:
                    history_scroll = clamp_scroll(history_scroll - event.y, history_rows)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if history_buttons["back"]["rect"].collidepoint(event.pos):
                            view = "menu"
                        elif history_buttons["refresh"]["rect"].collidepoint(event.pos):
                            history_rows, history_error = fetch_history_rows()
                            history_scroll = clamp_scroll(history_scroll, history_rows)
                    elif event.button == 4:
                        history_scroll = clamp_scroll(history_scroll - 1, history_rows)
                    elif event.button == 5:
                        history_scroll = clamp_scroll(history_scroll + 1, history_rows)

        if view == "menu":
            draw_menu(screen, fonts, buttons)
        else:
            draw_history(screen, fonts, history_rows, history_error, history_scroll, history_buttons)
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
