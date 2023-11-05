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
from typing import List, Tuple, Literal
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


def get_collapsed(cells: List[List[Cell]]) -> List[Cell]:
    return sum(cells, [])


def set_boundary_wall(partition1: List[List[Cell]], partition2: List[List[Cell]], vertical: bool):
    if vertical:
        for row in partition1:
            last_cell = row[-1]
            last_cell.wall_E = True

        for row in partition2:
            first_cell = row[0]
            first_cell.wall_W = True
        
        empty_cell_row = random.choice(range(len(partition1)))
        empty_cell_p1 = partition1[empty_cell_row][-1]
        empty_cell_p2 = partition2[empty_cell_row][0]
        empty_cell_p1.wall_E = False
        empty_cell_p2.wall_W = False
    else:
        last_row = partition1[0]
        for cell in last_row:
            cell.wall_S = True

        first_row = partition2[-1]
        for cell in first_row:
            cell.wall_N = True
        
        empty_cell_idx = random.choice(range(len(partition1[0])))
        empty_cell_p1 = last_row[empty_cell_idx]
        empty_cell_p2 = first_row[empty_cell_idx]
        empty_cell_p1.wall_S = False
        empty_cell_p2.wall_N = False


def set_subregions(subregion: List[List[Cell]], value: Literal[0, 1]) -> None:
    for row in subregion:
        for cell in row:
            cell.subregion = value


class Maze:
    width: int
    height: int
    cell_size: int
    cells: List[List[Cell]]

    min_room_size: int
    vertical_seek: bool = False

    def __init__(self, width: int, height: int, cell_size:int=40, min_room_size=4) -> None:
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.cells = [
            [Cell(x, y) for x in range(width)] 
            for y in range(height)
        ]
        self.min_room_size = min_room_size

    def bisect(self, cells: List[List[Cell]]) -> Tuple[List[List[Cell]]]:
        width = len(cells[0])
        height = len(cells)

        if width >= height:
            midpoint = width // 2
            selected_left = [
                row[:midpoint] for row in cells
            ]
            selected_right = [
                row[midpoint:] for row in cells
            ]
        else:
            midpoint = height // 2
            selected_left = [
                row for row in cells[:midpoint]
            ]
            selected_right = [
                row for row in cells[midpoint:]
            ]
        return selected_left, selected_right

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

        


    def reset_subregions(self) -> None:
        for row in self.cells:
            for cell in row:
                cell.subregion = None



    def _generate(self, area: List[List[Cell]], depth) -> None:
        self.vertical_seek = not self.vertical_seek
        if len(get_collapsed(area)) > self.min_room_size and depth > 0:
            first_area, second_area = self.bisect(area)
            set_boundary_wall(first_area, second_area, vertical=self.vertical_seek)
            set_subregions(first_area, 0)
            set_subregions(second_area, 1)
            yield self.cells
            self.reset_subregions()
            yield from self._generate(first_area, depth - 1)
            yield from self._generate(second_area, depth - 1)
        else:
            yield self.cells

    def generate(self):
        yield from self._generate(self.cells, 300)

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

def draw_cells(maze: Maze, cells: List[List[Cell]]) -> None:
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
    MAZE_H = MAZE_W = 40
    CELL_SZ = 30
    MIN_START_SZ = 4
    BASE_FILENAME = f"maze_{MAZE_H}-r{MIN_START_SZ}"
    FILENAME = f"{BASE_FILENAME}.pkl"

    # create_maze_animation(FILENAME, MAZE_W, MAZE_H, CELL_SZ, MIN_START_SZ)
    # exit()
    maze = Maze(MAZE_W, MAZE_H, CELL_SZ)
    # maze.load(FILENAME)

    init_window(maze.width * maze.cell_size, maze.height * maze.cell_size, "Maze")
    set_target_fps(20)
    for maze_next in maze.generate():
        begin_drawing()
        clear_background(RAYWHITE)
        draw_cells(maze, maze_next)
        end_drawing()
    take_screenshot(f"{BASE_FILENAME}.png")
    close_window()