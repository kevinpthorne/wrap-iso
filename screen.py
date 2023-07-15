import pygame


WIDTH, HEIGHT = 1280, 768
display = None

def init():
    global display
    
    display = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Isometric Pygame Demo")
