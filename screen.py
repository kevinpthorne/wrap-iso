import pygame


WIDTH, HEIGHT = 1920, 1080
FPS = 60
window = None

def init():
    global window

    window = pygame.display.set_mode((WIDTH, HEIGHT), (
        0# pygame.OPENGL
    ), vsync=1)
    pygame.display.set_caption("Isometric Pygame Demo")
