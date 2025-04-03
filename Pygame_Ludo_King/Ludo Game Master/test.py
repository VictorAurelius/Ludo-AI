import pygame
from pytmx.util_pygame import load_pygame

pygame.init()
screen = pygame.display.set_mode((800, 800))

# Load tile map
tiled_map = load_pygame('mapfinal/mapludo.tmx')

# Vẽ từng tile lên màn hình
for layer in tiled_map.visible_layers:
    for x, y, gid in layer:
        tile = tiled_map.get_tile_image_by_gid(gid)
        if tile:
            screen.blit(tile, (x * tiled_map.tilewidth, y * tiled_map.tileheight))

pygame.display.update()

# Thêm game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
    pygame.display.update()

pygame.quit()