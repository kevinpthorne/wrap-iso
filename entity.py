from abc import ABC, abstractmethod

import pygame

from render import MapPos, ScreenPos

class Sprite(ABC):
    position: MapPos
    surface: pygame.Surface


class Player(Sprite):
    surface = pygame.image.load("assets/character.png")

    def __init__(self, pos: MapPos):
        self.position = pos


class FpsCounter:
    position: ScreenPos
    font = pygame.font.SysFont("Verdana", 20)
    # surface: pygame.Surface

    def __init__(self, clock, pos: ScreenPos):
        self.position = pos
        self.clock = clock
        self.font = pygame.font.SysFont("Verdana", 20)

    @property
    def surface(self):
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

