import pygame
import pygame.gfxdraw
from config import *

# Inicializa Pygame
pygame.init()


# Cargar la imagen de la plataforma
imagen_plataforma = pygame.image.load('assets/images/plataforma2.jpg').convert_alpha()
plataforma = pygame.Rect(200, 550, pantalla_ancho - 400, 500)
imagen_plataforma = pygame.transform.scale(imagen_plataforma, (plataforma.width, plataforma.height))

# Crear una superficie con bordes redondeados
def crear_superficie_redondeada(imagen, radio):
    ancho, alto = imagen.get_size()
    superficie_redondeada = pygame.Surface((ancho, alto), pygame.SRCALPHA)
    
    # Dibujar el fondo transparente
    superficie_redondeada.fill((0, 0, 0, 0))
    
    # Crear la máscara redondeada
    mask_surface = pygame.Surface((ancho, alto), pygame.SRCALPHA)
    mask_surface.fill((0, 0, 0, 0))
    pygame.draw.rect(mask_surface, (255, 255, 255, 255), (0, 0, ancho, alto), border_radius=radio)
    
    # Aplicar la máscara a la imagen de la plataforma
    superficie_redondeada.blit(mask_surface, (0, 0))
    superficie_redondeada.blit(imagen, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    
    return superficie_redondeada

# Crear la superficie redondeada
radio_borde = 60  # Ajusta el radio de los bordes redondeados
imagen_plataforma = crear_superficie_redondeada(imagen_plataforma, radio_borde)