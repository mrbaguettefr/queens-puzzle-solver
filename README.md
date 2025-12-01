Queens Puzzle Solver
====================

Extracts colors from board images, assigns a unique region id per color, and solves the “colored regions queens” puzzle: one queen per region, with no shared rows/columns and no adjacent queens (including diagonals). When a solution exists, it renders a `{name}_solution.png` overlaying crowns at the queen positions.

Requirements
------------
- Python 3.12+
- Dependencies are in `pyproject.toml` (`numpy`, `pillow`). Install with `uv sync` or your preferred installer.

Usage
-----
```
python main.py
```

By default the script processes:
- `1.png` with `grid_size=9`
- `2.png` with `grid_size=8`
- `3.png` with `grid_size=8`

For each image it prints:
- Palette (index -> hex color)
- Numeric grid of region ids
- A text visualization of the queen placement

If solvable, it writes `{original_name}_solution.png` beside the input using `crown.png` for the queen marker.

Adapting
--------
- Update the `cases` list in `main.py` to point to your images and grid sizes.
- Adjust `color_match_threshold` in `extract_board_colors` if colors are noisy and you want looser/tighter grouping.

Files
-----
- `main.py` — color extraction, puzzle solver, solution overlay.
- `1.png`, `2.png`, `3.png` — sample boards.
- `crown.png` — marker used when rendering solutions.
