import atexit
import sys
from datetime import datetime

import mysql.connector as mysql_connector


DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "mysql",
    "database": "gamesense",
    "port": 3306,
}


def get_connection():
    return mysql_connector.connect(**DB_CONFIG)


def save_game_result(game, outcome, moves=None, play_time=None):
    if play_time is None:
        play_time = datetime.now().strftime("%H:%M:%S")

    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            "INSERT INTO history (play_time, game, outcome, moves) VALUES (%s, %s, %s, %s)",
            (play_time, game, outcome, moves),
        )
        connection.commit()
    finally:
        cursor.close()
        connection.close()


def save_win(game, moves=None, play_time=None):
    save_game_result(game, "win", moves, play_time)


def save_loss(game, moves=None, play_time=None):
    save_game_result(game, "lost", moves, play_time)


def save_closed_game(game, moves=None, play_time=None):
    save_game_result(game, "lost", moves, play_time)


class GameSession:
    def __init__(self, game_name, moves=0):
        self.game_name = game_name
        self.moves = moves
        self.saved = False
        atexit.register(self._save_loss_on_exit)

    def update_moves(self, moves):
        self.moves = moves

    def record_win(self, moves=None):
        if moves is not None:
            self.moves = moves
        if not self.saved:
            save_win(self.game_name, self.moves)
            self.saved = True

    def record_loss(self, moves=None):
        if moves is not None:
            self.moves = moves
        if not self.saved:
            save_loss(self.game_name, self.moves)
            self.saved = True

    def record_close(self, moves=None):
        if moves is not None:
            self.moves = moves
        if not self.saved:
            save_closed_game(self.game_name, self.moves)
            self.saved = True

    def _save_loss_on_exit(self):
        if not self.saved:
            try:
                save_closed_game(self.game_name, self.moves)
                self.saved = True
            except Exception as exc:
                sys.stderr.write(f"Could not save game result: {exc}\n")


if __name__ == "__main__":
    connection = get_connection()
    connection.close()
    print("MySQL connection is working.")
