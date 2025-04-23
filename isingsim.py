import pygame as pg
import numpy as np
from math import exp, sin, cos, atan2, pi, degrees


class Population:
    START_LOC = np.array((50, 0))  # Full grid offset
    COLOURS = ["black", "#8a0000", "#2596be"]  # Colours of cells
    GAP_SIZE = 0  # Space between cells
    COOLDOWN_TIMER = 500  # Manual flipping cooldown
    BITE_COOLDOWN = 1000  # How often herbivore can attack
    J = 1  # Coupling constant
    THERMO_OFFSET = 20
    THERMO_RANGE = (0, 5)
    NUM_OF_HERBIVORES = 1

    def __init__(self, size: int, randomize: bool, start_temp=3.):
        """Initialization: first group of variables are chosen, second depends on first, third is not chosen"""
        self.GRID_SIZE = size  # Number of cells on each side of grid
        self.temp = start_temp  # 'Temperature' of the entire system

        self.CELL_SIZE = 600//self.GRID_SIZE  # Side length of cell
        self.SCREEN_SIZE = self.GRID_SIZE * (self.CELL_SIZE + self.GAP_SIZE)  # Size of lattice
        self.MIX_START = randomize  # Randomized start or not

        self.herbivores = []
        for i in range(self.NUM_OF_HERBIVORES):
            self.herbivores.append(
                {"p": self.START_LOC + np.random.random(2) * ((self.SCREEN_SIZE,)*2),  # position
                "v": .06,  # speed
                "a": 0,  # angle
                "t": self.BITE_COOLDOWN*(1 + np.random.random())}
            )
        self.set_thermo()
        self.init_grid()
        self.cooldown = 0
        self.info = None
    
    def set_thermo(self):
        """Sets the position of the thermostat based on current temp"""
        self.thermo_pos = [
            self.START_LOC[0]//2,
            self.THERMO_OFFSET + (self.temp/(self.THERMO_RANGE[1] - self.THERMO_RANGE[0])) * (self.SCREEN_SIZE - 2*self.THERMO_OFFSET)]
    
    def set_temp(self):
        """Sets the temperature based on the current thermostat pos"""
        self.temp = self.THERMO_RANGE[0] + self.THERMO_RANGE[1] * (self.thermo_pos[1] - self.THERMO_OFFSET)/(self.SCREEN_SIZE - 2 * self.THERMO_OFFSET)
    
    def get_total(self):
        """Gets total energy across the entire lattice"""
        total = 0
        for i, row in enumerate(self.grid):
            for j, cell in enumerate(row):
                if i + 1 < self.grid_size:  # Vertical coupling
                    total += (-1, 1)[cell["spin"]] * (-1, 1)[self.grid[i + 1][j]["spin"]]
                if j + 1 < self.grid_size:  # Horizontal coupling
                    total += (-1, 1)[cell["spin"]] * (-1, 1)[row[j + 1]["spin"]]
        return total

    def init_grid(self):
        """Builds the starting lattice"""
        self.grid = []
        for i in range(self.GRID_SIZE):
            self.grid.append([])
            for j in range(self.GRID_SIZE):
                self.grid[i].append({
                    "spin": (-1, 1)[bool(np.random.randint(2))] if self.MIX_START else -1,
                    "rect": pg.Rect(
                        self.START_LOC[0] + (self.CELL_SIZE + self.GAP_SIZE)*j,
                        self.START_LOC[1] + (self.CELL_SIZE + self.GAP_SIZE)*i,
                        self.CELL_SIZE,
                        self.CELL_SIZE
                    )})
    
    def grid_coords(self, coords):
        """Converts from absolute coordinates to lattice coordinates"""
        return ((coords - self.START_LOC) // (self.CELL_SIZE + self.GAP_SIZE))[[1,0]]

    def set(self, coords, val=0, convert_to_grid=True):
        """Sets the value of a cell, converting coordinates. Alternates value by default"""
        if convert_to_grid:
            coords = self.grid_coords(coords)
        if val:
            self.grid[int(coords[0])][int(coords[1])]["spin"] = val
        else:
            self.grid[int(coords[0])][int(coords[1])]["spin"] *= -1
    
    def get(self, coords, convert_to_grid=False):
        """Gets the spin value for the cell at the given coordinates, converting if specified"""
        if convert_to_grid:
            coords = self.grid_coords(coords)
        return self.grid[int(coords[0])][int(coords[1])]["spin"]
    
    def potential(self, coords):
        """Calculates the energy difference of a cell if its spin were reversed"""
        spin = self.get(coords)

        neighbours = []
        for i in [coords[0] - 1, coords[0] + 1]:
            if i >= 0 and i < self.GRID_SIZE:
                neighbours.append(self.get((i, coords[1])))
        for j in [coords[1] - 1, coords[1] + 1]:
            if j >= 0 and j < self.GRID_SIZE:
                neighbours.append(self.get((coords[0], j)))
        
        current = -self.J * sum([spin * n for n in neighbours])
        new = -self.J * sum([-spin * n for n in neighbours])

        return new - current
    
    def flip(self):
        """Pick a random cell, do the energy calculation and flip accordingly"""
        cell = np.random.randint(0, self.GRID_SIZE, 2)
        dE = self.potential(cell)
        if dE < 0:
            self.set(cell, convert_to_grid=False)
        else:
            is_edge = (cell[0] in (0, self.GRID_SIZE-1), cell[1] in (0, self.GRID_SIZE-1))
            # Random flip impossible if E=8J for middle, 6J for edge, 4J for corner (max difference)
            if dE < (8 - 2 * sum(is_edge)) * self.J and np.random.random() < exp(-(1/self.temp) * dE):
                self.set(cell, convert_to_grid=False)
    
    def herbivory(self, time_step):
        for h in self.herbivores:
            h["a"] += np.random.random() * pi/8 - pi/16  # Random angle adjustment
            h["a"] %= 360
            step = np.array((cos(h["a"]), sin(h["a"]))) * h["v"] * time_step  # Step size
            h["p"] += step
            # Check if herbivore has moved out of bounds
            if h["p"][0] < self.START_LOC[0] or h["p"][0] > self.SCREEN_SIZE + self.START_LOC[0]:
                h["p"] -= step
                h["a"] = pi - h["a"] + int(h["a"] > 180) * 2*pi
            if h["p"][1] < self.START_LOC[1] or h["p"][1] > self.SCREEN_SIZE + self.START_LOC[1]:
                h["p"] -= step
                h["a"] = 2*pi - h["a"]
            
            angles = [i*pi/4 for i in range(8)]
            # angles = [45*i for i in range(8)]
            angles = np.array(angles)[[7, 6, 5, 0, 0, 4, 1, 2, 3]]
            cell = self.grid_coords(h["p"])
            surroundings = []
            for r in (-1, 0, 1):
                for c in (-1, 0, 1):
                    if cell[0] + r in range(self.GRID_SIZE) and cell[1] + c in range(self.GRID_SIZE) \
                        and not (r == 0 and c == 0) and self.get((cell[0]+r, cell[1]+c)) == 1:
                        surroundings.append(angles[3*(r+1) + (c+1)])
            A = atan2(sum([sin(a) for a in surroundings]), sum([cos(a) for a in surroundings]))
            if A < 0:
                A += 2*pi
            self.set_info(round(degrees(A),2))

            if h["t"] > 0:
                h["t"] -= 1
            else:  # If bite cooldown is 0
                h["t"] = int(self.BITE_COOLDOWN * (1 + np.random.random()))  # Ranges from 1x to 2x base cooldown
                self.set(h["p"], 1)

    def click(self, mouse_pos):
        if mouse_pos[0] < self.START_LOC[0]:  # User is clicking on thermostat
            if mouse_pos[1] > self.THERMO_OFFSET and mouse_pos[1] < self.SCREEN_SIZE - self.THERMO_OFFSET:
                self.thermo_pos[1] = mouse_pos[1]
                self.set_temp()
        elif not self.cooldown:  # User is clicking on lattice
            self.cooldown = self.COOLDOWN_TIMER
            self.set(mouse_pos)
    
    def draw_grid(self):
        """Draws lattice of cells"""
        for i, row in enumerate(self.grid):  # Draw lattice cells
            for j, cell in enumerate(row):
                pg.draw.rect(screen, self.COLOURS[cell["spin"]], cell["rect"])
    
    def draw_options(self):
        """Draws thermostat, and other future options if added"""
        pg.draw.circle(screen, "white", self.thermo_pos, 10)
    
    def draw_herbivores(self):
        for h in self.herbivores:
            pg.draw.circle(screen, "white", h["p"], self.CELL_SIZE/4)
    
    def set_info(self, val):
        self.info = text.render(str(val), False, "white")

sim = Population(size=10, randomize=False, start_temp=3)
DEBUG = True

# Pygame initialization
pg.init()
pg.display.set_caption("Ising Simulation")
text = pg.font.SysFont("moderno20", 30)
clock = pg.time.Clock()
running = True
screen = pg.display.set_mode((sim.SCREEN_SIZE + sim.START_LOC[0], sim.SCREEN_SIZE + sim.START_LOC[1]))

# Game loop
while running:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False

    dt = clock.tick()  # Dynamic time interval for constant herbivore speeds

    sim.flip()

    if sim.cooldown:
        sim.cooldown -= 1
    if pg.mouse.get_pressed()[0]:
        sim.click(np.array(pg.mouse.get_pos()))

    screen.fill("black")
    sim.draw_grid()
    sim.draw_options()
    sim.herbivory(dt)
    sim.draw_herbivores()
    
    # Draw text display(s)
    thermo_display = text.render(str(round(sim.temp, 1)), False, "white")
    screen.blit(thermo_display, (0, 0))
    if DEBUG:
        screen.blit(sim.info, sim.START_LOC)

    pg.display.flip()

pg.quit()
