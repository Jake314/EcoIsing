import pygame as pg
import numpy as np
from math import exp, sin, cos, pi


# Gets the total energy across the entire grid
def get_sum(grid):
    total = 0
    for i, row in enumerate(grid):
        for j, cell in enumerate(row):
            if i + 1 < len(grid):  # Vertical coupling
                total += (-1, 1)[cell["spin"]] * (-1, 1)[grid[i + 1][j]["spin"]]
            if j + 1 < len(grid[0]):  # Horizontal coupling
                total += (-1, 1)[cell["spin"]] * (-1, 1)[row[j + 1]["spin"]]
    return total


# Gets the energy at a specific cell with regard to its neighbours
def local_energy(grid, row, col):
    spin = (-1, 1)[int(grid[row][col]["spin"])]

    neighbours = []
    for i in [row - 1, row + 1]:
        if i >= 0 and i < grid_size:
            neighbours.append((-1, 1)[int(grid[i][col]["spin"])])
    for j in [col - 1, col + 1]:
        if j >= 0 and j < grid_size:
            neighbours.append((-1, 1)[int(grid[row][j]["spin"])])
    
    current = -J * sum([spin * n for n in neighbours])
    new = -J * sum([-spin * n for n in neighbours])

    return new - current

display_local = False
display_total = False
start_loc = (50, 0)  # Full grid offset
grid_size = 20  # Number of cells on each side of grid
cell_size = 600//grid_size  # Side length of cell
gap_size = 0  # Space between cells
MIX_START = False  # Randomized start or not
COOLDOWN_TIMER = 60  # Clicking cooldown
BITE_COOLDOWN = 1000
J = 1  # Coupling constant

pg.init()
text = pg.font.SysFont("Comic Sans MS", 30)
screen_size = grid_size * (cell_size + gap_size)

thermo_offset = 20
thermo_range = (0, 5)
temp = 1.
thermo_pos = [25, thermo_offset + (temp/(thermo_range[1] - thermo_range[0])) * (screen_size - 2 * thermo_offset)]

herbivores = [
    {"p": np.array((screen_size/2 + start_loc[0], screen_size/2 + start_loc[1])), "v": 1, "a": 0, "t": BITE_COOLDOWN}
    ]

screen = pg.display.set_mode((screen_size + start_loc[0], screen_size + start_loc[1]))
pg.display.set_caption("Ising Simulation")
clock = pg.time.Clock()
running = True

cols = ["#2596be", "#8a0000"]
df = []
for i in range(grid_size):
    df.append([])
    for j in range(grid_size):
        df[i].append({
            "spin": bool(np.random.randint(2)) if MIX_START else False,
            "rect": pg.Rect(
                start_loc[0] + (cell_size + gap_size)*i,
                start_loc[1] + (cell_size + gap_size)*j,
                cell_size,
                cell_size
            )})

cooldown = 0

while running:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False

    dt = clock.tick()/10

    if cooldown:
        cooldown -= 1

    thermo_display = text.render(str(round(temp, 1)), False, "white")

    select = pg.mouse.get_pos()
    mouse_display = text.render(str(select), False, (0, 0, 0))
    if display_total:
        energy_display = text.render(str(get_sum(df)), False, (0, 0, 0))

    randx = np.random.randint(grid_size)
    randy = np.random.randint(grid_size)

    energy_diff = local_energy(df, randy, randx)
    if display_local:
        local_display = text.render(str(local_energy(df, select[0], select[1])), False, (0, 0, 0))
    if energy_diff < 0:
        df[randy][randx]["spin"] = not df[randy][randx]["spin"]
    else:
        is_edge = (randx in (0, grid_size-1), randy in (0, grid_size-1))
        # Random flip impossible if E=8J for middle, 6J for edge, 4J for corner (max difference)
        if energy_diff < (8 - 2 * sum(is_edge)) * J and np.random.random() < exp(-(1/temp) * energy_diff):
            df[randy][randx]["spin"] = not df[randy][randx]["spin"]

    if pg.mouse.get_pressed()[0]:
        if select[0] < start_loc[0]:
            if select[1] > thermo_offset and select[1] < screen_size - thermo_offset:
                thermo_pos[1] = select[1]
                temp = thermo_range[0] + thermo_range[1] * (thermo_pos[1] - thermo_offset)/(screen_size - 2 * thermo_offset)
        elif not cooldown:
            grid_select = (np.array(select) - start_loc) // (cell_size + gap_size)
            cooldown = COOLDOWN_TIMER
            df[grid_select[0]][grid_select[1]]["spin"] = not df[grid_select[0]][grid_select[1]]["spin"]

    screen.fill("black")
    for i, row in enumerate(df):  # Draw lattice cells
        for j, cell in enumerate(row):
            pg.draw.rect(screen, cols[int(cell["spin"])], cell["rect"])
            pg.draw.circle(screen, "white", thermo_pos, 10)
    for h in herbivores:  # Draw herbivores
        h["a"] += np.random.random() * pi/8 - pi/16  # Random angle adjustment
        step = np.array((cos(h["a"]), sin(h["a"]))) * h["v"] * dt  # Step size
        h["p"] += step
        if h["p"][0] < start_loc[0] or h["p"][0] > screen_size + start_loc[0]:
            h["a"] = pi - h["a"] + int(h["a"] > 180) * 2*pi
        if h["p"][1] < start_loc[1] or h["p"][1] > screen_size + start_loc[1]:
            h["a"] = 2*pi - h["a"]
        pg.draw.circle(screen, "white", h["p"], cell_size/4)  # Draw individual

        if h["t"]:
            h["t"] -= 1
        else:
            h["t"] = int(BITE_COOLDOWN * (1 + np.random.random()))
            grid_pos = (h["p"] - start_loc) // (cell_size + gap_size)
            df[int(grid_pos[0])][int(grid_pos[1])]["spin"] = True
    
    screen.blit(thermo_display, (0, 0))
    if display_total:
        screen.blit(energy_display, (50, 0))
    if display_local:
        screen.blit(local_display, (screen_size - 50, 0))

    pg.display.flip()

pg.quit()
