from pathlib import Path
from PIL import Image
import numpy as np


def _rgb_to_hex(rgb):
    r, g, b = rgb
    return f"#{r:02x}{g:02x}{b:02x}"


def _find_palette_index(color, palette, threshold):
    """Return index of close-enough color in palette, else None."""
    for idx, p in enumerate(palette):
        if max(abs(color[0] - p[0]), abs(color[1] - p[1]), abs(color[2] - p[2])) <= threshold:
            return idx
    return None


def extract_board_colors(path: str, grid_size: int = 8, color_match_threshold: int = 10):
    """
    Generate a numeric grid where each distinct cell color is assigned a unique number,
    with a small tolerance when grouping similar colors.
    Also returns the palette list (hex strings) so numbers can be mapped back to colors.
    Assumes an empty board: every cell is uniformly colored with no pieces to ignore.
    """
    img = Image.open(path).convert("RGB")
    w, h = img.size

    cw, ch = w / grid_size, h / grid_size
    sample_offsets = [0.25, 0.5, 0.75]  # sample well inside each cell

    color_grid = []
    for r in range(grid_size):
        row = []
        for c in range(grid_size):
            samples = []
            for dy in sample_offsets:
                for dx in sample_offsets:
                    x = min(int((c + dx) * cw), w - 1)
                    y = min(int((r + dy) * ch), h - 1)
                    samples.append(img.getpixel((x, y)))

            avg = np.mean(samples, axis=0)
            r0, g0, b0 = [int(round(v)) for v in avg]
            row.append((r0, g0, b0))
        color_grid.append(row)

    palette = []
    numeric_grid = []
    for row in color_grid:
        num_row = []
        for color in row:
            idx = _find_palette_index(color, palette, color_match_threshold)
            if idx is None:
                idx = len(palette)
                palette.append(color)
            num_row.append(idx)
        numeric_grid.append(num_row)

    palette_hex = [_rgb_to_hex(c) for c in palette]
    return numeric_grid, palette_hex


def solve_colored_queens(region_grid):
    """
    Solve the 'colored regions queens' puzzle.
    Constraints:
      - exactly one queen per region (color)
      - no same row
      - no same column
      - no adjacent queens (including diagonals)
    Returns:
      dict: {region_id: (row, col)} or None if no solution.
    """
    rows = len(region_grid)
    cols = len(region_grid[0]) if rows else 0

    # Map each region id to its candidate cells
    regions = {}
    for r, row in enumerate(region_grid):
        for c, region_id in enumerate(row):
            regions.setdefault(region_id, []).append((r, c))

    # Quick feasibility check
    for region_id, cells in regions.items():
        if not cells:
            return None

    region_order = sorted(regions.keys(), key=lambda rid: len(regions[rid]))

    used_rows = set()
    used_cols = set()
    blocked = set()  # cells where a queen cannot be placed (occupied or adjacent)
    placement = {}

    def add_blockers(r, c, target_set):
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols:
                    target_set.add((nr, nc))

    def backtrack(idx):
        if idx == len(region_order):
            return True

        rid = region_order[idx]
        for (r, c) in regions[rid]:
            if r in used_rows or c in used_cols:
                continue
            if (r, c) in blocked:
                continue

            # Place queen
            placement[rid] = (r, c)
            used_rows.add(r)
            used_cols.add(c)

            new_blocked = set()
            add_blockers(r, c, new_blocked)
            newly_added = new_blocked - blocked
            blocked.update(newly_added)

            if backtrack(idx + 1):
                return True

            # Undo
            blocked.difference_update(newly_added)
            used_rows.remove(r)
            used_cols.remove(c)
            del placement[rid]

        return False

    solved = backtrack(0)
    return placement if solved else None


def format_solution(region_grid, solution):
    """Return a printable board with 'Q' on placed queens."""
    rows = len(region_grid)
    cols = len(region_grid[0]) if rows else 0
    board = [["." for _ in range(cols)] for _ in range(rows)]
    if solution:
        for _, (r, c) in solution.items():
            board[r][c] = "Q"
    return "\n".join(" ".join(row) for row in board)


def save_solution_image(board_path, region_grid, solution, crown_path="crown.png"):
    """
    Save a copy of the board image with crowns placed at the solved queen positions.
    Output is written next to the input as `{original_name}_solution.png`.
    """
    base = Path(board_path)
    out_path = base.with_name(f"{base.stem}_solution.png")

    img = Image.open(board_path).convert("RGBA")
    crown = Image.open(crown_path).convert("RGBA")

    rows = len(region_grid)
    cols = len(region_grid[0]) if rows else 0
    if rows == 0 or cols == 0:
        return None

    cw = img.width / cols
    ch = img.height / rows
    crown_scale = 0.7  # fraction of cell size
    target_w = int(cw * crown_scale)
    target_h = int(ch * crown_scale)
    crown_resized = crown.resize((target_w, target_h), Image.LANCZOS)

    canvas = img.copy()
    for _, (r, c) in solution.items():
        cx = int((c + 0.5) * cw)
        cy = int((r + 0.5) * ch)
        x0 = cx - target_w // 2
        y0 = cy - target_h // 2
        canvas.alpha_composite(crown_resized, (x0, y0))

    canvas.save(out_path)
    return out_path


if __name__ == "__main__":
    cases = [("1.png", 9), ("2.png", 8), ("3.png", 7), ("4.png", 8)]
    for path, size in cases:
        print(f"\nFile: {path}, grid_size={size}")
        numeric_grid, palette = extract_board_colors(path, size)
        print("Palette (index -> color):", palette)
        for row in numeric_grid:
            print(row)

        solution = solve_colored_queens(numeric_grid)
        if solution is None:
            print("No solution found.")
        else:
            print("Solution (region_id -> (row, col)):", solution)
            print("Board visualization:")
            print(format_solution(numeric_grid, solution))
            out = save_solution_image(path, numeric_grid, solution, crown_path="crown.png")
            if out:
                print(f"Saved solution image to {out}")
