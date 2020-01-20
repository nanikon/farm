import pygame
import os
import sqlite3

pygame.init()
SCRENN_SIZE = (800, 600)
screen = pygame.display.set_mode(SCRENN_SIZE)
clock = pygame.time.Clock()
all_sprites = pygame.sprite.Group()
FPS = 60


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
        else:
            maxx = 3
        for i in range(maxx):
            self.images.append(load_image(os.path.join(tip, name, str(i + 1) + '.jpg')))
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.rect.x = pos_x
        self.rect.y = pos_y
        self.time_dead = 60 * 60 * 60
        self.mature = False

    def update(self):
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
            self.time_dead -= 60

    def harvest(self):
        if self.time_dead <= 0:
            self.mature = True


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
                Thing(all_sprites, x, y)
    all_sprites.update()
    all_sprites.draw(screen)
    pygame.display.flip()
    clock.tick(FPS)
pygame.quit()