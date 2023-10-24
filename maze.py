# We will be learing python step-by-step by writing a simple game - a maze generation algorithm
# This will allow you to grasp useful concepts like functions, object oriented programming, command line arguments
# and test driven development
# Features:
# 1. A different, random,  solvable maze every time
# 2. Load/save functionality to replay your favourite mazes
# 3. Customisable maze size WxH
# 4. Different maze algorithms

from time import time
import copy
import random
from typing import List
from dataclasses import dataclass
import pickle


from pyray import * 

import sys
sys.setrecursionlimit(11000)
RAYBLUE = Color(136, 205, 252, 255)
RAYRED = Color(252, 161, 136, 255)


@dataclass
class Cell:
    x: int
    y: int
    subregion: int = None
    debug = False

    wall_N: bool =  False 
    wall_E: bool =  False 
    wall_S: bool =  False 
    wall_W: bool =  False 

    north: 'Cell' = None
    east: 'Cell' = None
    south: 'Cell' = None
    west: 'Cell' = None


    def get_neighbours(self) -> List['Cell']:
        return [self.north, self.south, self.east, self.west]



def cell_eq(c1: Cell, c2: Cell) -> bool:
    return c1.x == c2.x and c1.y == c2.y


class Maze:
    width: int
    height: int
    cell_size: int
    cells: List[List[Cell]]

    min_start_size: int

    def __init__(self, width: int, height: int, cell_size:int=40, min_start_size=4) -> None:
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.cells = [
            [Cell(x, y) for x in range(width)] 
            for y in range(height)
        ]
        self.min_start_size = min_start_size
        self.connect_cells()

    def save(self, filename: str) -> None:
        with open(filename, "wb") as fh:
            pickle.dump(
                {
                    "maze_states": self.maze_states,
                    "width": self.width,
                    "height": self.height,
                    "cell_size": self.cell_size
                },
                fh)

    def load(self, filename: str) -> None:
        with open(filename, "rb") as fh:
            maze_attributes = pickle.load(fh)
            self.width =  maze_attributes['width']
            self.height =  maze_attributes['height']
            self.cell_size =  maze_attributes['cell_size']


    #TODO REMOVE
    def clone_cells(self):
        return [
            [self.cells[y][x].serialise() for x in range(self.width)]
            for y in range(self.height)
        ]

    #TODO REMOVE
    def pprint(self):
        for row in self.cells:
            r = ""
            for cell in row:
                if cell.subregion is not None:
                    r += f"{cell.subregion}"
                else:
                    r += " "
            print(r)

        

    
    def is_within_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def get_collapsed(self) -> List[Cell]:
        return sum(self.cells, [])

    def reset_subregions(self) -> None:
        for row in self.cells:
            for cell in row:
                cell.subregion = None
    
    def connect_cells(self) -> None:
        for row in self.cells:
            for cell in row:
                # Von Neumann neighbourhood
                northX = cell.x
                northY = cell.y - 1
                if self.is_within_bounds(northX, northY):
                    cell.north = self.cells[northY][northX]

                southX = cell.x
                southY = cell.y + 1
                if self.is_within_bounds(southX, southY):
                    cell.south = self.cells[southY][southX]

                eastX = cell.x + 1
                eastY = cell.y 
                if self.is_within_bounds(eastX, eastY):
                    cell.east = self.cells[eastY][eastX]

                westX = cell.x - 1
                westY = cell.y 
                if self.is_within_bounds(westX, westY):
                    cell.west = self.cells[westY][westX]


    def set_walls_at_boundary(self, area):
        # sets walls to true for cells that border subregion
        # removes one wall at random to satisfy the condition of maze solvability
        
        last_cell = None
        is_removed = False
        removal_chance = 1.0/(len(area)**0.5) # needs a bit of explanation
        for cell in area: 
            # start = time()
            # print(f"set_walls_at_boundary (inner for loop) - {time() - start}")
            for n in cell.get_neighbours():
                if (random.random() < removal_chance) and not is_removed:
                    # No-op and set flag
                    is_removed = True
                else:
                    if n in area and n is not None and n.subregion != cell.subregion:
                        dX = n.x - cell.x
                        dY = n.y - cell.y
                        if dY > 0:
                            # neighbour is to the south
                            self.cells[cell.y][cell.x].wall_S = True
                            last_cell = (cell, "south")
                        elif dY < 0:
                            # neighbour is to the north
                            self.cells[cell.y][cell.x].wall_N = True
                            last_cell = (cell, "north")
                        elif dX > 0:
                            # neighbour is to the east
                            self.cells[cell.y][cell.x].wall_E = True
                            last_cell = (cell, "east")
                        elif dX < 0:
                            # neighbour is to the west
                            self.cells[cell.y][cell.x].wall_W = True
                            last_cell = (cell, "west")

        if is_removed:
            cell, direction = last_cell
            if direction == "south":
                self.cells[cell.y][cell.x].wall_S = False
            elif direction == "north":
                self.cells[cell.y][cell.x].wall_N = False
            elif direction == "east":
                self.cells[cell.y][cell.x].wall_E = False
            elif direction == "west":
                self.cells[cell.y][cell.x].wall_W = False

    def _generate(self, area: List[Cell]) -> None:
        if len(area) < self.min_start_size: return
        frontier = random.sample(area, 2)
        frontier[0].subregion = 0
        frontier[1].subregion = 1

        while len(frontier) > 0:
            pop_idx  = random.randint(0, len(frontier) - 1)
            cur_cell = frontier.pop(pop_idx)
            for n in cur_cell.get_neighbours():
                if n in area: 
                    if n is not None and n.subregion is None:
                        n.subregion = cur_cell.subregion
                        frontier.append(n)
                        self.cells[n.y][n.x].subregion = n.subregion
                        if random.random() < 0.1:
                            yield self.cells

        self.set_walls_at_boundary(area)
        all_cells = self.get_collapsed()
        left_area = [cell for cell in all_cells if cell.subregion == 0]
        right_area = [cell for cell in all_cells if cell.subregion == 1]
        self.reset_subregions()
        yield from self._generate(left_area)
        yield from self._generate(right_area)

    def generate(self):
        subregion = self.get_collapsed()
        yield from self._generate(subregion)

    def draw(self) -> None:
        for row in self.cells:
            for cell in row:
                if cell.subregion == 0:
                    color = RAYRED
                elif cell.subregion == 1:
                    color = RAYBLUE
                else:
                    color = RAYWHITE 
                if cell.debug:
                    color = RAYWHITE

                draw_rectangle(
                    cell.x * self.cell_size, 
                    cell.y * self.cell_size, 
                    self.cell_size, 
                    self.cell_size, 
                    color
                )

                for pos in ["north", "south", "east", "west"]:
                    self.draw_wall(cell, pos)



    def draw_wall(self, cell: Cell, position: str) -> None:
        startX = None
        if position == "north": 
            if cell.wall_N and (cell.north is None or cell.north.wall_S):
                startX = cell.x * self.cell_size
                startY = cell.y * self.cell_size
                endX = startX + self.cell_size
                endY = startY

        elif position == "south":
            if cell.wall_S and (cell.south is None or cell.south.wall_N):
                startX = cell.x * self.cell_size
                startY = (cell.y * self.cell_size) + self.cell_size
                endX = startX + self.cell_size
                endY = startY

        elif position == "west":
            if cell.wall_W and (cell.west is None or cell.west.wall_E):
                startX = cell.x * self.cell_size
                startY = cell.y * self.cell_size 
                endX = startX
                endY = startY + self.cell_size

        elif position == "east":
            if cell.wall_E and (cell.east is None or cell.east.wall_W):
                startX = (cell.x * self.cell_size) + self.cell_size
                startY = cell.y * self.cell_size 
                endX = startX
                endY = startY + self.cell_size


        if startX is not None:
            draw_line(
                startX, startY, 
                endX, endY,
                BLACK 
            )

def draw_cells(maze: Maze, cells: List[Cell]) -> None:
    for row in cells:
        for cell in row:
            if cell.subregion == 0:
                color = RAYRED
            elif cell.subregion == 1:
                color = RAYBLUE
            else:
                color = RAYWHITE 
            if cell.debug:
                color = RAYWHITE

            draw_rectangle(
                cell.x * maze.cell_size, 
                cell.y * maze.cell_size, 
                maze.cell_size, 
                maze.cell_size, 
                color
            )

            for pos in ["north", "south", "east", "west"]:
                maze.draw_wall(cell, pos)


            
def create_maze_animation(filename: str, w: int, h: int, cell_sz: int, min_start_sz: int) -> None:
    maze = Maze(w, h, cell_sz, min_start_sz)
    maze.generate()
    maze.save(filename)


if __name__ == "__main__":
    MAZE_H = MAZE_W = 20
    CELL_SZ = 30
    MIN_START_SZ = 16
    BASE_FILENAME = f"maze_{MAZE_H}-r{MIN_START_SZ}"
    FILENAME = f"{BASE_FILENAME}.pkl"

    # create_maze_animation(FILENAME, MAZE_W, MAZE_H, CELL_SZ, MIN_START_SZ)
    # exit()
    maze = Maze(MAZE_W, MAZE_H, CELL_SZ)
    # maze.load(FILENAME)

    init_window(maze.width * maze.cell_size, maze.height * maze.cell_size, "Maze")
    set_target_fps(20)
    i = 0
    # for maze_next in maze.maze_states:
    for maze_next in maze.generate():
        begin_drawing()
        clear_background(RAYWHITE)
        draw_cells(maze, maze_next)
        end_drawing()
        take_screenshot(f"{BASE_FILENAME}/image{i}.png")
        i += 1
    close_window()