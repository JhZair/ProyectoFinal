import pygame

def cargar_sprites(hoja, num_sprites, ancho_sprite, alto_sprite, color):
    sprites = []
    for i in range(num_sprites):
        sprite = hoja.subsurface(pygame.Rect(i * ancho_sprite, 0, ancho_sprite, alto_sprite))
        sprite.set_colorkey(color)
        sprites.append(sprite)

    return sprites