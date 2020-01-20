import pygame
import os

pygame.init()
SCRENN_SIZE = (800, 600)
screen = pygame.display.set_mode(SCRENN_SIZE)
clock = pygame.time.Clock()
FPS = 60
tiles_group = pygame.sprite.Group()
mouse_sprites = pygame.sprite.Group()
create_mode = 1
TILE_WIDTH = 63
TILE_HEIGHT = 37


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
            x, y = pygame.mouse.get_pos()
            #print(pygame.sprite.collide_mask(self, m))
            if pygame.sprite.collide_mask(self, m):
                #print(1)
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
                if not (type(elem) == Tile):
                    return False
                if pygame.sprite.collide_mask(elem, m):
                    return elem.get_x(), elem.get_y(),elem.get_coords()

    def add_item(self, i, j, elem):
        self.map[i][j] = elem


running = True
board = Board(10, 20, 10, 10)
while running:
    screen.fill((0, 120, 255))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            t = board.get_click(x, y)
            if t:
                i = t[2][0]
                j = t[2][1]
                x = t[0]
                y = t[1]
                board.add_item(i, j, Plant(x, y))
    mouse_sprites.update()
    mouse_sprites.draw(screen)
    board.update()
    board.draw()
    pygame.display.flip()
    clock.tick(FPS)
pygame.quit()