from abc import ABC, abstractmethod
from dataclasses import dataclass

import pygame
from pygame.math import Vector2

from maps import Map, TILE_REGISTRY
from render import MapPos, ScreenPos

import screen

class Composite:
    entities: list

    def __init__(self, entities):
        self.entities = entities

    def render(self, screen):
        for entity in self.entities:
            if entity.surface is not None:
                screen.window.blit(entity.surface, entity.position)
            elif entity.render:
                entity.render(screen)

    def __iter__(self):
        self.i = 0
        return self

    def __next__(self):
        if self.i < len(self.entities):
            x = self.entities[self.i]
            self.i += 1
            return x
        raise StopIteration


class Sprite(ABC):
    position: MapPos
    # offset: ScreenPos = ScreenPos(0, 0)
    surface: pygame.Surface


class Player(Sprite):
    surface = pygame.image.load("assets/character.png")

    def __init__(self, pos: MapPos):
        self.position = pos


class FpsCounter:
    position: ScreenPos
    font = pygame.font.SysFont("Verdana", 20)

    def __init__(self, clock, pos: ScreenPos):
        self.position = pos
        self.clock = clock
        self.font = pygame.font.SysFont("Verdana", 20)

    @property
    def surface(self) -> pygame.Surface:
        return self.font.render(str(round(self.clock.get_fps(),2)), True, (0,0,0), (255,255,255))

class DebugRect:
    position: ScreenPos
    surface = None

    def __init__(self, w: int, h: int, pos: ScreenPos):
        self.position = pos
        self.w = w
        self.h = h
    
    def render(self, screen) -> None:
        pygame.draw.rect(screen.window, [255, 0, 255], [self.position.x, self.position.y, self.w, self.h], 1)


class UIRect:
    position: ScreenPos
    surface = None

    def __init__(self, w: int, h: int, pos: ScreenPos):
        self.position = pos
        self.w = w
        self.h = h
    
    def render(self, screen) -> None:
        pygame.draw.rect(screen.window, [0, 0, 0], [self.position.x, self.position.y, self.w, self.h])


class MapEntity:
    surface = None

    position: ScreenPos
    offset: MapPos # = MapPos(0,0)
    the_map: Map
    map_viewport_length: int
    tile_size: int
    tile_ratio: Vector2
    tile_offset: ScreenPos
    tile_angle: int
    show_grid: bool = False
    show_coords: bool = False
    show_map_borders: bool = True

    def __init__(self, the_map: Map, pos: ScreenPos, map_viewport_length=128, tile_size=32, tile_ratio=Vector2(2, 4), tile_offset=None):
        self.position = pos
        self.offset = MapPos(0, 0)
        self.the_map = the_map
        self.map_viewport_length = map_viewport_length
        self.tile_size = tile_size
        self.tile_ratio = tile_ratio

        self.map_viewport_size = Vector2(self.map_viewport_length, self.map_viewport_length)

        # This defaults to the center of the window
        if tile_offset is not None:
            self.tile_offset = tile_offset
        else:
            entity_width, entity_height = self.screen_rect
            center_width = screen.WIDTH // 2
            center_height = screen.HEIGHT // 2
            self.tile_offset = ScreenPos(center_width - entity_width, center_height - entity_height)
        
        self.tile_angle = self.tile_size // self.tile_ratio.y
        if self.show_grid:
            self.tile_angle += 1

    @property
    def screen_rect(self):
        return (
            self.tile_size // self.tile_ratio.x, # width
            ((self.tile_size // self.tile_ratio.x) * self.map_viewport_size.y // 2) - (self.tile_size // self.tile_ratio.y) # height
        )


    def render(self, screen) -> None:
        for viewport_x in range(0, int(self.map_viewport_size.x)):
            for viewport_y in range(0, int(self.map_viewport_size.y)):
                # Translates viewport's pos to map's pos
                map_x, map_y = (viewport_x + self.offset.x) % self.the_map.width, (viewport_y + self.offset.y) % self.the_map.height
                # project_pos = iso_project((viewport_x, viewport_y))
                project_pos = Vector2(
                    (viewport_x - viewport_y) * self.tile_size // self.tile_ratio.x + self.tile_offset.x + self.position.x, 
                    (viewport_x + viewport_y) * self.tile_size // self.tile_ratio.y + self.tile_offset.y + self.position.y
                )
                
                # Culling
                if project_pos.x > screen.WIDTH or project_pos.y > screen.HEIGHT or project_pos.x < -self.tile_size or project_pos.y < -self.tile_size:
                    continue

                # verts = calc_iso_vertices(project_pos)
                verts = (
                    (project_pos.x, project_pos.y + self.tile_size // 2),
                    (project_pos.x + self.tile_size // 2, project_pos.y + self.tile_angle),  # TODO fix constant + 15
                    (project_pos.x + self.tile_size, project_pos.y + self.tile_size // 2),
                    (project_pos.x + self.tile_size // 2, project_pos.y + self.tile_size - self.tile_angle)
                )
                tile = self.the_map.at(map_x, map_y)
                if self.show_map_borders and (map_x == 0 or map_y == 0):
                    tile = TILE_REGISTRY[0]
                pygame.draw.polygon(screen.window, tile.color, verts)

    def render_map_entities(self, screen, map_entities):
        for entity in map_entities:
            map_x, map_y = (entity.position.x + self.offset.x) % self.the_map.width, (entity.position.y + self.offset.y) % self.the_map.height
            project_pos = Vector2(
                (entity.position.x - entity.position.y) * self.tile_size // self.tile_ratio.x + self.tile_offset.x + self.position.x, 
                (entity.position.x + entity.position.y) * self.tile_size // self.tile_ratio.y + self.tile_offset.y + self.position.y
            )

            # Culling
            if project_pos.x > screen.WIDTH or project_pos.y > screen.HEIGHT or project_pos.x < -self.tile_size or project_pos.y < -self.tile_size:
                continue

            rect = entity.surface.get_rect(topleft=(project_pos.x, project_pos.y))
            screen.window.blit(entity.surface, rect)


class MinimapRect:
    position: ScreenPos
    map_entity: MapEntity
    surface = None

    def __init__(self, pos: ScreenPos, map_entity: MapEntity):
        self.position = pos
        self.map_entity = map_entity
        self.w = map_entity.the_map.width * 2
        self.h = map_entity.the_map.height * 1
    
    def render(self, screen) -> None:
        viewport_x, viewport_y = self.map_entity.offset
        map_x, map_y = (viewport_x) % self.map_entity.the_map.width, (viewport_y) % self.map_entity.the_map.height
        project_pos = Vector2(
            (map_x - map_y) * 4 // self.map_entity.tile_ratio.x + 0, 
            (map_x + map_y) * 4 // self.map_entity.tile_ratio.y + 0
        )
        pygame.draw.rect(screen.window, [255, 255, 255], [
            self.position.x + (self.w / 2) + project_pos.x,
            self.position.y + (self.h / 2) + project_pos.y,
            self.w,
            self.h
        ], 1)

