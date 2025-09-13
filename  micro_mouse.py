import tkinter as tk
from collections import deque
import random

# Initialize the main application window
root = tk.Tk()
root.title("Interactive Maze Solver")
root.geometry("1200x800")
root.config(bg="#121212")  # Set background color

# Global variables
size_x, size_y = tk.IntVar(value=15), tk.IntVar(value=15)
random_chance = tk.DoubleVar(value=30)
mode = "Obstacle"  # Current mode (Obstacle, Start, End)
grid, start, end = [], None, None  # Maze grid, start point, and end point
distances = {}  # Distance map for pathfinding
cell_size = 20  # Default cell size for drawing
animation_speed = 100  # Speed of simulation (in ms)
current_path = []  # Current path being simulated
mouse_position = None  # Current position of the "mouse"


def create_ui():
    # Heading section
    heading_frame = tk.Frame(root, bg="#c7c5c9")
    heading_frame.pack(fill="x")
    tk.Label(
        heading_frame,
        text="MICROMOUSE SIMULATOR",
        font=("Calibri", 37, "bold"),
        bg="#c7c5c9",
        fg="#121212").pack(pady=10)

    # Control panel
    ctrl = tk.Frame(root, bg="#d4d4d6", highlightthickness=3)
    ctrl.pack(side="left", anchor="nw", padx=(40, 5), pady=40)

    # Maze size controls
    tk.Label(
        ctrl,
        text="Select Maze Size",
        bg="#232323",
        fg="#ffffff",
        font=("Calibri", 20, "bold"),
        pady=6
    ).pack(side="top", fill="x")

    size_frame = tk.Frame(ctrl, bg="#d4d4d6")
    size_frame.pack(side="top", padx=20, pady=(25, 7))

    tk.Label(
        size_frame,
        text="Rows:",
        bg="#d4d4d6",
        fg="#111111",
        font=("Calibri", 24, "bold")
        ).pack(side="left", padx=(20, 5))
    tk.Entry(
        size_frame,
        textvariable=size_y,
        width=3,
        bg="#121212",
        fg="#ffffff",
        insertbackground="#ffffff",
        font=("Calibri", 17, "bold")
        ).pack(side="left", padx=(5, 25))

    tk.Label(
        size_frame,
        text="Cols:",
        bg="#d4d4d6",
        fg="#111111",
        font=("Calibri", 24, "bold")
    ).pack(side="left", padx=(10, 0))
    tk.Entry(
        size_frame,
        textvariable=size_x,
        width=3,
        bg="#121212",
        fg="#ffffff",
        insertbackground="#ffffff",
        font=("Calibri", 17, "bold")
    ).pack(side="left", padx=(5, 25))

    tk.Button(
        ctrl,
        text="Resize",
        command=init_grid,
        bg="#4354bf",
        fg="#ffffff",
        font=("Calibri", 18, "bold"),
        padx=10,
        relief=tk.RAISED,
        overrelief=tk.SUNKEN,
        pady=2).pack(side="top", pady=10)

    # Random maze generation
    tk.Label(
        ctrl,
        text="Obstacles Percentage",
        bg="#232323",
        fg="#ffffff",
        font=("Calibri", 20, "bold"),
        pady=7).pack(side="top", fill="x", pady=10)
    tk.Scale(
        ctrl,
        from_=0,
        to=100,
        orient="horizontal",
        variable=random_chance,
        sliderlength=35,
        font=("Calibri", 14, "bold"),
        troughcolor="#d7d9d9",
        length=230,
        bg="#232323",
        fg="#ffffff"
    ).pack(side="top", pady=10)

    tk.Button(
        ctrl,
        text="Generate Random",
        command=random_maze,
        bg="#79007d",
        fg="#ffffff",
        font=("Calibri", 18, "bold"),
        pady=4,
        relief=tk.RAISED,
        overrelief=tk.SUNKEN
    ).pack(side="top", pady=10)

    # Mode selection (Start and End points)
    tk.Label(
        ctrl,
        text="Select Points",
        bg="#232323",
        fg="#ffffff",
        font=("Calibri", 20, "bold"),
        pady=7
    ).pack(side="top", fill="x", pady=10)

    button1 = tk.Frame(ctrl, bg="#d4d4d6")
    button1.pack(side="top", pady=(10, 20))

    tk.Button(
        button1,
        text="End",
        command=lambda: set_mode("end"),
        bg="#a31010",
        fg="white",
        activebackground="#ffffff",
        activeforeground="#000000",
        font=("Calibri", 20, "bold"),
        padx=18,
        relief=tk.RAISED,
        overrelief=tk.SUNKEN
    ).pack(side="left", padx=(20, 35))
    tk.Button(
        button1,
        text="Start",
        command=lambda: set_mode("start"),
        bg="#30913d",
        fg="white",
        activebackground="#ffffff",
        activeforeground="#000000",
        font=("Calibri", 20, "bold"),
        padx=12,
        relief=tk.RAISED,
        overrelief=tk.SUNKEN
    ).pack(side="right", padx=20)

    # Simulation and reset buttons
    sim = tk.Frame(ctrl, bg="#232323")
    sim.pack(side="top", fill="x")
    tk.Button(
        sim,
        text="SIMULATE",
        command=solve,
        bg="#2196f3",
        fg="white",
        activebackground="#ffffff",
        activeforeground="#000000",
        font=("Calibri", 20, "bold"),
        relief=tk.RAISED,
        overrelief=tk.SUNKEN,
        padx=25,
        pady=6
    ).pack(side="top", pady=4)
    tk.Button(
        ctrl,
        text="RESET",
        command=init_grid,
        bg="#010e40",
        fg="#ffffff",
        font=("Calibri", 19, "bold"),
        pady=1,
        relief=tk.RAISED,
        overrelief=tk.SUNKEN,
        padx=10
    ).pack(side="top", fill="both", pady=(3, 0))

    # Maze canvas
    maze_frame = tk.Frame(
        root,
        borderwidth=5,
        highlightthickness=2,
        bg="#6e6e70")
    maze_frame.pack(
        side="right",
        fill="both",
        expand=True,
        padx=40,
        pady=(40, 40))

    mode_frame = tk.Frame(
        maze_frame,
        bg="#9e9e9e")
    mode_frame.pack(
        side="top",
        pady=(6, 2))

    global status, canvas
    status = tk.Label(
        mode_frame,
        text="Click to place obstacles, start, and end points",
        bg="#d4d4d6",
        fg="#121212", font=("Calibri", 24, "bold"), padx=4, pady=4)
    status.pack()
    canvas = tk.Canvas(
        maze_frame,
        bg="#d4d4d6",
        relief=tk.RAISED,
        highlightthickness=3)
    canvas.pack(
        fill="both",
        expand=True,
        padx=7,
        pady=(10, 7))
    canvas.bind("<Button-1>", click)
    canvas.bind("<Configure>", lambda e: draw())  # Redraw on resize


def set_mode(new_mode):
    """Sets the current mode (Obstacle, Start, End)."""
    global mode, current_path
    mode = new_mode
    current_path = []
    status.config(text=f"Mode: {mode.capitalize()}")


def init_grid():
    """Initializes or resets the maze grid."""
    global grid, start, end, distances, current_path, mode, mouse_position
    grid = [[0] * size_x.get() for _ in range(size_y.get())]
    start = end = None  # Reset start and end points
    distances = {}
    current_path = []
    mouse_position = None
    mode = "obstacle"  # Set default mode
    status.config(text="Mode: Obstacle")
    draw()


def random_maze():
    """Generates a random maze based on the obstacle percentage."""
    global grid, start, end, current_path, mouse_position
    chance = random_chance.get() / 100
    grid = [[1 if random.random() < chance else 0
            for _ in range(size_x.get())]
            for _ in range(size_y.get())]
    start = end = None
    current_path = []
    mouse_position = None
    draw()


def draw():
    """Draws the maze grid on the canvas."""
    global cell_size
    w, h = canvas.winfo_width(), canvas.winfo_height()
    cell_size = min(max(
                    4, min((w-20)//size_x.get(), (h-20)//size_y.get())), 40)
    canvas.delete("all")
    for y in range(len(grid)):
        for x in range(len(grid[0])):
            x1, y1 = x * cell_size + (w - len(grid[0])*cell_size)//2, \
                     y * cell_size + (h - len(grid)*cell_size)//2
            fill = "#232323" if grid[y][x] else "#ffffff"
            if (x, y) in current_path:
                fill = "#2196f3"
            if (x, y) == mouse_position:
                fill = "#ff9800"
            if (x, y) == start:
                fill = "#17bf08"
            elif (x, y) == end:
                fill = "#d41919"
            canvas.create_rectangle(x1, y1, x1+cell_size, y1+cell_size,
                                    fill=fill,
                                    outline="#616161"
                                    if cell_size > 5 else fill)
            if (x, y) in distances and fill != "#232323" and cell_size >= 12:
                canvas.create_text(x1 + cell_size/2, y1 + cell_size/2,
                                   text=str(distances[(x, y)]),
                                   fill="white"
                                   if fill == "#2196f3"
                                   else "#232323",
                                   font=("TkDefaultFont",
                                         min(cell_size-4, 12)))


def click(event):
    global grid, start, end, current_path
    w, h = canvas.winfo_width(), canvas.winfo_height()
    grid_w, grid_h = len(grid[0])*cell_size, len(grid)*cell_size
    x = (event.x - (w - grid_w)//2) // cell_size
    y = (event.y - (h - grid_h)//2) // cell_size
    if 0 <= x < len(grid[0]) and 0 <= y < len(grid):
        if mode == "start" and not grid[y][x]:
            start = (x, y)
            current_path = []
            calc_distances()  # Recalculate distances
            draw()  # Redraw the maze
        elif mode == "end" and not grid[y][x]:
            end = (x, y)
            current_path = []
            draw()  # Redraw the maze
        else:
            grid[y][x] = 1 - grid[y][x]  # Toggle obstacle state
            current_path = []
            draw()


def solve():
    """Solves the maze using the precomputed distances."""
    global current_path, mouse_position
    if not (start and end):
        status.config(text="Invalid path or missing start/end points")
        return
    if start not in distances:  # safer than distances.get(start, 1)
        status.config(text="No path found!")
        return

    path = [start]
    mouse_position = start
    try:
        while path[-1] != end:
            if not root.winfo_exists():
                break
            x, y = path[-1]
            next_pos = min(
                [(nx, ny) for nx, ny in [(x+1, y), (x-1, y),
                                         (x, y+1), (x, y-1)]
                 if (nx, ny) in distances],
                key=lambda p: distances[p]
            )
            path.append(next_pos)
            current_path = path[:]
            mouse_position = next_pos
            draw()
            root.update()
            root.after(animation_speed)
    except Exception as e:
        status.config(text=f"Error during solving: {str(e)}")
    finally:
        mouse_position = None
        draw()
        if root.winfo_exists():
            status.config(text=f"Path found! Length: {len(path)} steps")


def calc_distances():
    """Calculates distances from the end point to all other cells using BFS."""
    global distances
    if not end:
        return
    distances = {end: 0}
    queue = deque([end])
    while queue:
        x, y = queue.popleft()
        for nx, ny in [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]:
            if (0 <= nx < len(grid[0]) and 0 <= ny < len(grid)
                    and not grid[ny][nx] and (nx, ny) not in distances):
                distances[(nx, ny)] = distances[(x, y)] + 1
                queue.append((nx, ny))


# Initialize & run the application
create_ui()
init_grid()
root.mainloop()
