import pygame as pg
import sys
import copy
from settings import *
from player import *
from ghost import *
import time

Vector = pg.math.Vector2

class Game:

    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((GAMEWIDTH, GAMEHEIGHT))
        self.clock = pg.time.Clock()
        pg.display.set_caption('Pacman')
        self.bg_color = (0, 0, 0)
        self.running = True
        self.state = 'intro'
        self.wall_width = MAZEWIDTH //COLS
        self.wall_height = MAZEHEIGHT//ROWS
        self.walls = []
        self.coins = []
        self.powers = []
        self.portal = []
        self.ghost = []
        self.G_pos = []
        self.fruit = None
        self.S_pos = None
        self.load()
        self.last_switch = self.now()
        self.fruit_appear = False
        self.ghostimage = [pg.image.load("blinky3.png"),pg.image.load("blinky4.png"),pg.image.load("clyde3.png"),
                           pg.image.load("clyde4.png"),pg.image.load("pinky3.png"),pg.image.load("pinky4.png"),
                           pg.image.load("inky3.png"),pg.image.load("inky4.png")]
        self.pacmanimage = [pg.image.load("walk1.png"),pg.image.load("walk2.png"),pg.image.load("walk3.png"),
                            pg.image.load("walk4.png")]
        self.last_intro = self.now()
        self.intro_state = 0
        self.anime_time = self.now()
        self.anime_state = 0
        self.anime_pix = [GAMEWIDTH,GAMEWIDTH,GAMEWIDTH,GAMEWIDTH,GAMEWIDTH]
        self.move_time = self.now()
        self.move_state = 0
        self.ghost_move_state = 0
        self.ghost_move_time = self.now()
        self.high_score = 0

        self.player = Player(self, Vector(self.S_pos))
        self.make_ghost()

        self.fruitimage = pg.image.load("fruit.png")
        self.fruitimage = pg.transform.scale(self.fruitimage, (self.wall_width // 2, self.wall_width // 2))

        self.bgm = "BGM.mp3"
        self.powerBGM = "Runaway.mp3"
        pg.mixer.music.load(self.bgm)
        self.music_switch = 1
        self.run_mode = False
        self.geating = pg.mixer.Sound("eatghost.wav")
        self.die_music = pg.mixer.Sound("die.wav")
        self.if_highscore = False

    def run(self):
        while self.running:
            if self.state == 'intro':
                self.intro_events()
                self.intro_update()
                self.intro_draw()
            elif self.state == 'playing':
                self.playing_events()
                self.playing_update()
                self.playing_draw()
            elif self.state == 'game over':
                self.over_events()
                self.over_update()
                self.over_draw()
            else:
                self.running = False
            self.clock.tick(FPS)
        pg.quit()
        sys.exit()

    #functions

    def draw_text(self,words,screen,pos,size,color,font_name,centered=False):
        font = pg.font.SysFont(font_name,size)
        text = font.render(words,False,color)
        text_size = text.get_size()
        if centered:
            pos[0] = pos[0] - text_size[0]//2
        screen.blit(text,pos)

    def load(self):
        self.background = pg.image.load('maze.png')
        self.background = pg.transform.scale(self.background, (MAZEWIDTH, MAZEHEIGHT))
        with open('walls.txt','r') as file:
            for yidx, line in enumerate(file):
                for xidx, char in enumerate(line):
                    if char == "1":
                        self.walls.append(Vector(xidx, yidx))
                    elif char == "C":
                        self.coins.append(Vector(xidx, yidx))
                    elif char == "P":
                        self.powers.append(Vector(xidx, yidx))
                    elif char == "F":
                        self.fruit = Vector(xidx, yidx)
                    elif char == "S":
                        self.S_pos = Vector(xidx, yidx)
                    elif char in ["2", "3", "4", "5"]:
                        self.G_pos.append([xidx,yidx])
                    elif char == "B":
                        pg.draw.rect(self.background, (0,0,0), (xidx*self.wall_width,
                                    yidx*self.wall_height,self.wall_width,self.wall_height))

    def make_ghost(self):
        for idx, pos in enumerate(self.G_pos):
            self.ghost.append(Ghost(self,Vector(pos),idx))

    def remove_life(self):
        self.player.lives -= 1
        self.die_music.play()
        if self.player.lives == 0:
            self.state = "game over"
        elif len(self.powers) == 0 and len(self.coins) == 0:
            self.state = "game over"
        else:
            self.player.grid_pos = Vector(self.player.starting_pos)
            self.player.pix_pos = self.player.get_pix_pos()
            self.player.direction *= 0
            self.player.close_portal()
            for ghosts in self.ghost:
                ghosts.grid_pos = Vector(ghosts.starting_pos)
                ghosts.pix_pos = ghosts.get_pix_pos()
                ghosts.direction *= 0

    def reset(self):
        self.player.lives = 3
        self.player.current_score = 0
        self.player.grid_pos = Vector(self.player.starting_pos)
        self.player.pix_pos = self.player.get_pix_pos()
        self.player.direction *= 0
        for ghosts in self.ghost:
            ghosts.grid_pos = Vector(ghosts.starting_pos)
            ghosts.pix_pos = ghosts.get_pix_pos()
            ghosts.direction *= 0

        self.coins = []

        with open('walls.txt','r') as file:
            for yidx, line in enumerate(file):
                for xidx, char in enumerate(line):
                    if char == "C":
                        self.coins.append(Vector(xidx, yidx))
                    elif char == "P":
                        self.powers.append(Vector(xidx, yidx))
        self.state = "playing"

    def now(self):
        return pg.time.get_ticks()

    def draw_fruit(self):
            self.screen.blit(self.fruitimage,
                           (int(self.fruit.x * self.wall_width) + self.wall_width // 2 + BUFFER // 2,
                            int(self.fruit.y * self.wall_height) + self.wall_height // 2 + BUFFER // 2 - 7))

    def if_fruit_appear(self):
        if self.fruit_appear:
            if self.now() - self.last_switch > FRUIT_APPEAR:
                self.fruit_appear = False
                self.last_switch = self.now()
        else:
            if self.now() - self.last_switch > FRUIT_DISAPPEAR:
                self.fruit_appear = True
                self.last_switch = self.now()

    def draw_anime(self):
        self.change_state()
        if self.intro_state == 1:
            self.screen.blit(self.ghostimage[1],[200, 100])
            self.draw_text('Blinky', self.screen, [400, 100], 17, (200, 200, 200), 'arial black', centered=True)
            self.change_state()
        elif self.intro_state == 2:
            self.screen.blit(self.ghostimage[1],[200, 100])
            self.draw_text('Blinky', self.screen, [400, 100], 17, (200, 200, 200), 'arial black', centered=True)
            self.screen.blit(self.ghostimage[3], [200, 150])
            self.draw_text('Clyde', self.screen, [400, 150], 17, (200, 200, 200), 'arial black', centered=True)
            self.change_state()
        elif self.intro_state == 3:
            self.screen.blit(self.ghostimage[1],[200, 100])
            self.draw_text('Blinky', self.screen, [400, 100], 17, (200, 200, 200), 'arial black', centered=True)
            self.screen.blit(self.ghostimage[3], [200, 150])
            self.draw_text('Clyde', self.screen, [400, 150], 17, (200, 200, 200), 'arial black', centered=True)
            self.screen.blit(self.ghostimage[5], [200, 200])
            self.draw_text('Pinky', self.screen, [400, 200], 17, (200, 200, 200), 'arial black', centered=True)
            self.change_state()
        elif self.intro_state == 4:
            self.screen.blit(self.ghostimage[1],[200, 100])
            self.draw_text('Blinky', self.screen, [400, 100], 17, (200, 200, 200), 'arial black', centered=True)
            self.screen.blit(self.ghostimage[3], [200, 150])
            self.draw_text('Clyde', self.screen, [400, 150], 17, (200, 200, 200), 'arial black', centered=True)
            self.screen.blit(self.ghostimage[5], [200, 200])
            self.draw_text('Pinky', self.screen, [400, 200], 17, (200, 200, 200), 'arial black', centered=True)
            self.screen.blit(self.ghostimage[7], [200, 250])
            self.draw_text('Inky', self.screen, [400, 250], 17, (200, 200, 200), 'arial black', centered=True)
            self.change_state()
        elif self.intro_state >= 5:
            self.screen.blit(self.ghostimage[1], [200, 100])
            self.draw_text('Blinky', self.screen, [400, 100], 17, (200, 200, 200), 'arial black', centered=True)
            self.screen.blit(self.ghostimage[3], [200, 150])
            self.draw_text('Clyde', self.screen, [400, 150], 17, (200, 200, 200), 'arial black', centered=True)
            self.screen.blit(self.ghostimage[5], [200, 200])
            self.draw_text('Pinky', self.screen, [400, 200], 17, (200, 200, 200), 'arial black', centered=True)
            self.screen.blit(self.ghostimage[7], [200, 250])
            self.draw_text('Inky', self.screen, [400, 250], 17, (200, 200, 200), 'arial black', centered=True)
            self.get_anime_time()
            if self.anime_state == 1:
                self.pacman_anime()
                self.get_anime_time()
            elif self.anime_state == 2:
                self.pacman_anime()
                self.b_anime()
                self.get_anime_time()
            elif self.anime_state == 3:
                self.pacman_anime()
                self.b_anime()
                self.c_anime()
                self.get_anime_time()
            elif self.anime_state == 4:
                self.pacman_anime()
                self.b_anime()
                self.c_anime()
                self.p_anime()
                self.get_anime_time()
            elif self.anime_state >= 5:
                self.pacman_anime()
                self.b_anime()
                self.c_anime()
                self.p_anime()
                self.i_anime()
                self.get_anime_time()

    def pacman_anime(self):
        if self.move_state == 0:
            self.screen.blit(self.pacmanimage[0], [self.anime_pix[0], 300])
            self.anime_pix[0] -= 1
            self.change_move_state()
        elif self.move_state == 1 or self.move_state == 5:
            self.screen.blit(self.pacmanimage[1], [self.anime_pix[0], 300])
            self.anime_pix[0] -= 1
            self.change_move_state()
        elif self.move_state == 2 or self.move_state == 4:
            self.screen.blit(self.pacmanimage[2], [self.anime_pix[0], 300])
            self.anime_pix[0] -= 1
            self.change_move_state()
        elif self.move_state == 3:
            self.screen.blit(self.pacmanimage[3], [self.anime_pix[0], 300])
            self.anime_pix[0] -= 1
            self.change_move_state()

    def b_anime(self):
        if self.ghost_move_state == 0:
            self.screen.blit(self.ghostimage[0], [self.anime_pix[1], 300])
            self.anime_pix[1] -= 1
            self.change_ghost_move_state()
        elif self.ghost_move_state == 1:
            self.screen.blit(self.ghostimage[1], [self.anime_pix[1], 300])
            self.anime_pix[1] -= 1
            self.change_ghost_move_state()

    def c_anime(self):
        if self.ghost_move_state == 0:
            self.screen.blit(self.ghostimage[2], [self.anime_pix[2], 300])
            self.anime_pix[2] -= 1
            self.change_ghost_move_state()
        elif self.ghost_move_state == 1:
            self.screen.blit(self.ghostimage[3], [self.anime_pix[2], 300])
            self.anime_pix[2] -= 1
            self.change_ghost_move_state()

    def p_anime(self):
        if self.ghost_move_state == 0:
            self.screen.blit(self.ghostimage[4], [self.anime_pix[3], 300])
            self.anime_pix[3] -= 1
            self.change_ghost_move_state()
        elif self.ghost_move_state == 1:
            self.screen.blit(self.ghostimage[5], [self.anime_pix[3], 300])
            self.anime_pix[3] -= 1
            self.change_ghost_move_state()

    def i_anime(self):
        if self.ghost_move_state == 0:
            self.screen.blit(self.ghostimage[6], [self.anime_pix[4], 300])
            self.anime_pix[4] -= 1
            self.change_ghost_move_state()
        elif self.ghost_move_state == 1:
            self.screen.blit(self.ghostimage[7], [self.anime_pix[4], 300])
            self.anime_pix[4] -= 1
            self.change_ghost_move_state()

    def change_move_state(self):
        if self.now() - self.move_time > ANIME_INTERVAL:
            if self.move_state == 5:
                self.move_state = 0
            else:
                self.move_state += 1
            self.move_time = self.now()

    def change_ghost_move_state(self):
        if self.now() - self.ghost_move_time > ANIME_INTERVAL:
            if self.ghost_move_state == 1:
                self.ghost_move_state = 0
            else:
                self.ghost_move_state += 1
            self.ghost_move_time = self.now()

    def change_state(self):
        if self.now() - self.last_intro > INTRO_PRODUCE:
            self.intro_state += 1
            self.last_intro = self.now()

    def change_number(self):
        if self.pacman_image_number == 3:
            self.pacman_image_number = 0

    def get_anime_time(self):
        if self.now() - self.anime_time > ANIME_TIME:
            self.anime_state += 1
            self.anime_time = self.now()

    def update_high_score(self):
        if self.player.current_score > self.high_score:
            self.high_score = self.player.current_score

    def music(self):
        if self.music_switch == 1:
            pg.mixer.music.play(-1)
            self.music_switch = 0

    def change_bgm(self):
        if self.music_switch == 1:
            if self.run_mode:
                pg.mixer.music.load(self.powerBGM)
            else:
                pg.mixer.music.load(self.bgm)

    def show_highscore(self):
        self.if_highscore = True

    # intro

    def intro_update(self):
        pass

    def intro_draw(self):
        self.screen.fill((0,0,0))
        self.draw_anime()
        if self.if_highscore:
            self.draw_text('high score: {}'.format(self.high_score), self.screen, [GAMEWIDTH // 2, 600], 17,
                           (200, 200, 200), 'arial black', centered=True)
        self.draw_text('PRESS SPACE TO PLAY GAME', self.screen, [GAMEWIDTH // 2, 500], 17, (200, 200, 200), 'arial black',centered=True)
        self.draw_text('PRESS H FOR HIGH SCORE', self.screen, [GAMEWIDTH // 2, 550], 17, (200, 200, 200), 'arial black',centered=True)
        pg.display.update()

    def intro_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False
            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                self.state = 'playing'
                self.if_highscore = False
            if event.type == pg.KEYDOWN and event.key == pg.K_h:
                self.show_highscore()

    # playing

    def playing_update(self):
        self.player.update()
        for ghosts in self.ghost:
            ghosts.update()

        for ghosts in self.ghost:
            if ghosts.grid_pos == self.player.grid_pos:
                if ghosts.mode != "runaway" and ghosts.mode != "back":
                    self.remove_life()
                elif ghosts.mode == "runaway":
                    ghosts.mode = "back"
                    self.geating.play()
                    self.player.current_score += 200 * ghosts.deadghost
                    ghosts.deadghost += 1

    def playing_draw(self):
        self.screen.fill((0,0,0))
        self.screen.blit(self.background,(BUFFER//2,BUFFER//2))
        self.draw_coins()
        self.draw_powers()
        self.change_bgm()
        self.music()
        self.if_fruit_appear()
        if self.fruit_appear:
            self.draw_fruit()
        self.draw_text('SCORE: {}'.format(self.player.current_score),self.screen,[10,5],17,(200,200,200),'arial black')
        self.player.draw()
        for ghosts in self.ghost:
            ghosts.draw()
        pg.display.update()

    def playing_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_LEFT:
                    self.player.move(Vector(-1, 0))
                if event.key == pg.K_RIGHT:
                    self.player.move(Vector(1, 0))
                if event.key == pg.K_UP:
                    self.player.move(Vector(0, -1))
                if event.key == pg.K_DOWN:
                    self.player.move(Vector(0, 1))
                if event.key == pg.K_SPACE:
                    self.player.portal()
                if event.key == pg.K_r:
                    self.player.close_portal()

    def draw_coins(self):
        for coin in self.coins:
            pg.draw.circle(self.screen,(255,255,255),(int(coin.x*self.wall_width)+self.wall_width//2+BUFFER//2,
                                               int(coin.y*self.wall_height)+self.wall_height// 2+BUFFER//2),2)

    def draw_powers(self):
        for power in self.powers:
            pg.draw.circle(self.screen,(255,255,255),(int(power.x*self.wall_width)+self.wall_width//2+BUFFER//2,
                                               int(power.y*self.wall_height)+self.wall_height// 2+BUFFER//2),4)

    # over
    def over_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False
            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                self.reset()
            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                self.running = False
            if event.type == pg.KEYDOWN and event.key == pg.K_h:
                self.show_highscore()

    def over_update(self):
        pass

    def over_draw(self):
        self.update_high_score()
        self.screen.fill((0,0,0))
        quit_text = "Press the escape button to QUIT"
        again_text = "Press SPACE bar to PLAY AGAIN"
        high_text = "Press H to see high score"
        self.draw_text("GAME OVER", self.screen, [GAMEWIDTH // 2, 100], 52, (255,0,0), "arial", centered=True)
        self.draw_text(again_text, self.screen, [
            GAMEWIDTH // 2, GAMEHEIGHT // 2], 36, (190, 190, 190), "arial", centered=True)
        self.draw_text(quit_text, self.screen, [
            GAMEWIDTH // 2, GAMEHEIGHT // 1.5], 36, (190, 190, 190), "arial", centered=True)
        self.draw_text(high_text, self.screen, [
            GAMEWIDTH // 2, GAMEHEIGHT // 3], 36, (190, 190, 190), "arial", centered=True)
        if self.if_highscore:
            self.draw_text('high score: {}'.format(self.high_score), self.screen, [GAMEWIDTH // 2, 600], 17,
                           (200, 200, 200), 'arial black', centered=True)
        pg.display.update()