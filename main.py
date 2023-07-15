import pygame

# Initialize Pygame
pygame.init()
pygame.font.init() # you have to call this at the start, 
                   # if you want to use this module.
my_font = pygame.font.SysFont('Comic Sans MS', 17)

# Set up the display
width, height = 1280, 768
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Isometric Pygame Demo")

# Define colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
TILE_TYPES = (RED, YELLOW, GREEN, BLUE)

# Define tile size and offset
tile_size = 64
tile_offset = (width // 2, 100)

# Load map
with open("assets/map.txt", 'r') as file:
    raw_map = file.read().split("\n")
line_lengths = list(map(lambda line: len(line), raw_map))
assert min(line_lengths) == max(line_lengths), "Map lines must be of the same width and height!"

map_width = max(line_lengths)
map_height = len(raw_map)
the_map = [[0 for _ in range(0, map_width)] for _ in range(0, map_height)]
map_tiles = {
    "w": 3,
    "g": 2
}

for y in range(0, map_height):
    for x in range(0, map_width):
        char = raw_map[y][x]
        the_map[y][x] = map_tiles[char]

# Load character sprite
character_image = pygame.image.load("assets/character.png")
character_pos = (5, 5)
map_offset = [0, 0]
camera_speed = 1

# Define the isometric projection function
def iso_project(pos):
    x, y = pos
    iso_x = (x - y) * tile_size // 2
    iso_y = (x + y) * tile_size // 4
    return iso_x, iso_y

def sq_project(pos):
    x, y = pos
    sq_x = x * tile_size
    sq_y = y * tile_size
    return sq_x, sq_y

# Mouse
# pygame.event.set_grab(True)

# Game loop
running = True
render_iso = True
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                map_offset[1] += camera_speed
            elif event.key == pygame.K_s:
                map_offset[1] -= camera_speed
            elif event.key == pygame.K_a:
                map_offset[0] += camera_speed
            elif event.key == pygame.K_d:
                map_offset[0] -= camera_speed
            elif event.key == pygame.K_ESCAPE:
                running = False
            
            if abs(map_offset[0]) > map_width:
                map_offset[0] = 0
            if abs(map_offset[1]) > map_height:
                map_offset[1] = 0
            print(map_offset)
            print(character_pos)

    ## Pan
    mouse_x, mouse_y = pygame.mouse.get_pos()
    if mouse_x <= 0:
        map_offset[0] -= camera_speed # / 2
        #map_offset[1] -= camera_speed / 2
    elif mouse_y <= 0:
        map_offset[1] -= camera_speed
    elif mouse_x >= width - 1:
        map_offset[0] += camera_speed
    elif mouse_y >= height - 1:
        map_offset[1] += camera_speed

    # Clear the screen
    screen.fill(WHITE)

    if render_iso:
        # render iso
        iso_limit_x, iso_limit_y = 50, 50 # int(map_width * 2.5), int(map_height * 2.5)
        for x in range(-iso_limit_x, iso_limit_x):
            for y in range(-iso_limit_y, iso_limit_y):
                map_x, map_y = (x + map_offset[0]) % map_width, (y + map_offset[1]) % map_height
                iso_x, iso_y = iso_project((x, y))

                tile_vertices = [
                    (iso_x + tile_offset[0], iso_y + tile_offset[1] + tile_size // 2),
                    (iso_x + tile_offset[0] + tile_size // 2, iso_y + tile_offset[1] + 15),
                    (iso_x + tile_offset[0] + tile_size, iso_y + tile_offset[1] + tile_size // 2),
                    (iso_x + tile_offset[0] + tile_size // 2, iso_y + tile_offset[1] + tile_size - 15)
                ]
                pygame.draw.polygon(screen, TILE_TYPES[the_map[map_y][map_x]], tile_vertices)

                char_x, char_y = character_pos
                if map_x == char_x and map_y == char_y:
                    character_rect = character_image.get_rect(topleft=(iso_x, iso_y))
                    screen.blit(character_image, character_rect)
    else:
        # render debug squares
        for x in range(0, width // tile_size):
            for y in range(0, height // tile_size):
                map_x, map_y = (x + map_offset[0]) % map_width, (y + map_offset[1]) % map_height
                sq_x, sq_y = sq_project((x, y))

                sq_tile_vertices = [
                    (sq_x, sq_y + (tile_size)), # BL
                    (sq_x, sq_y), # TL
                    (sq_x + (tile_size), sq_y), # TR
                    (sq_x + (tile_size), sq_y + (tile_size)), # BR
                ]
                pygame.draw.polygon(screen, TILE_TYPES[the_map[map_y][map_x]], sq_tile_vertices)
                txt = my_font.render(f'({map_x},{map_y})', False, (0,0,0))
                screen.blit(txt, (sq_x, sq_y))

                char_x, char_y = character_pos
                if map_x == char_x and map_y == char_y:
                    character_rect = character_image.get_rect(topleft=(sq_x, sq_y))
                    screen.blit(character_image, character_rect)

    # Update the display
    pygame.display.flip()

# Quit the game
pygame.quit()