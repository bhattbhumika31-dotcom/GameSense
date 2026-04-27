# Game Sense

A Python + Pygame mini-game collection with a launcher menu, local multiplayer support, and game history tracking.

## Included Games

- `Sudoku`
  A playable Sudoku game with move counting, help, solve, fullscreen toggle, and board-size switching.
- `Maze Game`
  A maze runner with easy, medium, and hard modes, DFS hint support, and move counting.
- `Go Game`
  A basic 9x9 Go board with capture tracking, hint support, and a reset button.
- `Chess`
  A full 8x8 chess game with move validation, castling, en passant, undo, and hint support.
- `Multiplayer`
  Host or join a multiplayer session for Chess or Go using `server.py` and `client.py`.

## Files

- `main_menu.py`
  Launcher menu for local games, multiplayer host/join, and game history.
- `sudoku.py`
  Main Sudoku game implementation.
- `sudoku_helper.py`
  Sudoku puzzle generation and helper logic.
- `maze_game.py`
  Maze game implementation with difficulty selection and hints.
- `go.py`
  Go game implementation for 9x9 boards.
- `go_hint.py`
  Go hint generation and helper code.
- `chess_game.py`
  Chess game implementation and renderer.
- `chess_helper.py`
  Chess move suggestion and helper logic.
- `server.py`
  Host multiplayer sessions for Chess or Go.
- `client.py`
  Join multiplayer sessions and control a remote game.
- `connectivity.py`
  Networking and game history persistence support.

## Requirements

- Python 3.x
- `pygame`

Install `pygame` with:

```bash
pip install pygame
```

## How To Run

Start the menu:

```bash
python main_menu.py
```

You can also run games directly:

```bash
python sudoku.py
python maze_game.py
python go.py
python chess_game.py
```

For multiplayer sessions:

```bash
python server.py
python client.py
```

## Controls

### Main Menu

- Click a game button to launch it
- Click `Host Multiplayer` or `Join Multiplayer` for network play
- Press `Esc` to close the menu

### Sudoku

- Click a cell to select it
- Press a number key to enter a digit
- `Backspace`, `Delete`, or `0` clears a selected cell
- `N` starts a new game
- `F` toggles fullscreen
- Buttons offer `Help`, `Solve Board`, and board-size switching

### Maze Game

- Use arrow keys or `W A S D` to move
- `1`, `2`, `3` switch between easy, medium, and hard
- `H` shows a DFS hint path
- `R` resets the maze

### Go Game

- Click board intersections to place stones
- Use the side panel for game state and reset controls

### Chess

- Click pieces to select and move
- Supports legal moves, castling, en passant, and pawn promotion
- `U` undoes the last move
- `R` resets the current game
- Hint support is available during gameplay

## Notes

- The launcher includes history viewing from `connectivity.py`.
- The project is intended for learning game development with Python and Pygame.
- `server.py` and `client.py` use sockets for local network play.
