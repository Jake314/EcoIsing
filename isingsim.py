import pygame as pg
import numpy as np


def get_sum(grid):
    total = 0
    for i, row in enumerate(grid):
        for j, cell in enumerate(row):
            if i + 1 < len(grid):  # Vertical coupling
                total += (-1, 1)[cell["spin"]] * (-1, 1)[grid[i + 1][j]["spin"]]
            if j + 1 < len(grid[0]):  # Horizontal coupling
                total += (-1, 1)[cell["spin"]] * (-1, 1)[row[j + 1]["spin"]]
    return total

start_loc = 0
grid_size = 20
cell_size = 20
gap_size = 2
MIX_START = False
COOLDOWN_TIMER = 20

pg.init()
text = pg.font.SysFont("Comic Sans MS", 30)
screen_size = grid_size * (cell_size + gap_size)

screen = pg.display.set_mode((screen_size, screen_size))
pg.display.set_caption("Ising Simulation")
clock = pg.time.Clock()
running = True

cols = ["blue", "red"]
df = []
for i in range(grid_size):
    df.append([])
    for j in range(grid_size):
        df[i].append({
            "spin": bool(np.random.randint(2)) if MIX_START else False,
            "rect": pg.Rect(
                start_loc + (cell_size + gap_size)*i,
                start_loc + (cell_size + gap_size)*j,
                cell_size,
                cell_size
            )})

cooldown = 0

while running:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False

    dt = clock.tick(60)/1000
    if cooldown:
        cooldown -= 1

    select = (np.array(pg.mouse.get_pos()) - start_loc) // (cell_size + gap_size)
    mouse_display = text.render(str(select), False, (0, 0, 0))
    energy_display = text.render(str(get_sum(df)), False, (0, 0, 0))

    screen.fill("black")
    for i, row in enumerate(df):
        for j, cell in enumerate(row):
            pg.draw.rect(screen, cols[int(cell["spin"])], cell["rect"])
    
    if pg.mouse.get_pressed()[0] and not cooldown:
        cooldown = COOLDOWN_TIMER
        df[select[0]][select[1]]["spin"] = not df[select[0]][select[1]]["spin"]
    
    screen.blit(energy_display, (0, 0))

    pg.display.flip()

pg.quit()
