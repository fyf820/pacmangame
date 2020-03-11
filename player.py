import pygame as pg
from settings import *
import time

Vector = pg.math.Vector2


class Player:
    def __init__(self, game, pos):
        self.game = game
        self.screen = self.game.screen
        self.grid_pos = Vector(pos[0], pos[1])
        self.pix_pos = self.get_pix_pos()
        self.direction = Vector(0, 0)
        self.stored_direction = None
        self.able_to_move = True
        self.current_score = 0
        self.lives = 3
        self.starting_pos = [pos.x, pos.y]
        self.open_portal1 = False
        self.open_portal2 = False
        self.open_portal_state = 1
        self.portal_direction1 = None
        self.portal_direction2 = None
        self.portal_pos1 = None
        self.portal_pos2 = None
        self.portal_grid_pos1 = None
        self.portal_grid_pos2 = None
        self.portal_number = None

        self.screen_rect = game.screen.get_rect()
        self.image = None
        self.walk = [pg.image.load("walk1.png"), pg.image.load("walk2.png"), pg.image.load("walk3.png"),
                     pg.image.load("walk4.png")]
        self.L_walk = [pg.transform.scale(self.walk[0], (self.game.wall_width // 2, self.game.wall_width // 2)),
                       pg.transform.scale(self.walk[1], (self.game.wall_width // 2, self.game.wall_width // 2)),
                       pg.transform.scale(self.walk[2], (self.game.wall_width // 2, self.game.wall_width // 2)),
                       pg.transform.scale(self.walk[3], (self.game.wall_width // 2, self.game.wall_width // 2))]
        self.U_walk = [pg.transform.rotate(self.L_walk[0], 90),
                       pg.transform.rotate(self.L_walk[1], 90),
                       pg.transform.rotate(self.L_walk[2], 90),
                       pg.transform.rotate(self.L_walk[3], 90)]
        self.R_walk = [pg.transform.rotate(self.U_walk[0], 90),
                       pg.transform.rotate(self.U_walk[1], 90),
                       pg.transform.rotate(self.U_walk[2], 90),
                       pg.transform.rotate(self.U_walk[3], 90)]
        self.D_walk = [pg.transform.rotate(self.R_walk[0], 90),
                       pg.transform.rotate(self.R_walk[1], 90),
                       pg.transform.rotate(self.R_walk[2], 90),
                       pg.transform.rotate(self.R_walk[3], 90)]

        self.move_time = self.now()
        self.move_state = 0

        self.portalimage = pg.image.load("portal.png")
        self.portalimage_V = pg.transform.scale(self.portalimage, (self.game.wall_width // 2, self.game.wall_height))
        self.portalimage_H = pg.transform.scale(self.portalimage, (self.game.wall_width, self.game.wall_height // 2))

        self.eatbgm = pg.mixer.Sound("eating.wav")

    def move(self, direction):
        self.stored_direction = direction

    def get_pix_pos(self):
        return Vector((self.grid_pos.x * self.game.wall_width) + BUFFER // 2 + self.game.wall_width // 2,
                      (self.grid_pos.y * self.game.wall_height) + BUFFER // 2 + self.game.wall_height // 2)

    def update(self):
        if self.on_portal():
            self.jump()
        else:
            if self.able_to_move:
                self.pix_pos += self.direction * 2
            if self.time_to_move():
                if self.stored_direction != None:
                    self.direction = self.stored_direction
                self.able_to_move = self.can_move()
        self.grid_pos.x = (self.pix_pos.x - BUFFER + self.game.wall_width // 2) // self.game.wall_width + 1
        self.grid_pos.y = (self.pix_pos.y - BUFFER + self.game.wall_height // 2) // self.game.wall_height + 1
        if self.on_coin():
            self.eatbgm.play()
            self.eat_coin()
        if self.on_power():
            self.eatbgm.play()
            self.eat_power()
        if self.on_fruit():
            self.eatbgm.play()
            self.eat_fruit()

    def draw(self):
        self.get_image()
        self.screen.blit(self.image, ((self.pix_pos.x - 3), (self.pix_pos.y - 3)))
        # pg.draw.rect(self.game.screen,(0,0,0),(self.grid_pos.x*self.game.wall_width+BUFFER//2,
        #               self.grid_pos.y * self.game.wall_height+BUFFER//2,self.game.wall_width,self.game.wall_height),1)
        if self.open_portal1:
            if self.portal_direction1 == Vector(1, 0) or self.portal_direction1 == Vector(-1,
                                                                                          0) or self.portal_direction1 == Vector(
                0, 0):
                self.screen.blit(self.portalimage_V, (self.portal_pos1[0] - 3, self.portal_pos1[1] - 7))
            if self.portal_direction1 == Vector(0, 1) or self.portal_direction1 == Vector(0,
                                                                                          -1) or self.portal_direction1 == Vector(
                0, 0):
                self.screen.blit(self.portalimage_H, (self.portal_pos1[0] - 7, self.portal_pos1[1] - 3))
        if self.open_portal2:
            if self.portal_direction2 == Vector(1, 0) or self.portal_direction2 == Vector(-1,
                                                                                          0) or self.portal_direction2 == Vector(
                0, 0):
                self.screen.blit(self.portalimage_V, (self.portal_pos2[0] - 3, self.portal_pos2[1] - 7))
            if self.portal_direction2 == Vector(0, 1) or self.portal_direction2 == Vector(0,
                                                                                          -1) or self.portal_direction2 == Vector(
                0, 0):
                self.screen.blit(self.portalimage_H, (self.portal_pos2[0] - 7, self.portal_pos2[1] - 3))
        for x in range(self.lives):
            pg.draw.circle(self.game.screen, (255, 255, 0), (30 + 20 * x, GAMEHEIGHT - 15), 7)

    def on_coin(self):
        if self.grid_pos in self.game.coins:
            if int(self.pix_pos.x + BUFFER // 2) % self.game.wall_width == 0:
                if self.direction == Vector(1, 0) or self.direction == Vector(-1, 0):
                    return True
            if int(self.pix_pos.y + BUFFER // 2) % self.game.wall_height == 0:
                if self.direction == Vector(0, 1) or self.direction == Vector(0, -1):
                    return True
        return False

    def eat_coin(self):
        self.game.coins.remove(self.grid_pos)
        self.current_score += 10

    def on_power(self):
        if self.grid_pos in self.game.powers:
            if int(self.pix_pos.x + BUFFER // 2) % self.game.wall_width == 0:
                if self.direction == Vector(1, 0) or self.direction == Vector(-1, 0):
                    return True
            if int(self.pix_pos.y + BUFFER // 2) % self.game.wall_height == 0:
                if self.direction == Vector(0, 1) or self.direction == Vector(0, -1):
                    return True
        return False

    def eat_power(self):
        self.game.powers.remove(self.grid_pos)
        self.current_score += 50
        self.game.run_mode = True
        self.game.music_switch = 1
        for ghosts in self.game.ghost:
            ghosts.mode = "runaway"
            ghosts.last_switch = ghosts.now()

    def time_to_move(self):
        if int(self.pix_pos.x + BUFFER // 2) % self.game.wall_width == 0:
            if self.direction == Vector(1, 0) or self.direction == Vector(-1, 0) or self.direction == Vector(0, 0):
                return True
        if int(self.pix_pos.y + BUFFER // 2) % self.game.wall_height == 0:
            if self.direction == Vector(0, 1) or self.direction == Vector(0, -1) or self.direction == Vector(0, 0):
                return True

    def can_move(self):
        if Vector(self.grid_pos + self.direction) == self.portal_grid_pos1 or Vector(
                self.grid_pos + self.direction) == self.portal_grid_pos2:
            if self.open_portal1 and self.open_portal2:
                return True
        if Vector(self.grid_pos) == self.portal_grid_pos1 or Vector(self.grid_pos) == self.portal_grid_pos2:
            return True
        for wall in self.game.walls:
            if Vector(self.grid_pos + self.direction) == wall:
                return False
        return True

    def portal(self):
        if self.open_portal_state == 2:
            self.open_portal()
            self.open_portal2 = True
            self.open_portal_state = 1
        else:
            self.open_portal()
            self.open_portal1 = True
            self.open_portal_state = 2

    def open_portal(self):
        if self.direction == Vector(1, 0) or self.direction == Vector(0, 0):
            x_dir = 1
            y_dir = 0
            if self.open_portal_state == 1:
                self.portal_direction1 = Vector(-1, 0)
            else:
                self.portal_direction2 = Vector(-1, 0)
            next_pos = Vector(self.grid_pos.x + x_dir, self.grid_pos.y + y_dir)
            while True:
                if next_pos in self.game.walls:
                    break
                next_pos = Vector(next_pos[0] + x_dir, next_pos[1] + y_dir)
            portal_pos = Vector((next_pos[0] * self.game.wall_width) + BUFFER // 2 + self.game.wall_width // 2,
                                (next_pos[1] * self.game.wall_height) + BUFFER // 2 + self.game.wall_height // 2)

        elif self.direction == Vector(-1, 0):
            x_dir = -1
            y_dir = 0
            if self.open_portal_state == 1:
                self.portal_direction1 = Vector(1, 0)
            else:
                self.portal_direction2 = Vector(1, 0)
            next_pos = Vector(self.grid_pos.x + x_dir, self.grid_pos.y + y_dir)
            while True:
                if next_pos in self.game.walls:
                    break
                next_pos = Vector(next_pos[0] + x_dir, next_pos[1] + y_dir)
            portal_pos = Vector((next_pos[0] * self.game.wall_width) + BUFFER // 2 + self.game.wall_width // 2,
                                (next_pos[1] * self.game.wall_height) + BUFFER // 2 + self.game.wall_height // 2)

        elif self.direction == Vector(0, 1):
            x_dir = 0
            y_dir = 1
            if self.open_portal_state == 1:
                self.portal_direction1 = Vector(0, -1)
            else:
                self.portal_direction2 = Vector(0, -1)
            next_pos = Vector(self.grid_pos.x + x_dir, self.grid_pos.y + y_dir)
            while True:
                if next_pos in self.game.walls:
                    break
                next_pos = Vector(next_pos[0] + x_dir, next_pos[1] + y_dir)
            portal_pos = Vector((next_pos[0] * self.game.wall_width) + BUFFER // 2 + self.game.wall_width // 2,
                                (next_pos[1] * self.game.wall_height) + BUFFER // 2 + self.game.wall_height // 2)

        elif self.direction == Vector(0, -1):
            x_dir = 0
            y_dir = -1
            if self.open_portal_state == 1:
                self.portal_direction1 = Vector(0, 1)
            else:
                self.portal_direction2 = Vector(0, 1)
            next_pos = Vector(self.grid_pos.x + x_dir, self.grid_pos.y + y_dir)
            while True:
                if next_pos in self.game.walls:
                    break
                next_pos = Vector(next_pos[0] + x_dir, next_pos[1] + y_dir)
            portal_pos = Vector((next_pos[0] * self.game.wall_width) + BUFFER // 2 + self.game.wall_width // 2,
                                (next_pos[1] * self.game.wall_height) + BUFFER // 2 + self.game.wall_height // 2)

        if self.open_portal_state == 1:
            self.portal_pos1 = portal_pos
            self.portal_grid_pos1 = next_pos
        else:
            self.portal_pos2 = portal_pos
            self.portal_grid_pos2 = next_pos

    def on_portal(self):
        if self.grid_pos == self.portal_grid_pos1:
            if int(self.pix_pos.x + BUFFER // 2) % self.game.wall_width == 0:
                if self.direction == Vector(1, 0) or self.direction == Vector(-1, 0):
                    self.portal_number = 1
                    return True
            if int(self.pix_pos.y + BUFFER // 2) % self.game.wall_height == 0:
                if self.direction == Vector(0, 1) or self.direction == Vector(0, -1):
                    self.portal_number = 1
                    return True
        if self.grid_pos == self.portal_grid_pos2:
            if int(self.pix_pos.x + BUFFER // 2) % self.game.wall_width == 0:
                if self.direction == Vector(1, 0) or self.direction == Vector(-1, 0):
                    self.portal_number = 2
                    return True
            if int(self.pix_pos.y + BUFFER // 2) % self.game.wall_height == 0:
                if self.direction == Vector(0, 1) or self.direction == Vector(0, -1):
                    self.portal_number = 2
                    return True
        return False

    def jump(self):
        if self.portal_number == 1:
            self.direction = self.portal_direction2
            self.pix_pos = self.portal_pos2 + self.direction * 2

        else:
            self.direction = self.portal_direction1
            self.pix_pos = self.portal_pos1 + self.direction * 2

    def close_portal(self):
        self.open_portal1 = False
        self.open_portal2 = False
        self.open_portal_state = 1
        self.portal_direction1 = None
        self.portal_direction2 = None
        self.portal_pos1 = None
        self.portal_pos2 = None
        self.portal_grid_pos1 = None
        self.portal_grid_pos2 = None
        self.portal_number = None

    def on_fruit(self):
        if self.grid_pos == self.game.fruit:
            if int(self.pix_pos.x + BUFFER // 2) % self.game.wall_width == 0:
                if self.direction == Vector(1, 0) or self.direction == Vector(-1, 0):
                    return True
            if int(self.pix_pos.y + BUFFER // 2) % self.game.wall_height == 0:
                if self.direction == Vector(0, 1) or self.direction == Vector(0, -1):
                    return True
        return False

    def eat_fruit(self):
        self.game.fruit_appear = False
        self.game.last_switch = self.game.now()
        self.current_score += 100

    def get_image(self):
        if self.move_state == 0:
            if self.direction == Vector(-1, 0):
                self.image = self.L_walk[0]
            elif self.direction == Vector(1, 0) or self.direction == Vector(0, 0):
                self.image = self.R_walk[0]
            elif self.direction == Vector(0, 1):
                self.image = self.U_walk[0]
            elif self.direction == Vector(0, -1):
                self.image = self.D_walk[0]
            self.change_move_state()
        elif self.move_state == 1 or self.move_state == 5:
            if self.direction == Vector(-1, 0):
                self.image = self.L_walk[1]
            elif self.direction == Vector(1, 0) or self.direction == Vector(0, 0):
                self.image = self.R_walk[1]
            elif self.direction == Vector(0, 1):
                self.image = self.U_walk[1]
            elif self.direction == Vector(0, -1):
                self.image = self.D_walk[1]
            self.change_move_state()
        elif self.move_state == 2 or self.move_state == 4:
            if self.direction == Vector(-1, 0):
                self.image = self.L_walk[2]
            elif self.direction == Vector(1, 0) or self.direction == Vector(0, 0):
                self.image = self.R_walk[2]
            elif self.direction == Vector(0, 1):
                self.image = self.U_walk[2]
            elif self.direction == Vector(0, -1):
                self.image = self.D_walk[2]
            self.change_move_state()
        elif self.move_state == 3:
            if self.direction == Vector(-1, 0):
                self.image = self.L_walk[3]
            elif self.direction == Vector(1, 0) or self.direction == Vector(0, 0):
                self.image = self.R_walk[3]
            elif self.direction == Vector(0, 1):
                self.image = self.U_walk[3]
            elif self.direction == Vector(0, -1):
                self.image = self.D_walk[3]
            self.change_move_state()

    def change_move_state(self):
        if self.now() - self.move_time > ANIME_INTERVAL:
            if self.move_state == 5:
                self.move_state = 0
            else:
                self.move_state += 1
            self.move_time = self.now()

    def now(self):
        return pg.time.get_ticks()
