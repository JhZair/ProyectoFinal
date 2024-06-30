import pygame

def cargar_sprites(hoja, num_sprites, ancho_sprite, alto_sprite, color, espejo=False):
    sprites = []
    for i in range(num_sprites):
        sprite = hoja.subsurface(pygame.Rect(i * ancho_sprite, 0, ancho_sprite, alto_sprite))
        sprite.set_colorkey(color)
        if espejo:
            sprite = pygame.transform.flip(sprite, True, False)  # Espejo horizontal
        sprites.append(sprite)
    return sprites

def pintar_superficie(surface, color):
    tinted_surface = surface.copy()
    tinted_surface.fill((0, 0, 0, 255), None, pygame.BLEND_RGBA_MULT)
    tinted_surface.fill(color[0:3] + (0,), None, pygame.BLEND_RGBA_ADD)
    return tinted_surface