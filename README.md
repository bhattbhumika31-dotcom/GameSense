# Game Sense

A small Python + Pygame mini-game collection with a launcher menu.

## Included Games

- `Sudoku`
  A playable Sudoku game with move counting, help, solve, fullscreen toggle, and board-size switching.
- `Maze Game`
  A maze runner with easy, medium, and hard modes, DFS hint support, and move counting.
- `Go Game`
  A basic 9x9 Go board with separate Black/White move counters and a reset button.

## Files

- `main_menu.py`
  Launches the project menu.
- `sudoku.py`
  Main Sudoku game.
- `sudoku_helper.py`
  Helper functions used by Sudoku.
- `maze_game.py`
  Maze game implementation.
- `go.py`
  Go game implementation.
- `go_hint.py`
  Extra Go-related file in the project folder.

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
```

## Controls

### Main Menu

- Click a game button to launch it
- `Esc` closes the menu

### Sudoku

- Click a cell to select it
- Number keys enter values
- `Backspace`, `Delete`, or `0` clears a selected cell
- Click `New Game` for a fresh puzzle
- Click `Help` to show the next suggested move
- Click `Solve Board` to auto-fill the puzzle
- Click `Fullscreen` to toggle fullscreen mode
- Click `4x4 Board` or `9x9 Board` to switch puzzle size
- `N` starts a new game
- `F` toggles fullscreen

Note:
- `4x4 Board` means a 4x4 Sudoku with 2x2 subgrids.
- `9x9 Board` means a standard Sudoku with 3x3 subgrids.

### Maze Game

- Arrow keys or `W A S D` move the player
- `1`, `2`, `3` switch between easy, medium, and hard
- `H` shows a DFS hint path
- `R` resets the maze
- The side panel shows the current mode, path length, and move count

### Go Game

- Click intersections to place stones
- The side panel shows Black moves, White moves, and the current turn
- Click `Reset` to clear the board and restart the game

## Notes

- The games are built with straightforward Python and Pygame code for learning and experimentation.
- Some files are procedural and some are still class-based depending on the game.
