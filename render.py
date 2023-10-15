from enum import Enum
from dataclasses import dataclass
from typing import List, Tuple

import pygame
from pygame.math import Vector2

# from entity import MapEntity
from maps import Map, TILE_REGISTRY
import screen

ScreenPos = Vector2
ProjectedPos = Vector2
MapPos = Vector2


TILE_RATIO = Vector2(2, 4)
TILE_SIZE = 8 # goes down by powers of 2 as viewport length goes up in powers of 2. 64, 64 is midpoint
MAP_VIEWPORT_LENGTH = 512
MAP_VIEWPORT_SIZE: MapPos = MapPos(MAP_VIEWPORT_LENGTH, MAP_VIEWPORT_LENGTH)
TILE_OFFSET: ScreenPos = ScreenPos(screen.WIDTH // 2 - (TILE_SIZE // TILE_RATIO.x), screen.HEIGHT // 2 - ((TILE_SIZE // TILE_RATIO.x) * MAP_VIEWPORT_SIZE.y // 2) - (TILE_SIZE // TILE_RATIO.y))
SHOW_GRID = False
TILE_ANGLE = TILE_SIZE // TILE_RATIO.y if not SHOW_GRID else TILE_SIZE // TILE_RATIO.y + 1

class ViewportDirection(Enum):
    LEFT = 0,
    UPLEFT = 1,
    UP = 2,
    UPRIGHT = 3,
    RIGHT = 4,
    DOWNRIGHT = 5,
    DOWN = 6,
    DOWNLEFT = 7

@dataclass
class ViewportDebugFlags:
    show_grid = False
    show_coords = False
    show_map_borders = True


class Viewport:
    debug_flags: ViewportDebugFlags = ViewportDebugFlags()
    background_fill = (0, 0, 0)
    camera_speed = 1

    # map_entity: MapEntity
    map_offset: MapPos

    def __init__(self, map_entity, debug_flags=None):
        self.map_entity = map_entity
        self.map_offset = MapPos(0, 0)
        self.debug_font = pygame.font.SysFont("Verdana", 12)
        self.debug_flags = debug_flags if debug_flags is not None else self.debug_flags


    def on_update(self, map_entities: list, screen_entities: list):
        screen.window.fill(self.background_fill)  # Clear screen

        self.map_entity.render(screen)
        self.map_entity.render_map_entities(screen, map_entities)

        for entity in screen_entities:
            if hasattr(entity, "surface"):
                screen.window.blit(entity.surface, entity.position)
            elif hasattr(entity, "render"):
                entity.render(screen)
            else:
                print(f"Warning: cannot render entity {entity}")


    def find_clicked_entity(self, map_entities: list, mouse_pos: ScreenPos):
        print('click')


    def move(self, direction: ViewportDirection):
        if direction == ViewportDirection.LEFT:
            self.map_entity.offset.x -= self.camera_speed
            self.map_entity.offset.y += self.camera_speed
        elif direction == ViewportDirection.UP:
            self.map_entity.offset.x -= self.camera_speed
            self.map_entity.offset.y -= self.camera_speed
        elif direction == ViewportDirection.RIGHT:
            self.map_entity.offset.x += self.camera_speed
            self.map_entity.offset.y -= self.camera_speed
        elif direction == ViewportDirection.DOWN:
            self.map_entity.offset.x += self.camera_speed
            self.map_entity.offset.y += self.camera_speed
        else:
            raise NotImplementedError()
