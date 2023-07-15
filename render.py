from enum import Enum
from dataclasses import dataclass
from typing import List, Tuple

import pygame
from pygame.math import Vector2

from maps import Map
import screen

ScreenPos = Vector2
ProjectedPos = Vector2
MapPos = Vector2


TILE_SIZE = 64
TILE_OFFSET: ScreenPos = ScreenPos(screen.WIDTH // 2, -350) # TODO fix -150 constant, tie to window size

class ViewportDirection(Enum):
    LEFT = 0,
    UPLEFT = 1,
    UP = 2,
    UPRIGHT = 3,
    RIGHT = 4,
    DOWNRIGHT = 5,
    DOWN = 6,
    DOWNLEFT = 7

class Viewport:
    in_debug_mode = False
    background_fill = (0, 0, 0)
    camera_speed = 1
    map_viewport_size = MapPos(45, 45)

    the_map: Map
    map_offset: MapPos

    def __init__(self, the_map: Map):
        self.the_map = the_map
        self.map_offset = MapPos(0, 0)
        self.debug_font = pygame.font.SysFont("Verdana", 12)


    def on_update(self, map_entities: list, screen_entities: list):
        screen.window.fill(self.background_fill)  # Clear screen

        for viewport_x in range(0, int(self.map_viewport_size.x)):
            for viewport_y in range(0, int(self.map_viewport_size.y)):
                # Translates viewport's pos to map's pos
                map_x, map_y = (viewport_x + self.map_offset.x) % self.the_map.width, (viewport_y + self.map_offset.y) % self.the_map.height
                # project_pos = iso_project((viewport_x, viewport_y))
                project_pos = Vector2(
                    (viewport_x - viewport_y) * TILE_SIZE // 2 + TILE_OFFSET.x, 
                    (viewport_x + viewport_y) * TILE_SIZE // 4 + TILE_OFFSET.y
                )
                if project_pos.x > screen.WIDTH or project_pos.y > screen.HEIGHT or project_pos.x < -TILE_SIZE or project_pos.y < -TILE_SIZE:
                    continue

                # verts = calc_iso_vertices(project_pos)
                verts = (
                    (project_pos.x, project_pos.y + TILE_SIZE // 2),
                    (project_pos.x + TILE_SIZE // 2, project_pos.y + 15),  # TODO fix constant + 15
                    (project_pos.x + TILE_SIZE, project_pos.y + TILE_SIZE // 2),
                    (project_pos.x + TILE_SIZE // 2, project_pos.y + TILE_SIZE - 15)
                )
                pygame.draw.polygon(screen.window, self.the_map.at(map_x, map_y).color, verts)

                for entity in map_entities:
                    entity_x, entity_y = entity.position
                    if map_x == entity_x and map_y == entity_y:
                        rect = entity.surface.get_rect(topleft=(project_pos.x, project_pos.y))
                        screen.window.blit(entity.surface, rect)

                if self.in_debug_mode:
                    txt = self.debug_font.render(f'({map_x},{map_y})', False, (0,0,0), (255,255,255))
                    screen.window.blit(txt, (int(project_pos.x), int(project_pos.y)))

        for entity in screen_entities:
            screen.window.blit(entity.surface, entity.position)


    def move(self, direction: ViewportDirection):
        if direction == ViewportDirection.LEFT:
            self.map_offset.x -= self.camera_speed
            self.map_offset.y += self.camera_speed
        elif direction == ViewportDirection.UP:
            self.map_offset.x -= self.camera_speed
            self.map_offset.y -= self.camera_speed
        elif direction == ViewportDirection.RIGHT:
            self.map_offset.x += self.camera_speed
            self.map_offset.y -= self.camera_speed
        elif direction == ViewportDirection.DOWN:
            self.map_offset.x += self.camera_speed
            self.map_offset.y += self.camera_speed
        else:
            raise NotImplementedError()
