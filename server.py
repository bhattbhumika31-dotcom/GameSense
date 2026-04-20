import json
import queue
import socket
import sys
import threading

import pygame

import chess_game
from connectivity import GameSession


HOST = "0.0.0.0"
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


def get_local_ip():
    probe = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        probe.connect(("8.8.8.8", 80))
        return probe.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        probe.close()


def choose_game():
    while True:
        choice = input("Host which game? Enter 'chess' or 'go': ").strip().lower()
        if choice in {"chess", "go"}:
            return choice
        print("Please enter 'chess' or 'go'.")


def sync_chess_session(game, session):
    session.update_moves(len(game.history))
    if game.status == "checkmate":
        session.record_win(len(game.history))
    elif game.status == "stalemate":
        session.record_loss(len(game.history))


class ChessServerApp:
    game_name = "chess"

    def __init__(self):
        self.screen = pygame.display.set_mode((chess_game.WIN_W, chess_game.WIN_H))
        pygame.display.set_caption("Chess Server")
        self.clock = pygame.time.Clock()
        self.renderer = chess_game.Renderer(self.screen)
        self.game = chess_game.Game()
        self.session = GameSession("Chess")

    def state(self):
        return {
            "board": self.game.board,
            "turn": self.game.turn,
            "selected": self.game.selected,
            "sel_moves": self.game.sel_moves,
            "last_move": self.game.last_move,
            "notation": self.game.notation,
            "pending_note": self.game._pending_note,
            "status": self.game.status,
            "promoting": self.game.promoting,
            "hint_text": self.game.hint_text,
            "hint_move": self.game.hint_move,
            "history_len": len(self.game.history),
        }

    def draw(self):
        self.renderer.draw(self.game)
        pygame.display.flip()

    def reset_round(self):
        self.session.record_loss(len(self.game.history))
        self.game.reset()
        self.session = GameSession("Chess")

    def handle_key(self, key_name):
        if key_name == "r":
            self.reset_round()
            return True
        if key_name == "u":
            self.game.undo()
            sync_chess_session(self.game, self.session)
            return True
        return False

    def handle_click(self, pos):
        mx, my = pos
        if mx >= chess_game.BOARD_PX:
            if self.renderer.hint_button_rect().collidepoint(mx, my):
                self.game.request_hint()
                return True
            return False

        if self.game.promoting:
            piece = self.renderer.promo_click(mx, my, self.game)
            if piece:
                self.game.promote(piece)
                sync_chess_session(self.game, self.session)
                return True
            return False

        col = mx // chess_game.SQ
        row = my // chess_game.SQ
        self.game.click(row, col)
        sync_chess_session(self.game, self.session)
        return True

    def handle_input(self, message):
        kind = message.get("kind")
        if kind == "key":
            return self.handle_key(message.get("key", ""))
        if kind == "mouse" and message.get("button") == 1:
            return self.handle_click(tuple(message.get("pos", (0, 0))))
        return False

    def close(self):
        self.session.record_close(len(self.game.history))


class GoServerApp:
    game_name = "go"

    def __init__(self):
        self.screen = pygame.display.set_mode((GO_WINDOW_WIDTH, GO_WINDOW_HEIGHT))
        pygame.display.set_caption("Go Server")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 32)
        self.small_font = pygame.font.Font(None, 26)
        self.session = GameSession("Go Game")
        self.board = []
        self.current_player = "B"
        self.black_moves = 0
        self.white_moves = 0
        self.reset(initial=True)

    def reset(self, initial=False):
        if not initial:
            self.session.record_loss(self.black_moves + self.white_moves)
            self.session = GameSession("Go Game")
        self.board = [["." for _ in range(GO_SIZE)] for _ in range(GO_SIZE)]
        self.current_player = "B"
        self.black_moves = 0
        self.white_moves = 0

    def neighbors(self, row, col):
        offsets = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        return [
            (row + dr, col + dc)
            for dr, dc in offsets
            if 0 <= row + dr < GO_SIZE and 0 <= col + dc < GO_SIZE
        ]

    def dfs(self, row, col, visited):
        stack = [(row, col)]
        color = self.board[row][col]
        group = []
        has_liberty = False

        while stack:
            current_row, current_col = stack.pop()
            if (current_row, current_col) in visited:
                continue
            visited.add((current_row, current_col))
            group.append((current_row, current_col))

            for next_row, next_col in self.neighbors(current_row, current_col):
                if self.board[next_row][next_col] == ".":
                    has_liberty = True
                elif self.board[next_row][next_col] == color:
                    stack.append((next_row, next_col))

        return group, has_liberty

    def remove_captured(self, opponent):
        visited = set()
        for row in range(GO_SIZE):
            for col in range(GO_SIZE):
                if self.board[row][col] == opponent and (row, col) not in visited:
                    group, liberty = self.dfs(row, col, visited)
                    if not liberty:
                        for group_row, group_col in group:
                            self.board[group_row][group_col] = "."

    def count_liberties(self, row, col):
        visited = set()
        group, _ = self.dfs(row, col, visited)
        liberties = set()

        for group_row, group_col in group:
            for next_row, next_col in self.neighbors(group_row, group_col):
                if self.board[next_row][next_col] == ".":
                    liberties.add((next_row, next_col))

        return len(liberties)

    def get_position(self, pos):
        x, y = pos
        col = int((x - GO_MARGIN + GO_CELL_SIZE // 2) // GO_CELL_SIZE)
        row = int((y - GO_MARGIN + GO_CELL_SIZE // 2) // GO_CELL_SIZE)
        if 0 <= row < GO_SIZE and 0 <= col < GO_SIZE:
            return row, col
        return None

    def state(self):
        return {
            "board": self.board,
            "current_player": self.current_player,
            "black_moves": self.black_moves,
            "white_moves": self.white_moves,
        }

    def draw(self):
        self.screen.fill(GO_WOOD)

        for index in range(GO_SIZE):
            pygame.draw.line(
                self.screen,
                GO_LINE,
                (GO_MARGIN, GO_MARGIN + index * GO_CELL_SIZE),
                (GO_BOARD_SIZE - GO_MARGIN, GO_MARGIN + index * GO_CELL_SIZE),
            )
            pygame.draw.line(
                self.screen,
                GO_LINE,
                (GO_MARGIN + index * GO_CELL_SIZE, GO_MARGIN),
                (GO_MARGIN + index * GO_CELL_SIZE, GO_BOARD_SIZE - GO_MARGIN),
            )

        for row in range(GO_SIZE):
            for col in range(GO_SIZE):
                if self.board[row][col] != ".":
                    color = GO_BLACK if self.board[row][col] == "B" else GO_WHITE
                    pygame.draw.circle(
                        self.screen,
                        color,
                        (GO_MARGIN + col * GO_CELL_SIZE, GO_MARGIN + row * GO_CELL_SIZE),
                        GO_CELL_SIZE // 2 - 5,
                    )

        panel = pygame.Rect(GO_BOARD_SIZE, 0, GO_PANEL_WIDTH, GO_WINDOW_HEIGHT)
        pygame.draw.rect(self.screen, GO_PANEL_BG, panel)
        pygame.draw.line(self.screen, GO_LINE, (GO_BOARD_SIZE, 0), (GO_BOARD_SIZE, GO_WINDOW_HEIGHT), 2)

        title = self.font.render("Moves", True, GO_TEXT)
        self.screen.blit(title, (GO_BOARD_SIZE + 35, 40))

        black_text = self.small_font.render(f"Black: {self.black_moves}", True, GO_TEXT)
        self.screen.blit(black_text, (GO_BOARD_SIZE + 20, 100))

        white_text = self.small_font.render(f"White: {self.white_moves}", True, GO_TEXT)
        self.screen.blit(white_text, (GO_BOARD_SIZE + 20, 140))

        turn_label = "Black" if self.current_player == "B" else "White"
        turn_text = self.small_font.render(f"Turn: {turn_label}", True, GO_TEXT)
        self.screen.blit(turn_text, (GO_BOARD_SIZE + 20, 200))

        mouse_pos = pygame.mouse.get_pos()
        button_color = GO_BUTTON_HOVER if GO_RESET_BUTTON.collidepoint(mouse_pos) else GO_BUTTON
        pygame.draw.rect(self.screen, button_color, GO_RESET_BUTTON, border_radius=8)
        pygame.draw.rect(self.screen, GO_LINE, GO_RESET_BUTTON, 2, border_radius=8)

        reset_text = self.small_font.render("Reset", True, GO_WHITE)
        reset_rect = reset_text.get_rect(center=GO_RESET_BUTTON.center)
        self.screen.blit(reset_text, reset_rect)

        pygame.display.flip()

    def handle_click(self, pos):
        if GO_RESET_BUTTON.collidepoint(pos):
            self.reset()
            return True

        board_pos = self.get_position(pos)
        if board_pos is None:
            return False

        row, col = board_pos
        if self.board[row][col] != ".":
            return False

        self.board[row][col] = self.current_player
        opponent = "W" if self.current_player == "B" else "B"
        self.remove_captured(opponent)

        if self.count_liberties(row, col) == 0:
            self.board[row][col] = "."
            return False

        if self.current_player == "B":
            self.black_moves += 1
        else:
            self.white_moves += 1

        self.session.update_moves(self.black_moves + self.white_moves)
        self.current_player = opponent
        return True

    def handle_input(self, message):
        if message.get("kind") == "mouse" and message.get("button") == 1:
            return self.handle_click(tuple(message.get("pos", (0, 0))))
        return False

    def close(self):
        self.session.record_close(self.black_moves + self.white_moves)


def make_app(game_name):
    if game_name == "chess":
        return ChessServerApp()
    return GoServerApp()


def main():
    game_name = choose_game()

    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listener.bind((HOST, PORT))
    listener.listen(1)

    local_ip = get_local_ip()
    print(f"Server is listening on {local_ip}:{PORT}")
    print(f"Waiting for a client to join {game_name}...")

    client_socket, address = listener.accept()
    listener.close()
    print(f"Client connected from {address[0]}:{address[1]}")

    connection = JsonConnection(client_socket)

    pygame.init()
    app = make_app(game_name)
    connection.send({"type": "welcome", "game": game_name})
    connection.send({"type": "state", "game": game_name, "state": app.state()})

    running = True
    while running:
        dirty = False

        for message in connection.poll():
            if message.get("type") == "disconnect":
                print("Client disconnected.")
                running = False
                break
            if message.get("type") == "input" and app.handle_input(message):
                dirty = True

        if not running:
            break

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            if event.type == pygame.KEYDOWN:
                if isinstance(app, ChessServerApp):
                    if app.handle_input({"kind": "key", "key": pygame.key.name(event.key)}):
                        dirty = True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if app.handle_input({"kind": "mouse", "button": event.button, "pos": list(event.pos)}):
                    dirty = True

        if dirty:
            connection.send({"type": "state", "game": game_name, "state": app.state()})

        app.draw()
        app.clock.tick(60)

    app.close()
    connection.close()
    pygame.quit()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pygame.quit()
        sys.exit()
