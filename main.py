import json

import pygame

# Initialize Pygame
pygame.init()
pygame.font.init()

import screen
import maps
import render
import entity
from render import MapPos, ScreenPos

def mod_map_json(json: dict, key: str, by: int) -> dict:
    json[key] += by
    print(f"{key} = {json[key]}")
    return json

DEV_KEYS = {
    pygame.K_y: lambda map_json: mod_map_json(map_json, "size", 1),
    pygame.K_h: lambda map_json: mod_map_json(map_json, "size", -1),
    pygame.K_u: lambda map_json: mod_map_json(map_json, "frequency", 1),
    pygame.K_j: lambda map_json: mod_map_json(map_json, "frequency", -1),
    pygame.K_i: lambda map_json: mod_map_json(map_json, "octaves", 1),
    pygame.K_k: lambda map_json: mod_map_json(map_json, "octaves", -1),
    pygame.K_o: lambda map_json: mod_map_json(map_json, "persistence", 0.1),
    pygame.K_l: lambda map_json: mod_map_json(map_json, "persistence", -0.1),
    pygame.K_p: lambda map_json: mod_map_json(map_json, "lacunarity", 0.1),
    pygame.K_SEMICOLON: lambda map_json: mod_map_json(map_json, "lacunarity", -0.1),
}
IS_EDGE_PAN_ENABLED = True


def main():
    screen.init()
    fps_clock = pygame.time.Clock()

    # Map
    with open("assets/map.json", 'r') as json_file:
        map_json = json.load(json_file)

    is_running = True
    while is_running:
        try:
            print("Game loop mounted")
            the_map = maps.Map.from_noise(**map_json)

            print("Map generated. Mounting entities")
            # Entities
            map_entity = entity.MapEntity(the_map, ScreenPos(0, 0))
            map_entities = [
                # entity.Player(MapPos(35, 35))
            ]
            screen_entities = [
                entity.FpsCounter(fps_clock, ScreenPos(0, 0)),
                entity.UIRect(
                    4*the_map.width,
                    2*the_map.height,
                    ScreenPos(screen.WIDTH - 4*the_map.width, screen.HEIGHT - 2*(the_map.height)),
                ),
                entity.MapEntity(  # minimap
                    the_map,
                    ScreenPos(screen.WIDTH - 2*the_map.width, screen.HEIGHT - 2*(the_map.height)),
                    map_viewport_length=the_map.width,
                    tile_size=4,
                    tile_offset=ScreenPos(0, 0)
                ),
                entity.MinimapRect(
                    ScreenPos(screen.WIDTH - 4*the_map.width, screen.HEIGHT - 2*(the_map.height)),
                    map_entity
                )
                # entity.DebugRect(screen.WIDTH, screen.HEIGHT, ScreenPos(screen.WIDTH // 2, screen.HEIGHT // 2)),
                # entity.DebugRect(screen.WIDTH // 2, screen.HEIGHT // 2, ScreenPos(0, 0))
            ]
            print("Mounting viewport")
            # Viewport
            viewport = render.Viewport(map_entity)

            # Mouse
            # pygame.event.set_grab(True)

            # Game loop
            is_playing = True
            while is_playing:
                # Handle events
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        raise QuitGame()
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            raise QuitGame()
                        elif event.key == pygame.K_F3:
                            print(viewport.map_offset)
                            print(map_entities[0].position)
                        elif event.key == pygame.K_F5:
                            raise RefreshInitialState()
                        for dev_key in DEV_KEYS:
                            if event.key == dev_key:
                                map_json = DEV_KEYS[event.key](map_json)
                                raise RefreshInitialState()

                ## Pan
                if IS_EDGE_PAN_ENABLED:
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

                fps_clock.tick(screen.FPS)
        except RefreshInitialState:
            # print("Refreshing")
            pass
        except QuitGame:
            pygame.event.set_grab(False)
            break
        except:
            pygame.event.set_grab(False)
            raise

    # Quit the game
    pygame.quit()


class RefreshInitialState(Exception):
    pass

class QuitGame(Exception):
    pass


if __name__ == '__main__':
    main()