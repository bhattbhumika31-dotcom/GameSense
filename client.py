import json
import queue
import socket
import sys
import threading

import pygame

import chess_game


PORT = 5000


GO_SIZE = 9
GO_CELL_SIZE = 60
GO_MARGIN = 40
GO_PANEL_WIDTH = 180
GO_BOARD_SIZE = GO_SIZE * GO_CELL_SIZE + 2 * GO_MARGIN
GO_WINDOW_WIDTH = GO_BOARD_SIZE + GO_PANEL_WIDTH
GO_WINDOW_HEIGHT = GO_BOARD_SIZE

GO_WOOD = (222, 184, 135)
GO_BLACK = (0, 0, 0)
GO_WHITE = (255, 255, 255)
GO_LINE = (0, 0, 0)
GO_TEXT = (40, 20, 0)
GO_PANEL_BG = (240, 220, 180)
GO_BUTTON = (180, 120, 70)
GO_BUTTON_HOVER = (200, 140, 90)
GO_RESET_BUTTON = pygame.Rect(GO_BOARD_SIZE + 30, 250, 120, 45)


class JsonConnection:
    def __init__(self, sock):
        self.sock = sock
        self.sock_file = sock.makefile("r", encoding="utf-8")
        self.messages = queue.Queue()
        self.alive = True
        self.lock = threading.Lock()
        self.thread = threading.Thread(target=self._reader, daemon=True)
        self.thread.start()

    def _reader(self):
        try:
            for line in self.sock_file:
                line = line.strip()
                if not line:
                    continue
                self.messages.put(json.loads(line))
        except Exception as exc:
            self.messages.put({"type": "disconnect", "error": str(exc)})
        finally:
            self.alive = False
            self.messages.put({"type": "disconnect"})

    def send(self, message):
        if not self.alive:
            return
        data = (json.dumps(message) + "\n").encode("utf-8")
        try:
            with self.lock:
                self.sock.sendall(data)
        except OSError:
            self.alive = False

    def poll(self):
        items = []
        while True:
            try:
                items.append(self.messages.get_nowait())
            except queue.Empty:
                return items

    def wait(self):
        return self.messages.get()

    def close(self):
        self.alive = False
        try:
            self.sock_file.close()
        except OSError:
            pass
        try:
            self.sock.close()
        except OSError:
            pass


class ChessMirror:
    def __init__(self):
        self.board = []
        self.turn = chess_game.WHITE
        self.selected = None
        self.sel_moves = []
        self.last_move = None
        self.notation = []
        self._pending_note = None
        self.status = "playing"
        self.promoting = False
        self.hint_text = ""
        self.hint_move = None
        self.history = []

    def update(self, state):
        raw_board = state.get("board", [])
        self.board = []
        for row in raw_board:
            new_row = []
            for cell in row:
                if isinstance(cell, list):
                    new_row.append(tuple(cell))
                else:
                    new_row.append(cell)
            self.board.append(new_row)
        self.turn = state.get("turn", chess_game.WHITE)
        self.selected = state.get("selected")
        self.sel_moves = state.get("sel_moves", [])
        self.last_move = state.get("last_move")
        self.notation = state.get("notation", [])
        self._pending_note = state.get("pending_note")
        self.status = state.get("status", "playing")
        self.promoting = state.get("promoting", False)
        self.hint_text = state.get("hint_text", "")
        self.hint_move = state.get("hint_move")
        self.history = [None] * state.get("history_len", 0)


def draw_go(screen, font, small_font, state):
    screen.fill(GO_WOOD)

    for index in range(GO_SIZE):
        pygame.draw.line(
            screen,
            GO_LINE,
            (GO_MARGIN, GO_MARGIN + index * GO_CELL_SIZE),
            (GO_BOARD_SIZE - GO_MARGIN, GO_MARGIN + index * GO_CELL_SIZE),
        )
        pygame.draw.line(
            screen,
            GO_LINE,
            (GO_MARGIN + index * GO_CELL_SIZE, GO_MARGIN),
            (GO_MARGIN + index * GO_CELL_SIZE, GO_BOARD_SIZE - GO_MARGIN),
        )

    board = state.get("board", [])
    for row in range(GO_SIZE):
        for col in range(GO_SIZE):
            if row < len(board) and col < len(board[row]) and board[row][col] != ".":
                color = GO_BLACK if board[row][col] == "B" else GO_WHITE
                pygame.draw.circle(
                    screen,
                    color,
                    (GO_MARGIN + col * GO_CELL_SIZE, GO_MARGIN + row * GO_CELL_SIZE),
                    GO_CELL_SIZE // 2 - 5,
                )

    panel = pygame.Rect(GO_BOARD_SIZE, 0, GO_PANEL_WIDTH, GO_WINDOW_HEIGHT)
    pygame.draw.rect(screen, GO_PANEL_BG, panel)
    pygame.draw.line(screen, GO_LINE, (GO_BOARD_SIZE, 0), (GO_BOARD_SIZE, GO_WINDOW_HEIGHT), 2)

    title = font.render("Moves", True, GO_TEXT)
    screen.blit(title, (GO_BOARD_SIZE + 35, 40))

    black_moves = state.get("black_moves", 0)
    white_moves = state.get("white_moves", 0)
    current_player = state.get("current_player", "B")

    black_text = small_font.render(f"Black: {black_moves}", True, GO_TEXT)
    screen.blit(black_text, (GO_BOARD_SIZE + 20, 100))

    white_text = small_font.render(f"White: {white_moves}", True, GO_TEXT)
    screen.blit(white_text, (GO_BOARD_SIZE + 20, 140))

    turn_label = "Black" if current_player == "B" else "White"
    turn_text = small_font.render(f"Turn: {turn_label}", True, GO_TEXT)
    screen.blit(turn_text, (GO_BOARD_SIZE + 20, 200))

    mouse_pos = pygame.mouse.get_pos()
    button_color = GO_BUTTON_HOVER if GO_RESET_BUTTON.collidepoint(mouse_pos) else GO_BUTTON
    pygame.draw.rect(screen, button_color, GO_RESET_BUTTON, border_radius=8)
    pygame.draw.rect(screen, GO_LINE, GO_RESET_BUTTON, 2, border_radius=8)

    reset_text = small_font.render("Reset", True, GO_WHITE)
    reset_rect = reset_text.get_rect(center=GO_RESET_BUTTON.center)
    screen.blit(reset_text, reset_rect)

    pygame.display.flip()


def connect_to_server():
    ip_address = input("Enter server IP address: ").strip() or "127.0.0.1"
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((ip_address, PORT))
    return JsonConnection(client_socket)


def receive_startup_messages(connection):
    game_name = None
    initial_state = None

    while game_name is None or initial_state is None:
        message = connection.wait()
        if message.get("type") == "disconnect":
            raise ConnectionError("Server disconnected before sending game data.")
        if message.get("type") == "welcome":
            game_name = message.get("game")
        elif message.get("type") == "state":
            initial_state = message.get("state")

    return game_name, initial_state


def main():
    try:
        connection = connect_to_server()
    except OSError as exc:
        print(f"Could not connect to server: {exc}")
        return

    try:
        game_name, state = receive_startup_messages(connection)
    except ConnectionError as exc:
        connection.close()
        print(exc)
        return

    pygame.init()

    if game_name == "chess":
        screen = pygame.display.set_mode((chess_game.WIN_W, chess_game.WIN_H))
        pygame.display.set_caption("Chess Client")
        renderer = chess_game.Renderer(screen)
        view = ChessMirror()
        view.update(state)
        go_font = None
        go_small_font = None
    elif game_name == "go":
        screen = pygame.display.set_mode((GO_WINDOW_WIDTH, GO_WINDOW_HEIGHT))
        pygame.display.set_caption("Go Client")
        renderer = None
        view = None
        go_font = pygame.font.Font(None, 32)
        go_small_font = pygame.font.Font(None, 26)
    else:
        connection.close()
        print(f"Unsupported game sent by server: {game_name}")
        return

    clock = pygame.time.Clock()
    running = True

    while running:
        for message in connection.poll():
            if message.get("type") == "disconnect":
                print("Server disconnected.")
                running = False
                break
            if message.get("type") == "state":
                state = message.get("state", state)
                if game_name == "chess":
                    view.update(state)

        if not running:
            break

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            if event.type == pygame.KEYDOWN and game_name == "chess":
                key_name = pygame.key.name(event.key)
                if key_name in {"r", "u"}:
                    connection.send({"type": "input", "kind": "key", "key": key_name})
            elif event.type == pygame.MOUSEBUTTONDOWN:
                connection.send(
                    {
                        "type": "input",
                        "kind": "mouse",
                        "button": event.button,
                        "pos": list(event.pos),
                    }
                )

        if game_name == "chess":
            renderer.draw(view)
            pygame.display.flip()
        else:
            draw_go(screen, go_font, go_small_font, state)

        clock.tick(60)

    connection.close()
    pygame.quit()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pygame.quit()
        sys.exit()
