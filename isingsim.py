import pygame as pg
import numpy as np
from math import exp, sin, cos, atan2, pi, radians


class Population:
    # These variables do not often need to be adjusted. Ones that do are in init
    START_LOC = np.array((30, 0))  # Full grid offset
    COLOURS = ["black", "#8a0000", "#2596be"]  # Colours of cells
    COOLDOWN_TIMER = 500  # Manual flipping cooldown
    BITE_COOLDOWN = 1000  # How often herbivore can attack (random from 1x to 2x)
    J = 1  # Coupling constant
    THERMO_OFFSET = 20  # Thermometer distance from top and bottom
    THERMO_RANGE = (0, 5)  # Min an max temperatures

    def __init__(self, size=10, randomize=False, herbivores=10, HERBIVORE_SPEED=0.06, start_temp=3., GAP_SIZE=0, PUSH_FACTOR=0.01, TURN_FACTOR=10, MAX_ACTIVATION=50):
        """Initialization: first group of variables are chosen, second depends on first, third is not chosen"""
        self.GRID_SIZE = size  # Number of cells on each side of grid
        self.temp = start_temp  # 'Temperature' of the entire system (reactivity)
        self.NUM_OF_HERBIVORES = herbivores
        self.GAP_SIZE = GAP_SIZE
        self.HERBIVORE_SPEED = HERBIVORE_SPEED
        self.PUSH_FACTOR = PUSH_FACTOR  # Percent of the herbivore's velocity the active cells push the herbivore away
        self.TURN_FACTOR = TURN_FACTOR  # Max random turn in degrees
        self.MAX_ACTIVATION = MAX_ACTIVATION  # Number of ticks an active cell can receive before being forced to deactivate

        self.CELL_SIZE = 600//self.GRID_SIZE  # Side length of cell
        self.SCREEN_SIZE = self.GRID_SIZE * (self.CELL_SIZE + self.GAP_SIZE)  # Size of lattice
        self.MIX_START = randomize  # Randomized start or not
        self.GRID_VEC = pg.Vector2((self.CELL_SIZE + self.GAP_SIZE,)*2)

        self.herbivores = []
        for i in range(self.NUM_OF_HERBIVORES):
            # Generates the herbivores with random start position, intitial velocity, and attack cooldown
            self.herbivores.append(
                {"p": np.random.random(2) * ((self.SCREEN_SIZE,)*2) + self.START_LOC,  # position
                "v": pg.Vector2(*(np.random.random(2)*2-1)),  # velocity
                "t": self.BITE_COOLDOWN*(1 + np.random.random()),
                "state": 1  # Alive or dead
                })
            self.herbivores[i]["v"].scale_to_length(self.HERBIVORE_SPEED)
        self.init_grid()
        self.click_cooldown = 0
        self.info = None
    
    def set_thermo(self):
        """Sets the position of the thermostat based on current temp"""
        self.thermo_pos = [
            self.START_LOC[0]//2,
            self.THERMO_OFFSET + (self.temp/(self.THERMO_RANGE[1] - self.THERMO_RANGE[0])) * (self.SCREEN_SIZE - 2*self.THERMO_OFFSET)]
        self.thermo_display = text.render(str(round(self.temp, 1)), False, "white")
    
    def set_temp(self):
        """Sets the temperature based on the current thermostat pos"""
        self.temp = self.THERMO_RANGE[0] + self.THERMO_RANGE[1] * (self.thermo_pos[1] - self.THERMO_OFFSET)/(self.SCREEN_SIZE - 2 * self.THERMO_OFFSET)
        self.thermo_display = text.render(str(round(self.temp, 1)), False, "white")
    
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
                        self.CELL_SIZE),
                    "time_active": 0})
    
    def grid_coords(self, coords):
        """Converts from absolute coordinates to lattice coordinates"""
        return ((coords - self.START_LOC) // (self.CELL_SIZE + self.GAP_SIZE))[[1,0]]
    
    def grid_clamp(self, val):
        """Takes an (x,y) grid-coordinate input and clamps the values to be within the grid"""
        x = min(val[0], self.GRID_SIZE) if val[0] > 0 else 0
        y = min(val[1], self.GRID_SIZE) if val[1] > 0 else 0
        return (x, y)
    
    def screen_clamp(self, val):
        """Takes an (x,y) absolute-coordinate input and clamps the values to be within the grid"""
        x = min(val[0], self.START_LOC[0] + self.SCREEN_SIZE - 1) if val[0] > self.START_LOC[0] else self.START_LOC[0] + 1
        y = min(val[1], self.START_LOC[1] + self.SCREEN_SIZE - 1) if val[1] > self.START_LOC[1] else self.START_LOC[1] + 1
        return (x, y)

    def set(self, coords, val=0, convert_to_grid=False):
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
    
    def get_activation(self, coords, convert_to_grid=False):
        if convert_to_grid:
            coords = self.grid_coords(coords)
        return self.grid[int(coords[0])][int(coords[1])]["time_active"]
    
    def set_activation(self, coords, val, convert_to_grid=False):
        if convert_to_grid:
            coords = self.grid_coords(coords)
        self.grid[int(coords[0])][int(coords[1])]["time_active"] = val
    
    def tick(self, coords, convert_to_grid=False):
        """Gets the spin value for the cell at the given coordinates, converting if specified"""
        if convert_to_grid:
            coords = self.grid_coords(coords)
        self.set_activation(coords, (self.get_activation(coords) + 1) % self.MAX_ACTIVATION)
        if not self.get_activation(coords):
            self.set(coords, -1)
            self.set_activation(coords, 0)
    
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
            self.set(cell)
        else:
            is_edge = (cell[0] in (0, self.GRID_SIZE-1), cell[1] in (0, self.GRID_SIZE-1))
            # Random flip impossible if E=8J for middle, 6J for edge, 4J for corner (max difference)
            if dE < (8 - 2 * sum(is_edge)) * self.J and np.random.random() < exp(-(1/self.temp) * dE):
                self.set(cell)
        if self.get(cell) == 1:
            self.tick(cell)
        else:
            self.set_activation(cell, 0)
    
    def herbivory(self, time_step):
        """Carries out a single step in the herbivory process: change direction, move, attack"""
        for h in self.herbivores:
            if not h["state"]:
                continue

            h["v"].rotate_ip(np.random.random()*20 - 10)  # Random velocity rotation

            # Defense-active cells nudge velocity away (avoidance)
            surroundings = []
            for r in (-1, 0, 1):
                for c in (-1, 0, 1):  # Looks in 3x3 centred on herbivore
                    neighbour = h["p"] + self.GRID_VEC.elementwise()*(c, r)
                    if not (tuple(neighbour) == self.grid_clamp(neighbour) and self.get(neighbour, convert_to_grid=True) == -1):
                        # If neighbour is in grid and deactive, skip. Otherwise, nudge (active or border)
                        surroundings.append(h["v"].length() * self.PUSH_FACTOR * pg.Vector2(-c,-r))
            push = pg.Vector2()
            for vec in surroundings:
                push += vec  # Total push is sum of all neighbours, so [0,2] will be stronger than [1] and in the same direction
            h["v"] += push

            # Move according to new adjusted velocity
            step = np.array(h["v"]) * time_step  # Time step normalizes movement according to framerate
            h["p"] += step
            h["p"] = np.array(self.screen_clamp(h["p"]), dtype="float64")  # Out of bounds check

            h["v"].scale_to_length(self.HERBIVORE_SPEED)  # Reset velocity's magnitude

            # Perform attack based on cooldown
            if h["t"] > 0:
                h["t"] -= 1
            else:  # If bite cooldown is 0
                h["t"] = int(self.BITE_COOLDOWN * (1 + np.random.random()))  # Ranges from 1x to 2x base cooldown
                if self.get(h["p"], convert_to_grid=True) == 1:
                    h["v"].scale_to_length(0)
                    h["state"] = 0
                else:
                    self.set(h["p"], 1, convert_to_grid=True)

    def click(self, mouse_pos):
        """Adjusts thermostat or flips cell according to where user clicks"""
        if mouse_pos[0] < self.START_LOC[0]:  # User is clicking on thermostat
            if mouse_pos[1] > self.THERMO_OFFSET and mouse_pos[1] < self.SCREEN_SIZE - self.THERMO_OFFSET:
                self.thermo_pos[1] = mouse_pos[1]
                self.set_temp()
        elif not self.click_cooldown:  # User is clicking on lattice
            self.click_cooldown = self.COOLDOWN_TIMER
            self.set(mouse_pos, convert_to_grid=True)

    def right_click(self, mouse_pos):
        """Reveals extra information in DEBUG mode"""
        coords = self.grid_coords(mouse_pos)
        self.set_info(self.grid[coords[0]][coords[1]]["time_active"])
    
    def draw_grid(self):
        """Draws lattice of cells"""
        for i, row in enumerate(self.grid):  # Draw lattice cells
            for j, cell in enumerate(row):
                pg.draw.rect(screen, self.COLOURS[cell["spin"]], cell["rect"])
                if DEBUG:
                    pg.draw.rect(screen, (0, 255*cell["time_active"]/self.MAX_ACTIVATION, 0), pg.Rect(
                            self.START_LOC[0] + (self.CELL_SIZE + self.GAP_SIZE)*j,
                            self.START_LOC[1] + (self.CELL_SIZE + self.GAP_SIZE)*i,
                            max(1, self.CELL_SIZE/10),
                            max(1, self.CELL_SIZE/10)))
    
    def draw_options(self):
        """Draws thermostat, and other future options if added"""
        pg.draw.circle(screen, "green", self.thermo_pos, self.START_LOC[0]//3)
    
    def draw_herbivores(self):
        for h in self.herbivores:
            pg.draw.circle(screen, ("black", "white")[h["state"]], h["p"], max(self.CELL_SIZE/5, 1))
    
    def set_info(self, val):
        """Sets info text (used for debugging)"""
        self.info = text.render(str(val), False, "white")

def run(sim, debug_mode=False):
    global clock, running, screen, text, DEBUG
    DEBUG = debug_mode
    # Pygame initialization
    pg.init()
    pg.display.set_caption("Ising Simulation")
    clock = pg.time.Clock()
    running = True
    screen = pg.display.set_mode((sim.SCREEN_SIZE + sim.START_LOC[0], sim.SCREEN_SIZE + sim.START_LOC[1]))
    text = pg.font.SysFont("moderno20", sim.START_LOC[0])
    sim.set_thermo()  # This is not done in class initialization because it needs the pygame text object (and screen needs class info)

    # Game loop
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

        dt = clock.tick()  # Dynamic time interval for constant herbivore speeds

        sim.flip()  # Ising process
        sim.herbivory(dt)  # Move/attack process

        if sim.click_cooldown:
            sim.click_cooldown -= 1
        button_clicks = pg.mouse.get_pressed()
        if button_clicks[0]:
            sim.click(np.array(pg.mouse.get_pos()))
        if button_clicks[2]:
            sim.right_click(np.array(pg.mouse.get_pos()))

        # Clear screen (black), draw lattice -> options (thermostat) -> herbivores
        screen.fill("black")
        sim.draw_grid()
        sim.draw_options()
        sim.draw_herbivores()
        
        # Draw text display(s)
        screen.blit(sim.thermo_display, (0, 0))
        if DEBUG:
            if type(sim.info) == pg.surface.Surface:
                screen.blit(sim.info, sim.START_LOC)

        pg.display.flip()

run(Population(
    size=10,
    randomize=False,
    herbivores=10,
    HERBIVORE_SPEED=0.06,
    start_temp=3.,
    GAP_SIZE=0,
    PUSH_FACTOR=0.01,
    TURN_FACTOR=10,
    MAX_ACTIVATION=50),
    debug_mode=False
    )

pg.quit()
