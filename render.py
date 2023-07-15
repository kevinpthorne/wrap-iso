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


# class MapPos:
#     x: int
#     y: int
#     map_ref: Map
    
#     def __init__(self, x: int, y: int, map_ref: Map):
#         self.x = x
#         self.y = y
#         self.map_ref = map_ref

    # @property
    # def x(self):
    #     return self._x

    # @property
    # def y(self):
    #     return self._y

    # @x.setter
    # def x(self, value: int):
    #     self._x = value# % self.map_ref.width

    # @y.setter
    # def y(self, value: int):
    #     self._y = value# % self.map_ref.height


TILE_SIZE = 64
TILE_OFFSET: ScreenPos = ScreenPos(screen.WIDTH // 2, 100)


def iso_project(pos: MapPos) -> ProjectedPos:
    x, y = pos
    iso_x = (x - y) * TILE_SIZE // 2
    iso_y = (x + y) * TILE_SIZE // 4
    return ProjectedPos(iso_x, iso_y)

def square_project(pos: MapPos) -> ProjectedPos:
    x, y = pos
    sq_x = x * TILE_SIZE
    sq_y = y * TILE_SIZE
    return ProjectedPos(sq_x, sq_y)


def calc_square_vertices(pos: ProjectedPos) -> List[int]:
    return [
        (pos.x, pos.y + (TILE_SIZE)), # BL
        (pos.x, pos.y), # TL
        (pos.x + (TILE_SIZE), pos.y), # TR
        (pos.x + (TILE_SIZE), pos.y + (TILE_SIZE)), # BR
    ]

def calc_iso_vertices(pos: ProjectedPos) -> List[int]:
    return [
        (pos.x + TILE_OFFSET.x, pos.y + TILE_OFFSET.y + TILE_SIZE // 2),
        (pos.x + TILE_OFFSET.x + TILE_SIZE // 2, pos.y + TILE_OFFSET.y + 15),  # TODO fix constant + 15
        (pos.x + TILE_OFFSET.x + TILE_SIZE, pos.y + TILE_OFFSET.y + TILE_SIZE // 2),
        (pos.x + TILE_OFFSET.x + TILE_SIZE // 2, pos.y + TILE_OFFSET.y + TILE_SIZE - 15)
    ]

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
    background_fill = (0, 0, 0)
    camera_speed = 1
    projection = "iso"
    projections = ["iso", "sq"]

    the_map: Map
    map_offset: MapPos

    def __init__(self, the_map: Map):
        self.the_map = the_map
        self.map_offset = MapPos(0, 0)
        assert self.projection in self.projections, f"Invalid projection '{self.projection}' in viewport"

    def _every_tile(self):
        if self.projection == "iso":
            iso_limit_x, iso_limit_y = 50, 50 # int(map_width * 2.5), int(map_height * 2.5)
            for x in range(-iso_limit_x, iso_limit_x):
                for y in range(-iso_limit_y, iso_limit_y):
                    yield x, y
            return
        elif self.projection == "sq":
            for x in range(0, screen.WIDTH // TILE_SIZE):
                for y in range(0, screen.height // TILE_SIZE):
                    yield x, y
            return

    @property
    def _project(self):
        if self.projection == "iso":
            return iso_project
        elif self.projection == "sq":
            return sq_project

    @property
    def _tile_vertices_calc(self):
        if self.projection == "iso":
            return calc_iso_vertices
        elif self.projection == "sq":
            return calc_square_vertices


    def on_update(self, entities: list):
        screen.display.fill(self.background_fill)  # Clear screen

        for viewport_x, viewport_y in self._every_tile():
            # Translates viewport's pos to map's pos
            map_x, map_y = (viewport_x + self.map_offset.x) % self.the_map.width, (viewport_y + self.map_offset.y) % self.the_map.height
            # project_pos = iso_project((viewport_x, viewport_y))
            project_pos = Vector2((viewport_x - viewport_y) * TILE_SIZE // 2, (viewport_x + viewport_y) * TILE_SIZE // 4)

            # verts = calc_iso_vertices(project_pos)
            verts = (
                (project_pos.x + TILE_OFFSET.x, project_pos.y + TILE_OFFSET.y + TILE_SIZE // 2),
                (project_pos.x + TILE_OFFSET.x + TILE_SIZE // 2, project_pos.y + TILE_OFFSET.y + 15),  # TODO fix constant + 15
                (project_pos.x + TILE_OFFSET.x + TILE_SIZE, project_pos.y + TILE_OFFSET.y + TILE_SIZE // 2),
                (project_pos.x + TILE_OFFSET.x + TILE_SIZE // 2, project_pos.y + TILE_OFFSET.y + TILE_SIZE - 15)
            )
            pygame.draw.polygon(screen.display, self.the_map.at(map_x, map_y).color, verts)

            for entity in entities:
                entity_x, entity_y = entity.position
                if map_x == entity_x and map_y == entity_y:
                    rect = entity.surface.get_rect(topleft=(project_pos.x, project_pos.y))
                    screen.display.blit(entity.surface, rect)

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
