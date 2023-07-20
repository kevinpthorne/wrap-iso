import pygame


WIDTH, HEIGHT = 1920, 1080
FPS = 60
window = None

def init():
    global window

    window = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Isometric Pygame Demo")
