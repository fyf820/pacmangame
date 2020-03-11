import pygame as pg
import random
from settings import *
import time

Vector = pg.math.Vector2


class Ghost:
    def __init__(self, game, pos, number):
        self.game = game
        self.screen = self.game.screen
        self.grid_pos = pos
        self.starting_pos = [pos.x, pos.y]
        self.pix_pos = self.get_pix_pos()
        self.number = number
        self.direction = Vector(0, 0)
        self.target = None
        self.mode = "normal"
        self.speed = self.set_speed()
        self.last_switch = self.now()
        self.deadghost = 1

        self.blinkyimage = [pg.image.load("blinky1.png"), pg.image.load("blinky2.png"), pg.image.load("blinky3.png"),
                            pg.image.load("blinky4.png"), pg.image.load("blinky5.png"), pg.image.load("blinky6.png"),
                            pg.image.load("blinky7.png"), pg.image.load("blinky8.png")]
        self.clydeimage = [pg.image.load("clyde1.png"), pg.image.load("clyde2.png"), pg.image.load("clyde3.png"),
                           pg.image.load("clyde4.png"), pg.image.load("clyde5.png"), pg.image.load("clyde6.png"),
                           pg.image.load("clyde7.png"), pg.image.load("clyde8.png")]
        self.pinkyimage = [pg.image.load("pinky1.png"), pg.image.load("pinky2.png"), pg.image.load("pinky3.png"),
                           pg.image.load("pinky4.png"), pg.image.load("pinky5.png"), pg.image.load("pinky6.png"),
                           pg.image.load("pinky7.png"), pg.image.load("pinky8.png")]
        self.inkyimage = [pg.image.load("inky1.png"), pg.image.load("inky2.png"), pg.image.load("inky3.png"),
                          pg.image.load("inky4.png"), pg.image.load("inky5.png"), pg.image.load("inky6.png"),
                          pg.image.load("inky7.png"), pg.image.load("inky8.png")]
        self.eyeimage = [pg.image.load("eyes1.png"), pg.image.load("eyes2.png"), pg.image.load("eyes3.png"),
                         pg.image.load("eyes4.png")]
        self.ghostimage = [pg.image.load("ghost1.png"), pg.image.load("ghost2.png"), pg.image.load("ghost3.png"),
                           pg.image.load("ghost4.png")]

        self.image = None
        self.move_state = 0
        self.move_time = self.now()
        self.run_state = 0
        self.run_time = self.now()

    def update(self):
        self.speed = self.set_speed()
        self.set_mode()
        self.target = self.set_target()
        if self.target != self.grid_pos:
            self.pix_pos += self.direction * self.speed
            if self.time_to_move():
                self.move()

        self.grid_pos[0] = (self.pix_pos[0] - BUFFER + self.game.wall_width // 2) // self.game.wall_width + 1
        self.grid_pos[1] = (self.pix_pos[1] - BUFFER + self.game.wall_height // 2) // self.game.wall_height + 1

    def draw(self):
        self.set_image()
        self.image = pg.transform.scale(self.image, (self.game.wall_width // 2, self.game.wall_width // 2))
        self.screen.blit(self.image, ((self.pix_pos.x - 3), (self.pix_pos.y - 3)))

    def get_pix_pos(self):
        return Vector((self.grid_pos.x * self.game.wall_width) + BUFFER // 2 + self.game.wall_width // 2,
                      (self.grid_pos.y * self.game.wall_height) + BUFFER // 2 + self.game.wall_height // 2)

    def set_image(self):
        if self.mode == "runaway":
            if self.run_state == 0:
                self.image = self.ghostimage[0]
                self.change_run_state()
            elif self.run_state == 1:
                self.image = self.ghostimage[1]
                self.change_run_state()
            elif self.run_state == 2:
                self.image = self.ghostimage[2]
                self.change_run_state()
            elif self.run_state == 3:
                self.image = self.ghostimage[3]
                self.change_run_state()
        elif self.mode == "back":
            if self.direction == Vector(-1, 0):
                self.image = self.eyeimage[1]
            elif self.direction == Vector(1, 0):
                self.image = self.eyeimage[2]
            elif self.direction == Vector(0, -1):
                self.image = self.eyeimage[0]
            elif self.direction == Vector(0, 1):
                self.image = self.eyeimage[3]
        else:
            if self.move_state == 0:
                if self.direction == Vector(-1, 0):
                    if self.number == 0:
                        self.image = self.blinkyimage[2]
                    elif self.number == 1:
                        self.image = self.clydeimage[2]
                    elif self.number == 2:
                        self.image = self.pinkyimage[2]
                    elif self.number == 3:
                        self.image = self.inkyimage[2]
                elif self.direction == Vector(1, 0) or self.direction == Vector(0, 0):
                    if self.number == 0:
                        self.image = self.blinkyimage[4]
                    elif self.number == 1:
                        self.image = self.clydeimage[4]
                    elif self.number == 2:
                        self.image = self.pinkyimage[4]
                    elif self.number == 3:
                        self.image = self.inkyimage[4]
                elif self.direction == Vector(0, -1):
                    if self.number == 0:
                        self.image = self.blinkyimage[0]
                    elif self.number == 1:
                        self.image = self.clydeimage[0]
                    elif self.number == 2:
                        self.image = self.pinkyimage[0]
                    elif self.number == 3:
                        self.image = self.inkyimage[0]
                elif self.direction == Vector(0, 1):
                    if self.number == 0:
                        self.image = self.blinkyimage[6]
                    elif self.number == 1:
                        self.image = self.clydeimage[6]
                    elif self.number == 2:
                        self.image = self.pinkyimage[6]
                    elif self.number == 3:
                        self.image = self.inkyimage[6]
                self.change_move_state()
            elif self.move_state == 1:
                if self.direction == Vector(-1, 0):
                    if self.number == 0:
                        self.image = self.blinkyimage[2]
                    elif self.number == 1:
                        self.image = self.clydeimage[2]
                    elif self.number == 2:
                        self.image = self.pinkyimage[2]
                    elif self.number == 3:
                        self.image = self.inkyimage[2]
                elif self.direction == Vector(1, 0) or self.direction == Vector(0, 0):
                    if self.number == 0:
                        self.image = self.blinkyimage[4]
                    elif self.number == 1:
                        self.image = self.clydeimage[4]
                    elif self.number == 2:
                        self.image = self.pinkyimage[4]
                    elif self.number == 3:
                        self.image = self.inkyimage[4]
                elif self.direction == Vector(0, -1):
                    if self.number == 0:
                        self.image = self.blinkyimage[1]
                    elif self.number == 1:
                        self.image = self.clydeimage[1]
                    elif self.number == 2:
                        self.image = self.pinkyimage[1]
                    elif self.number == 3:
                        self.image = self.inkyimage[1]
                elif self.direction == Vector(0, 1):
                    if self.number == 0:
                        self.image = self.blinkyimage[7]
                    elif self.number == 1:
                        self.image = self.clydeimage[7]
                    elif self.number == 2:
                        self.image = self.pinkyimage[7]
                    elif self.number == 3:
                        self.image = self.inkyimage[7]
                self.change_move_state()

    def change_move_state(self):
        if self.now() - self.move_time > ANIME_INTERVAL:
            if self.move_state == 1:
                self.move_state = 0
            else:
                self.move_state += 1
            self.move_time = self.now()

    def change_run_state(self):
        if self.now() - self.run_time > ANIME_INTERVAL:
            if self.now() - self.last_switch > RUN_BLUE:
                if self.run_state == 3:
                    self.run_state = 0
                else:
                    self.run_state += 1
            else:
                if self.run_state == 1:
                    self.run_state = 0
                else:
                    self.run_state += 1
            self.run_time = self.now()

    def time_to_move(self):
        if int(self.pix_pos.x + BUFFER // 2) % self.game.wall_width == 0:
            if self.direction == Vector(1, 0) or self.direction == Vector(-1, 0) or self.direction == Vector(0, 0):
                return True
        if int(self.pix_pos.y + BUFFER // 2) % self.game.wall_height == 0:
            if self.direction == Vector(0, 1) or self.direction == Vector(0, -1) or self.direction == Vector(0, 0):
                return True
        return False

    def move(self):
        if self.mode == "normal":
            if self.number == 0:
                self.direction = self.get_random_direction()
            if self.number == 1:
                self.direction = self.get_clock_direction()
            if self.number == 2:
                self.direction = self.get_counterclock_direction()
            if self.number == 3:
                self.direction = self.get_clock_direction()
        elif self.mode == "back" and self.grid_pos == self.starting_pos:
            if self.number == 0:
                self.direction = self.get_random_direction()
            if self.number == 1:
                self.direction = self.get_clock_direction()
            if self.number == 2:
                self.direction = self.get_counterclock_direction()
            if self.number == 3:
                self.direction = self.get_clock_direction()
        else:
            self.direction = self.get_path_direction(self.target)

    def get_clock_direction(self):
        next_pos = self.grid_pos + self.direction
        next_direction = self.direction
        while True:
            if next_pos not in self.game.walls:
                break
            else:
                if self.direction == Vector(1, 0):
                    x_dir, y_dir = 0, 1
                    next_pos = Vector(self.grid_pos.x + x_dir, self.grid_pos.y + y_dir)
                    if next_pos in self.game.walls:
                        next_direction = self.get_random_direction()
                    else:
                        next_direction = Vector(x_dir, y_dir)
                    break
                elif self.direction == Vector(-1, 0):
                    x_dir, y_dir = 0, -1
                    next_pos = Vector(self.grid_pos.x + x_dir, self.grid_pos.y + y_dir)
                    if next_pos in self.game.walls:
                        next_direction = self.get_random_direction()
                    else:
                        next_direction = Vector(x_dir, y_dir)
                    break
                elif self.direction == Vector(0, 1):
                    x_dir, y_dir = 1, 0
                    next_pos = Vector(self.grid_pos.x + x_dir, self.grid_pos.y + y_dir)
                    if next_pos in self.game.walls:
                        next_direction = self.get_random_direction()
                    else:
                        next_direction = Vector(x_dir, y_dir)
                    break
                elif self.direction == Vector(0, -1):
                    x_dir, y_dir = -1, 0
                    next_pos = Vector(self.grid_pos.x + x_dir, self.grid_pos.y + y_dir)
                    if next_pos in self.game.walls:
                        next_direction = self.get_random_direction()
                    else:
                        next_direction = Vector(x_dir, y_dir)
                    break
        if self.direction == Vector(0, 0):
            next_direction = self.get_random_direction()
        return next_direction

    def get_counterclock_direction(self):
        next_pos = self.grid_pos + self.direction
        next_direction = self.direction
        while True:
            if next_pos not in self.game.walls:
                break
            else:
                if self.direction == Vector(1, 0):
                    x_dir, y_dir = 0, -1
                    next_pos = Vector(self.grid_pos.x + x_dir, self.grid_pos.y + y_dir)
                    if next_pos in self.game.walls:
                        next_direction = self.get_random_direction()
                    else:
                        next_direction = Vector(x_dir, y_dir)
                    break
                elif self.direction == Vector(-1, 0):
                    x_dir, y_dir = 0, 1
                    next_pos = Vector(self.grid_pos.x + x_dir, self.grid_pos.y + y_dir)
                    if next_pos in self.game.walls:
                        next_direction = self.get_random_direction()
                    else:
                        next_direction = Vector(x_dir, y_dir)
                    break
                elif self.direction == Vector(0, 1):
                    x_dir, y_dir = -1, 0
                    next_pos = Vector(self.grid_pos.x + x_dir, self.grid_pos.y + y_dir)
                    if next_pos in self.game.walls:
                        next_direction = self.get_random_direction()
                    else:
                        next_direction = Vector(x_dir, y_dir)
                    break
                elif self.direction == Vector(0, -1):
                    x_dir, y_dir = 1, 0
                    next_pos = Vector(self.grid_pos.x + x_dir, self.grid_pos.y + y_dir)
                    if next_pos in self.game.walls:
                        next_direction = self.get_random_direction()
                    else:
                        next_direction = Vector(x_dir, y_dir)
                    break
        if self.direction == Vector(0, 0):
            next_direction = self.get_random_direction()
        return next_direction

    def get_random_direction(self):
        while True:
            number = random.randint(-2, 1)
            if number == -2:
                x_dir, y_dir = 1, 0
            elif number == -1:
                x_dir, y_dir = 0, 1
            elif number == 0:
                x_dir, y_dir = -1, 0
            else:
                x_dir, y_dir = 0, -1
            next_pos = Vector(self.grid_pos.x + x_dir, self.grid_pos.y + y_dir)
            if next_pos not in self.game.walls:
                break
        return Vector(x_dir, y_dir)

    def get_path_direction(self, target):
        next_cell = self.find_next_in_path(target)
        xdir = next_cell[0] - self.grid_pos[0]
        ydir = next_cell[1] - self.grid_pos[1]
        return Vector(xdir, ydir)

    def find_next_in_path(self, target):
        path = self.BFS([int(self.grid_pos.x), int(self.grid_pos.y)],
                        [int(target[0]), int(target[1])])
        return path[1]

    def BFS(self, start, target):
        grid = [[0 for x in range(28)] for x in range(30)]
        for wall in self.game.walls:
            if wall.x < 28 and wall.y < 30:
                grid[int(wall.y)][int(wall.x)] = 1
        queue = [start]
        path = []
        visited = []
        while queue:
            current = queue[0]
            queue.remove(queue[0])
            visited.append(current)
            if current == target:
                break
            else:
                neighbours = [[0, -1], [1, 0], [0, 1], [-1, 0]]
                for neighbour in neighbours:
                    if neighbour[0] + current[0] >= 0 and neighbour[0] + current[0] < len(grid[0]):
                        if neighbour[1] + current[1] >= 0 and neighbour[1] + current[1] < len(grid):
                            next_wall = [neighbour[0] + current[0], neighbour[1] + current[1]]
                            if next_wall not in visited:
                                if grid[next_wall[1]][next_wall[0]] != 1:
                                    queue.append(next_wall)
                                    path.append({"Current": current, "Next": next_wall})
        shortest = [target]
        while target != start:
            for step in path:
                if step["Next"] == target:
                    target = step["Current"]
                    shortest.insert(0, step["Current"])
        return shortest

    def set_target(self):
        if self.mode == "chase":
            return self.game.player.grid_pos
        elif self.mode == "runaway":
            if self.game.player.grid_pos[0] > COLS // 2 and self.game.player.grid_pos[1] > ROWS // 2:
                return Vector(1, 1)
            if self.game.player.grid_pos[0] > COLS // 2 and self.game.player.grid_pos[1] < ROWS // 2:
                return Vector(1, ROWS - 2)
            if self.game.player.grid_pos[0] < COLS // 2 and self.game.player.grid_pos[1] > ROWS // 2:
                return Vector(COLS - 2, 1)
            else:
                return Vector(COLS - 2, ROWS - 2)
        elif self.mode == "shopping":
            if self.number == 0:
                return Vector(COLS - 2, ROWS - 1)
            if self.number == 1:
                return Vector(COLS - 2, 1)
            if self.number == 2:
                return Vector(1, ROWS - 1)
            else:
                return Vector(1, 1)
        elif self.mode == "back":
            return self.starting_pos

    def set_speed(self):
        speed = 1
        return speed

    def set_mode(self):
        if self.mode == "normal":
            if self.now() - self.last_switch > NORMAL:
                self.mode = "chase"
                self.last_switch = self.now()
        elif self.mode == "chase":
            if self.now() - self.last_switch > CHASE:
                self.mode = "shopping"
                self.last_switch = self.now()
        elif self.mode == "shopping":
            if self.now() - self.last_switch > SHOPPING:
                self.mode = "normal"
                self.last_switch = self.now()
        elif self.mode == "runaway":
            if self.now() - self.last_switch > RUN:
                self.mode = "normal"
                self.run_state = 0
                self.run_state_time = self.now()
                self.last_switch = self.now()
                self.game.run_mode = False
                self.game.music_switch = 1
        elif self.mode == "back":
            if self.now() - self.last_switch > RUN:
                self.mode = "normal"
                self.run_state = 0
                self.run_state_time = self.now()
                self.last_switch = self.now()
                self.game.run_mode = False
                self.game.music_switch = 1

    def N_mode(self):
        self.mode = "normal"

    def C_mode(self):
        self.mode = "chase"

    def S_mode(self):
        self.mode = "shopping"

    def now(self):
        return pg.time.get_ticks()
