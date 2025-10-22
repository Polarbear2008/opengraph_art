#!/usr/bin/env python3
import os, subprocess
from datetime import date, datetime, timedelta

# --------- TUNE THESE ----------
DARK_COMMITS = 8   # how many commits per "dark" square (try 8–12 for darkest)
MID_COMMITS  = 4   # if you later add mid-tone squares
MESSAGE      = "graph art"
# --------------------------------

# 5x7 pixel font for letters we need (X = filled, . = empty)
FONT = {
    "P": [
        "XXXX.",
        "X...X",
        "X...X",
        "XXXX.",
        "X....",
        "X....",
        "X....",
    ],
    "O": [
        ".XXX.",
        "X...X",
        "X...X",
        "X...X",
        "X...X",
        "X...X",
        ".XXX.",
    ],
    "L": [
        "X....",
        "X....",
        "X....",
        "X....",
        "X....",
        "X....",
        "XXXXX",
    ],
    "A": [
        ".XXX.",
        "X...X",
        "X...X",
        "XXXXX",
        "X...X",
        "X...X",
        "X...X",
    ],
    "R": [
        "XXXX.",
        "X...X",
        "X...X",
        "XXXX.",
        "X.X..",
        "X..X.",
        "X...X",
    ],
    " ": [
        ".....",
        ".....",
        ".....",
        ".....",
        ".....",
        ".....",
        ".....",
    ],
}

TEXT = "P O L A R"   # add spaces to spread letters a bit

# Build a 7 x N grid for the whole word (N <= 52 columns)
cols = []
for ch in TEXT:
    if ch == " ":
        # 2-column spacer
        cols += list(zip(*FONT[" "]))[:2]
        continue
    letter = FONT[ch]
    # append 5 columns of the letter
    cols += list(zip(*letter))
    # 1 column spacing between letters
    cols += list(zip(*FONT[" "]))[:1]

# Turn tuples into strings of length 7 (top->bottom = row 0..6)
grid_cols = ["".join(c) for c in cols]
width = len(grid_cols)
if width > 52:
    raise SystemExit(f"Pattern is {width} weeks wide (>52). Remove some spaces.")

# Compute start Sunday for the leftmost column (52 weeks wide)
today = date.today()
# last Sunday (GitHub columns end on last Saturday; starting at previous Sunday works well)
days_since_sunday = (today.weekday() + 1) % 7  # Monday=0 => Sunday=6
last_sunday = today - timedelta(days=days_since_sunday)
start_sunday = last_sunday - timedelta(weeks=51)  # 52 columns total

# We want our word right-aligned inside the 52 weeks (so it ends near this week)
left_pad_weeks = 52 - width
def day_at(col, row):
    """Return the actual date for a cell (row 0=Sunday .. row 6=Saturday)."""
    col_idx = left_pad_weeks + col
    return start_sunday + timedelta(weeks=col_idx, days=row)

# Ensure repo has a file to change
ARTFILE = "art.txt"
if not os.path.exists(ARTFILE):
    open(ARTFILE, "w").write("polar art\n")

def commit_on(d: date, n: int):
    if n <= 0: return
    for k in range(n):
        with open(ARTFILE, "a") as f:
            f.write(f"{d.isoformat()} #{k+1}\n")
        subprocess.run(["git", "add", ARTFILE], check=True)
        # noon local time; you can change timezone if you want
        tstamp = f"{d.isoformat()} 12:00:00"
        env = os.environ.copy()
        env["GIT_AUTHOR_DATE"] = tstamp
        env["GIT_COMMITTER_DATE"] = tstamp
        subprocess.run(["git", "commit", "-m", f"{MESSAGE} {d.isoformat()} #{k+1}"], check=True, env=env)

# Walk the grid and commit where needed
for c, col in enumerate(grid_cols):
    # col is a 7-char string, index 0=top (Sunday) -> 6=bottom (Saturday)
    for r, ch in enumerate(col):
        if ch == "X":
            commit_on(day_at(c, r), DARK_COMMITS)

print("Done. Now push: git push origin main")
