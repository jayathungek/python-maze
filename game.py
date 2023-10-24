from pyray import *

from maze import Maze


MAZE_H = 15
MAZE_W = 15
CELL_SZ = 50
PLAYER_SZ = 20

class Player:
    x: int
    y: int

    def __init__(self, x: int, y: int, size: float) -> None:
        self.x = x
        self.y = y
        self.size = size
    
    def draw(self, maze: Maze) -> None:
        cX = int((self.x + 0.5) * maze.cell_size)
        cY = int((self.y + 0.5) * maze.cell_size)
        draw_circle(cX, cY, self.size, RED)

    def can_move(self, dir: str, maze: Maze) -> bool:
        cell =  maze.cells[self.y][self.x]
        if dir == "north":
            return cell.north is not None and not (cell.wall_N and cell.north.wall_S)
        elif dir == "south":
            return cell.south is not None and not (cell.wall_S and cell.south.wall_N)
        elif dir == "east":
            return cell.east is not None and not (cell.wall_E and cell.east.wall_W)
        elif dir == "west":
            return cell.west is not None and not (cell.wall_W and cell.west.wall_E)

    def move(self, dir: str) -> None:
        if dir == "north":
            self.y -= 1
        elif dir == "south":
            self.y += 1
        elif dir == "east":
            self.x += 1
        elif dir == "west":
            self.x -= 1


if __name__=="__main__":
    maze = Maze(MAZE_W, MAZE_H, CELL_SZ)
    maze.generate()
    player = Player(0, 5, PLAYER_SZ)
    init_window(800, 800, "Maze")
    set_target_fps(60)
    pressed_key = get_key_pressed()


    while pressed_key != KeyboardKey.KEY_Q:
        begin_drawing()
        clear_background(RAYWHITE)
        maze.draw()
        player.draw(maze)
        if pressed_key == KeyboardKey.KEY_UP and player.can_move("north", maze):
            player.move("north")
        elif pressed_key == KeyboardKey.KEY_DOWN and player.can_move("south", maze):
            player.move("south")
        elif pressed_key == KeyboardKey.KEY_LEFT and player.can_move("west", maze):
            player.move("west")
        elif pressed_key == KeyboardKey.KEY_RIGHT and player.can_move("east", maze):
            player.move("east")
        pressed_key = get_key_pressed()
        end_drawing()
    close_window()
