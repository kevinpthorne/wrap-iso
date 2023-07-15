import pygame

# Initialize Pygame
pygame.init()
pygame.font.init() # you have to call this at the start, 
                   # if you want to use this module.
my_font = pygame.font.SysFont('Comic Sans MS', 17)

# Set up the display
import screen
screen.init()

# Define colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
TILE_TYPES = (RED, YELLOW, GREEN, BLUE)

# Define tile size and offset
# tile_size = 64
# tile_offset = (screen.WIDTH // 2, 100)

# Load map
import maps
the_map = maps.Map.from_txt_file("assets/map.txt")

# Viewport
import render
viewport = render.Viewport(the_map)
FPS = 60
fps_clock = pygame.time.Clock()

# Entities
import entity
from render import MapPos, ScreenPos
map_entities = [
    entity.Player(MapPos(5, 5))
]
screen_entities = [
    entity.FpsCounter(fps_clock, ScreenPos(0, 0)),
    # entity.DebugRect(screen.WIDTH, screen.HEIGHT, ScreenPos(screen.WIDTH // 2, screen.HEIGHT // 2)),
    # entity.DebugRect(screen.WIDTH // 2, screen.HEIGHT // 2, ScreenPos(0, 0))
]

# Mouse
# pygame.event.set_grab(True)

# Game loop
running = True
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if event.key == pygame.K_F3:
                print(viewport.map_offset)
                print(map_entities[0].position)

    ## Pan
    mouse_x, mouse_y = pygame.mouse.get_pos()
    if mouse_x <= 0:
        viewport.move(render.ViewportDirection.LEFT)
    elif mouse_y <= 0:
        viewport.move(render.ViewportDirection.UP)
    elif mouse_x >= screen.WIDTH - 1:
        viewport.move(render.ViewportDirection.RIGHT)
    elif mouse_y >= screen.HEIGHT - 1:
        viewport.move(render.ViewportDirection.DOWN)

    if abs(viewport.map_offset.x) > the_map.width:
        viewport.map_offset.x = 0
    if abs(viewport.map_offset.y) > the_map.height:
        viewport.map_offset.y = 0

    viewport.on_update(map_entities, screen_entities)

    # Update the display
    pygame.display.flip()
    fps_clock.tick(FPS)

# Quit the game
pygame.quit()