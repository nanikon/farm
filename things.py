import pygame
import os
import sqlite3

pygame.init()
SCRENN_SIZE = (710, 540)
TILE_WIDTH = 63
TILE_HEIGHT = 37
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
pay_buttons_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
mouse_sprites = pygame.sprite.Group()

con = sqlite3.connect("information.db")
cur = con.cursor()
inventar = dict()
product = cur.execute("""SELECT harvest FROM plant""").fetchall()
for i in product:
    inventar[i[0]] = 0
product = cur.execute("""SELECT harvest FROM animal""").fetchall()
for i in product:
    inventar[i[0]] = 0
market_plant = cur.execute("""SELECT name, name_rus, timer FROM plant""").fetchall()
market_animal = cur.execute("""SELECT name, name_rus, timer FROM animal""").fetchall()

active_screen = 1
active_task = 1
create_mode = 0
payed_elem = ''
payed_tip = ''
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
    font = pygame.font.Font(None, 12)
    text = font.render('Собрать!', 2, (0, 255, 0))
    text_w = text.get_width()
    text_h = text.get_height()
    x = x - text_w // 2 - 10
    pygame.draw.rect(screen, (255, 255, 255), (x, y, text_w + 20, text_h + 10))
    screen.blit(text, (x + 10, y + 5))


def draw_frame():
    color = pygame.Color(160, 82, 45)
    pygame.draw.rect(screen, color, (0, 0, SCRENN_SIZE[0], 20), 0)
    pygame.draw.rect(screen, color, (0, 0, 20, SCRENN_SIZE[1]), 0)
    pygame.draw.rect(screen, color, (SCRENN_SIZE[0] - 20, 0, SCRENN_SIZE[0], SCRENN_SIZE[1]), 0)
    pygame.draw.rect(screen, color, (0, 420, SCRENN_SIZE[0], SCRENN_SIZE[1]), 0)
    market_button_sprites.update()
    market_button_sprites.draw(screen)
    inventar_button_sprites.draw(screen)
    task_button_sprites.draw(screen)
    font = pygame.font.Font(None, 16)
    text = font.render('Монеты:' + str(coins), 2, (255, 255, 255))
    text_w = text.get_width()
    screen.blit(text, (SCRENN_SIZE[0] - text_w - 10, 5))


class DopMouse(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(mouse_sprites)
        self.image = load_image(os.path.join('tiles', 'mouse.png'), colorkey=-1)
        self.rect = self.image.get_rect().move(10, 10)
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        x, y = pygame.mouse.get_pos()
        self.rect.x = x
        self.rect.y = y


m = DopMouse()


class Tile(pygame.sprite.Sprite):
    image = load_image(os.path.join('tiles', 'tile.png'), colorkey=-1)
    image_act = load_image(os.path.join('tiles', 'tile_active.png'), colorkey=-1)

    def __init__(self, pos_x, pos_y, top, left):
        super().__init__(tiles_group)
        self.image = Tile.image
        self.rect = self.image.get_rect()
        self.coords = (pos_x, pos_y)
        if pos_y % 2 == 1:
            self.pos_x = TILE_WIDTH * pos_x + left
            self.pos_y = TILE_HEIGHT * (pos_y // 2) + top
        else:
            self.pos_x = TILE_WIDTH * (pos_x + 0.5) + left
            self.pos_y = TILE_HEIGHT * (pos_y // 2 + 0.5) + top
        self.rect = self.rect.move(self.pos_x, self.pos_y)
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        if create_mode == 1:
            if pygame.sprite.collide_mask(self, m):
                self.image = Tile.image_act
            else:
                self.image = Tile.image

    def get_x(self):
        return self.pos_x

    def get_y(self):
        return self.pos_y

    def get_image(self):
        return self.image

    def get_coords(self):
        return self.coords


class Board:
    def __init__(self, width, height, top, left):
        self.width = width
        self.height = height
        self.map = []
        for i in range(self.height):
            b = []
            for j in range(self.width):
                b.append(Tile(j, i, top, left))
            self.map.append(b)

    def update(self):
        for row in self.map:
            for elem in row:
                elem.update()

    def draw(self):
        for row in self.map:
            for elem in row:
                screen.blit(elem.get_image(), (elem.get_x(), elem.get_y()))

    def get_click(self, x, y):
        for row in self.map:
            for elem in row:
                if pygame.sprite.collide_mask(elem, m):
                    if not (type(elem) == Tile):
                        return False
                    return elem.get_x(), elem.get_y(),elem.get_coords()

    def add_item(self, i, j, elem):
        self.map[j][i] = elem


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
            self.images.append(load_image(os.path.join(tip, name, str(i + 1) + '.png'), colorkey=-1))
        self.image = self.images[0]
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.x = pos_x
        self.rect.y = pos_y - (self.rect.h - TILE_HEIGHT)
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
            # x, y = pygame.mouse.get_pos()
            if pygame.sprite.collide_mask(self, m):
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

    def get_image(self):
        return self.image

    def get_x(self):
        return self.rect.x

    def get_y(self):
        return self.rect.y


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
        self.mask = pygame.mask.from_surface(self.image)

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
            self.mask = pygame.mask.from_surface(self.image)
            inventar[self.product] += 1
        elif self.count >= 2:
            self.image = self.images[1]
            self.mask = pygame.mask.from_surface(self.image)


class ExitButton(pygame.sprite.Sprite):
    image = load_image(os.path.join('buttons', 'exit.png'))

    def __init__(self):
        super().__init__(exit_button_sprites)
        self.image = pygame.transform.scale(ExitButton.image, (50, 50))
        self.rect = self.image.get_rect()
        self.rect.x = SCRENN_SIZE[0] - 70
        self.rect.y = 20
        self.mask = pygame.mask.from_surface(self.image)

    def onclick(self):
        global active_screen
        active_screen = 1


class MarketButton(pygame.sprite.Sprite):
    image = load_image(os.path.join('buttons', 'market.png'))

    def __init__(self):
        super().__init__(market_button_sprites)
        self.image = pygame.transform.scale(MarketButton.image, (200, 75))
        self.rect = self.image.get_rect()
        self.rect.y = 440
        self.rect.x = 20
        self.mask = pygame.mask.from_surface(self.image)

    def onclick(self):
        global active_screen
        active_screen = 2
        return


class InventarButton(pygame.sprite.Sprite):
    image = load_image(os.path.join('buttons', 'inventar.png'))

    def __init__(self):
        super().__init__(inventar_button_sprites)
        self.image = pygame.transform.scale(InventarButton.image, (251, 75))
        self.rect = self.image.get_rect()
        self.rect.y = 440
        self.rect.x = 228
        self.mask = pygame.mask.from_surface(self.image)

    def onclick(self):
        global active_screen
        active_screen = 3
        return


class TaskButton(pygame.sprite.Sprite):
    image = load_image(os.path.join('buttons', 'task.png'))

    def __init__(self):
        super().__init__(task_button_sprites)
        self.image = pygame.transform.scale(TaskButton.image, (202, 75))
        self.rect = self.image.get_rect()
        self.rect.y = 440
        self.rect.x = 488
        self.mask = pygame.mask.from_surface(self.image)

    def onclick(self):
        global active_screen
        active_screen = 4
        return


class PayButton(pygame.sprite.Sprite):
    image = load_image(os.path.join('buttons', 'pay.png'))

    def __init__(self, x, y, elem, tip):
        super().__init__(pay_buttons_sprites)
        self.image = PayButton.image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.elem = elem
        self.tip = tip
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        if pygame.sprite.collide_mask(self, m):
            self.onclick()

    def onclick(self):
        global create_mode, active_screen, payed_elem, payed_tip
        create_mode = 1
        active_screen = 4
        payed_elem = self.elem
        payed_tip = self.tip


def draw_farmin():
    screen.fill((0, 150, 255))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if pygame.sprite.collide_mask(magazin, m):
                magazin.onclick()
            x, y = event.pos
            t = board.get_click(x, y)
            if t and create_mode == 1:
                i = t[2][0]
                j = t[2][1]
                x = t[0]
                y = t[1]
                if payed_tip == 'plant':
                    board.add_item(i, j, Plant(x, y, payed_elem))
                else:
                    board.add_item(i, j, Animal(x, y, payed_elem))
                create_mode = 0
            else:
                for elem in all_sprites:
                    if pygame.sprite.collide_mask(elem, m):
                        elem.harvest()
    mouse_sprites.update()
    mouse_sprites.draw(screen)
    tiles_group.update()
    tiles_group.draw(screen)
    all_sprites.draw(screen)
    all_sprites.update()
    draw_frame()


def draw_market():
    screen.fill((255, 222, 173))
    font = pygame.font.Font(None, 16)
    text = font.render('Растения:', 2, (10, 10, 0))
    screen.blit(text, (30, 30))
    for i, elem in enumerate(market_plant):
        m_image = load_image(os.path.join('plant', elem[0], '5.png'), colorkey=-1)
        screen.blit(m_image, (30 + 210 * i, 50))
        font = pygame.font.Font(None, 20)
        text = font.render(elem[1], 2, (0, 0, 0))
        screen.blit(text, (30 + 210 * i + 70, 50))
        text = font.render('Время:' + elem[2], 2, (0, 0, 0))
        screen.blit(text, (30 + 210 * i + 70, 70))
        PayButton(30 + 210 * i, 130, elem[0], 'plant')
    font = pygame.font.Font(None, 16)
    text = font.render('Животные:', 2, (10, 10, 0))
    screen.blit(text, (30, 200))
    for i, elem in enumerate(market_animal):
        m_image = load_image(os.path.join('animal', elem[0], '3.png'), colorkey=-1)
        screen.blit(m_image, (30 + 210 * i, 220))
        font = pygame.font.Font(None, 20)
        text = font.render(elem[1], 2, (0, 0, 0))
        screen.blit(text, (30 + 210 * i + 70, 220))
        text = font.render('Время:' + elem[2], 2, (0, 0, 0))
        screen.blit(text, (30 + 210 * i + 70, 240))
        PayButton(30 + 210 * i, 310, elem[0], 'animal')
    pay_buttons_sprites.draw(screen)
    draw_frame()
    mouse_sprites.update()
    mouse_sprites.draw(screen)
    exit_button_sprites.draw(screen)
    pass


def draw_inventar():
    screen.fill((255, 222, 173))
    draw_frame()
    font = pygame.font.Font(None, 30)
    text = font.render('Появится в будущем', 2, (0, 0, 0))
    screen.blit(text, (50, 50))
    mouse_sprites.update()
    mouse_sprites.draw(screen)
    exit_button_sprites.draw(screen)
    pass


def draw_task():
    screen.fill((255, 222, 173))
    draw_frame()
    font = pygame.font.Font(None, 30)
    text = font.render('Появится в будущем', 2, (0, 0, 0))
    screen.blit(text, (50, 50))
    mouse_sprites.update()
    mouse_sprites.draw(screen)
    exit_button_sprites.draw(screen)
    pass


magazin = MarketButton()
inv = InventarButton()
tas = TaskButton()
e = ExitButton()

running = True
board = Board(10, 20, 25, 25)
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if pygame.sprite.collide_mask(magazin, m):
                magazin.onclick()
            elif pygame.sprite.collide_mask(e, m):
                e.onclick()
            elif pygame.sprite.collide_mask(inv, m):
                inv.onclick()
            elif pygame.sprite.collide_mask(tas, m):
                tas.onclick()
    if active_screen == 1:
        draw_farmin()
    elif active_screen == 2:
        draw_market()
    elif active_screen == 3:
        draw_inventar()
    else:
        draw_task()
    pygame.display.flip()
    clock.tick(FPS)
pygame.quit()