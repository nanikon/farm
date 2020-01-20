import pygame
import os
import sqlite3

pygame.init()
SCRENN_SIZE = (800, 600)
screen = pygame.display.set_mode(SCRENN_SIZE)
clock = pygame.time.Clock()
FPS = 60

all_sprites = pygame.sprite.Group()
plant_sprites = pygame.sprite.Group()
animal_sprites = pygame.sprite.Group()
exit_button_sprites = pygame.sprite.Group()
market_button_sprites = pygame.sprite.Group()
inventar_button_sprites = pygame.sprite.Group()
task_button_sprites = pygame.sprite.Group()

con = sqlite3.connect("information.db")
cur = con.cursor()
inventar = dict()
product = cur.execute("""SELECT harvest FROM plant""").fetchall()
for i in product:
    inventar[i[0]] = 0
product = cur.execute("""SELECT harvest FROM animal""").fetchall()
for i in product:
    inventar[i[0]] = 0

active_screen = 1
active_task = 1
coins = 1000


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    image = pygame.image.load(fullname).convert()
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def draw_clock(x, y, time_s):
    font = pygame.font.Font(None, 16)
    text = font.render(time_s, 1, (0, 0, 0))
    text_w = text.get_width()
    text_h = text.get_height()
    pygame.draw.rect(screen, (255, 255, 255), (x, y, text_w + 20, text_h + 10))
    screen.blit(text, (x + 10, y + 5))


def draw_tick(x, y):
    font = pygame.font.Font(None, 25)
    text = font.render('Собрать!', 2, (0, 255, 0))
    text_w = text.get_width()
    text_h = text.get_height()
    x = x - text_w // 2 - 10
    pygame.draw.rect(screen, (255, 255, 255), (x, y, text_w + 20, text_h + 10))
    screen.blit(text, (x + 10, y + 5))


class Thing(pygame.sprite.Sprite):
    def __init__(self, group, pos_x, pos_y, tip='plant', name='sanimus'):
        super().__init__(group)
        self.images = []
        if tip == 'plant':
            maxx = 5
            t = cur.execute("""SELECT timer FROM plant WHERE name = ?""",
                                         (name,)).fetchall()[0][0]
            self.time_dead = t.split(':')[::-1]
            self.product = cur.execute("""SELECT harvest FROM plant WHERE name = ?""",
                                       (name,)).fetchall()[0][0]
        else:
            maxx = 3
            self.time_dead = cur.execute("""SELECT timer FROM animal WHERE name = ?""",
                                         (name,)).fetchall()[0][0].split(':')[::-1]
            self.product = cur.execute("""SELECT harvest FROM animal WHERE name = ?""",
                                       (name,)).fetchall()[0][0]
        for i in range(maxx):
            self.images.append(load_image(os.path.join(tip, name, str(i + 1) + '.png'), colorkey=(255, 255, 255)))
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.rect.x = pos_x
        self.rect.y = pos_y
        self.add(all_sprites)
        te = 0
        for t in range(len(self.time_dead)):
            te += (int(self.time_dead[t]) * 60 ** (t + 1))
        self.time_dead = te * 60
        self.mature = False

    def update(self):
        self.time_dead -= 60
        if active_screen == 1:
            self.drawing()

    def drawing(self):
        if self.time_dead <= 0:
            if not self.mature:
                draw_tick(self.rect.x + self.rect.w // 2, self.rect.y - 22)
        else:
            x, y = pygame.mouse.get_pos()
            if self.rect.collidepoint(x, y):
                min = self.time_dead // (60 ** 3)
                sec = (self.time_dead // 3600) % 60
                s = str(min).rjust(2, '0') + ':' + str(sec).rjust(2, '0')
                width = self.rect.w
                x = self.rect.x + width // 2 - 20
                y = self.rect.y - 22
                draw_clock(x, y, s)

    def harvest(self):
        if self.time_dead <= 0:
            self.mature = True


class Plant(Thing):
    def __init__(self, x, y, is_name):
        super().__init__(plant_sprites, x, y, tip='plant', name=is_name)
        self.one = self.time_dead // 4
        self.two = self.time_dead // 2
        self.three = (self.time_dead // 4) * 3

    def update(self):
        super().update()
        if (self.time_dead <= 0) and self.mature:
            self.kill()
        elif self.time_dead >= self.three:
            self.image = self.images[0]
        elif self.time_dead >= self.two:
            self.image = self.images[1]
        elif self.time_dead >= self.one:
            self.image = self.images[2]
        elif self.time_dead > 0:
            self.image = self.images[3]
        else:
            self.image = self.images[4]

    def harvest(self):
        super().harvest()
        inventar[self.product] += 1


class Animal(Thing):
    def __init__(self, x, y, is_name):
        super().__init__(animal_sprites, x, y, tip='animal', name=is_name)
        self.count = 0

    def update(self):
        super().update()

    def harvest(self):
        super().harvest()
        self.mature = False
        self.count += 1
        if self.count >= 4:
            self.image = self.images[2]
            inventar[self.product] += 1
        elif self.count >= 2:
            self.image = self.images[1]


class ExitButton(pygame.sprite.Sprite):
    image = load_image(os.path.join('buttons', 'exit.png'))

    def __init__(self):
        super().__init__(exit_button_sprites)
        self.image = ExitButton.image
        self.rect = self.image.get_rect()
        self.rect.x = SCRENN_SIZE[0] - 170
        self.rect.x = SCRENN_SIZE[1] - 10

    def on_click(self):
        active_screen = 1


class MarketButton(pygame.sprite.Sprite):
    image = load_image(os.path.join('buttons', 'market.png'))

    def __init__(self):
        super().__init__(market_button_sprites)
        self.image = MarketButton.image
        self.rect = self.image.get_rect()

    def on_click(self):
        active_screen = 2


class InventarButton(pygame.sprite.Sprite):
    image = load_image(os.path.join('buttons', 'inventar.png'))

    def __init__(self):
        super().__init__(inventar_button_sprites)
        self.image = InventarButton.image
        self.rect = self.image.get_rect()

    def on_click(self):
        active_screen = 3


class TaskButton(pygame.sprite.Sprite):
    image = load_image(os.path.join('buttons', 'task.png'))

    def __init__(self):
        super().__init__(task_button_sprites)
        self.image = TaskButton.image
        self.rect = self.image.get_rect()

    def on_click(self):
        active_screen = 4


def draw_farmin():
    pass


def draw_market():
    pass


def draw_inventar():
    pass


def draw_task():
    pass


running = True
while running:
    screen.fill((0, 0, 0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            hav = True
            for thing in all_sprites:
                if thing.rect.collidepoint(x, y):
                    thing.harvest()
                    hav = False
            if hav:
                Plant(x, y, 'sunflower')
    all_sprites.update()
    all_sprites.draw(screen)
    pygame.display.flip()
    clock.tick(FPS)
pygame.quit()