import pygame
import pytmx

pygame.init()

filename = 'map.tmx'
display_width = 1260
display_height = 470

white = (255, 255, 255)

gameScreen = pygame.display.set_mode((display_width, display_height))
gameScreen.fill((6, 164, 221))
pygame.display.set_caption('Заповедник "Плюк"')
clock = pygame.time.Clock()

# load map data
gameMap = pytmx.load_pygame(filename, pixelalpha=True)


def game_loop():
    gameExit = False
    while not gameExit:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
               gameExit = True
        for layer in gameMap.visible_layers:
            k, n, kp = 0, 0, 0
            dy = 0
            for x, y, gid, in layer:
                kp = k
                k = y
                if k != kp:
                    dy += 0.5
                tile = gameMap.get_tile_image_by_gid(gid)
                if k % 2 == 0:
                    gameScreen.blit(tile, (x * gameMap.tilewidth, (y - dy) * gameMap.tileheight))
                else:
                    gameScreen.blit(tile, ((x + 0.5) * gameMap.tilewidth, (y - dy) * gameMap.tileheight))
        pygame.display.update()
        clock.tick(60)

game_loop()
pygame.quit()