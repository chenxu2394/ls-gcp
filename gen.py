import itertools

def generate_base_grid(width, height):
    grid = []
    for row in range(height):
        if row % 3 == 0:
            row_data = []
            for col in range(width):
                row_data.append('r' if col % 8 else 'Q')
            grid.append(row_data)
        else:
            grid.append(['r'] * width)
    return grid

def apply_patches(grid, patch_positions, pw, ph):
    new_grid = [row.copy() for row in grid]
    patch_num = 1
    for (sr, sc) in patch_positions:
        for i in range(sr, sr + ph):
            for j in range(sc, sc + pw):
                new_grid[i][j] = str(patch_num)
        patch_num += 1
    return new_grid

def grid_to_string(grid):
    return '\n'.join(''.join(row) for row in grid)

def patches_overlap(patch_positions, patch_width, patch_height):
    """Return True if any patch positions overlap."""
    occupied = set()
    for (sr, sc) in patch_positions:
        for i in range(sr, sr + patch_height):
            for j in range(sc, sc + patch_width):
                if (i, j) in occupied:
                    return True
                occupied.add((i, j))
    return False

def generate_layouts(gw, gh, npatches, pw, ph):
    """Yields one layout at a time as a string."""
    base_grid = generate_base_grid(gw, gh)

    # All possible top-left positions for a patch of size pw x ph
    max_r = gh - ph + 1
    max_c = gw - pw + 1
    all_positions = [
        (row, col)
        for row in range(max_r)
        for col in range(max_c)
    ]
    
    # All combinations of patch positions
    for patch_positions in itertools.combinations(all_positions, npatches):
        if patches_overlap(patch_positions, pw, ph):
            continue
        patched = apply_patches(base_grid, patch_positions, pw, ph)
        yield grid_to_string(patched)

##################
# Main script
##################
import sys
import requests
import os

def main():
    if len(sys.argv) < 7:
        print("Usage: python gen.py grid_width grid_height num_patches patch_width patch_height instructions_file")
        sys.exit(1)

    try:
        gw = int(sys.argv[1])
        gh = int(sys.argv[2])
        npatches = int(sys.argv[3])
        pw = int(sys.argv[4])
        ph = int(sys.argv[5])
    except ValueError:
        print("Grid dimensions and patch parameters must be integers.")
        sys.exit(1)

    instructions_file = sys.argv[6]
    if not os.path.exists(instructions_file):
        print(f"Instructions file does not exist: {instructions_file}")
        sys.exit(1)

    # Read the entire instructions file into memory
    with open(instructions_file, "rb") as f:
        instructions_data = f.read()  # read raw bytes

    url = "http://localhost:8080/process"

    # Generate and send layouts
    for i, layout_string in enumerate(
        generate_layouts(gw, gh, npatches, pw, ph), 
        start=1
    ):
        files = {
            "instructions": (instructions_file, instructions_data, "text/plain"),
            "layout": ("layout.txt", layout_string, "text/plain"),
        }

        print(f"\n--- Sending layout #{i} ---")

        # print layout string
        print(layout_string)
        print('\n')

        try:
            response = requests.post(url, files=files, timeout=10)
            response_data = response.json()
            print(f"Response: {response_data}")

            if "error" in response_data:
                print("Error encountered, possibly aborting or skipping further layouts.")
                continue

        except requests.exceptions.Timeout:
            print("Request timed out, skipping this layout or retry.")
        except Exception as e:
            print(f"An error occurred sending layout #{i}: {e}")

if __name__ == "__main__":
    main()