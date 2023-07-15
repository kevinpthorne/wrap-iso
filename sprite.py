from abc import ABC, abstractmethod

import pygame

from render import MapPos

class Sprite(ABC):
    position: MapPos
    surface: pygame.Surface


class Player(Sprite):
    surface = pygame.image.load("assets/character.png")

    def __init__(self, pos: MapPos):
        self.position = pos
