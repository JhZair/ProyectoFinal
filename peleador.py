import pygame
from sprites import cargar_sprites
from menu import pantalla
from arena import plataforma  

blanco = (255, 255, 255)
verde_vd = (1, 233, 12)
amarillos_ps = (255, 243, 78)
fondo_samurai = (192, 192, 192)


class Jugador:
    def __init__(self, color, rectan, aura, velocidad=2, fuerza_salto=7.5, gravedad=0.3, sprites=None):
        self.color = color
        self.rectan = rectan
        self.aura = aura
        self.velocidad = velocidad
        self.fuerza_salto = fuerza_salto
        self.gravedad = gravedad
        self.velocidad_y = 0
        self.en_plataforma = False
        self.salud = 500
        self.cooldown = 0
        self.ataque_especial = 0
        self.defendiendo = False

        # Animaciones
        self.sprites = sprites
        self.animacion_actual = "idle"
        self.animaciones = {
            "idle": cargar_sprites(pygame.image.load('assets/anims/samurai/idle_samurai.png').convert_alpha(), 10, 107.6, 140, fondo_samurai),
            "run": cargar_sprites(pygame.image.load('assets/anims/samurai/caminar_samurai.png').convert_alpha(), 8, 125, 140, fondo_samurai),
            "run_b": cargar_sprites(pygame.image.load('assets/anims/samurai/caminata_atras_samurai.png').convert_alpha(), 8, 118.25, 140, fondo_samurai),
            "jump": cargar_sprites(pygame.image.load('assets/anims/samurai/salto_samurai.png').convert_alpha(), 5, 108.2, 140, fondo_samurai),
            "attack": cargar_sprites(pygame.image.load('assets/anims/samurai/ataque_samurai.png').convert_alpha(), 5, 146.2, 140, fondo_samurai),
            "defense": cargar_sprites(pygame.image.load('assets/anims/samurai/bloqueo_samurai.png').convert_alpha(), 4, 109, 140, fondo_samurai)
        }
        self.sprite_index = 0
        self.image = self.animaciones[self.animacion_actual][self.sprite_index]
        self.tiempo_ultimo_sprite = pygame.time.get_ticks()
        self.tiempo_entre_sprites = 75  # Milisegundos entre cada frame de la animación


    def actualizar(self, teclas, izq, derecha, salto, defensa, ataque, otro_jugador):
        tiempo = pygame.time.get_ticks()
        if teclas[izq]:
            self.rectan.x -= self.velocidad
            self.aura.x -= self.velocidad
            self.animacion_actual = "run_b" 
    
        if teclas[derecha]:
            self.animacion_actual = "run"
            self.rectan.x += self.velocidad
            self.aura.x += self.velocidad

        if teclas[salto] and self.en_plataforma:
            self.en_plataforma = False
            self.velocidad_y = -self.fuerza_salto
        
        if not self.en_plataforma:
            self.animacion_actual = "jump"
        
        if teclas[ataque]:
            self.animacion_actual = "attack"
        
        if self.cooldown < tiempo and self.en_plataforma and not teclas[izq] and not teclas[derecha]:
            self.animacion_actual = "idle"
        
        #Aplicar gravedad
        self.rectan.y += self.velocidad_y
        self.aura.y += self.velocidad_y
        self.velocidad_y += self.gravedad

        # Colisión con la plataforma
        if self.rectan.colliderect(plataforma):
            self.rectan.bottom = plataforma.top
            self.aura.bottom = plataforma.top
            self.velocidad_y = 0
            self.en_plataforma = True

        # Colisión con el otro jugador
        if self.rectan.colliderect(otro_jugador.rectan):
            if teclas[izq]:
                self.rectan.x = otro_jugador.rectan.right
                self.aura.x = otro_jugador.rectan.right - 20
            if teclas[derecha]:
                self.rectan.x = otro_jugador.rectan.left - self.rectan.width
                self.aura.x = otro_jugador.rectan.left - self.aura.width + 20

        # Actualizar estado de defensa y velocidad de movimiento
        self.defendiendo = teclas[defensa]
        if self.defendiendo:
            self.velocidad = 2
            self.animacion_actual = "defense"
        else:
            self.velocidad = 5

        # Actualizar animación
        self.actualizar_animacion()

    def actualizar_animacion(self):
        ahora = pygame.time.get_ticks()
        if ahora - self.tiempo_ultimo_sprite > self.tiempo_entre_sprites:
            self.tiempo_ultimo_sprite = ahora
            self.sprite_index += 1
            if self.sprite_index >= len(self.animaciones[self.animacion_actual]):
                self.sprite_index = 0
            self.image = self.animaciones[self.animacion_actual][self.sprite_index]


    def bajar_salud(self, dano):
        self.salud -= dano
        if self.salud <= 0:
            self.salud = 0
            return True
        return False

    def incrementar_ataque_especial(self, incremento):
        self.ataque_especial += incremento
        if self.ataque_especial > 200:
            self.ataque_especial = 200

    def dibujar_barra_salud(self, posicion, espejo=False):
        ancho_barra = 500
        alto_barra = 30
        if espejo:
            barra = pygame.Rect(posicion[0] - ancho_barra, posicion[1], ancho_barra, alto_barra)
            progreso = pygame.Rect(posicion[0] - self.salud, posicion[1], self.salud, alto_barra)
        else:
            barra = pygame.Rect(posicion[0], posicion[1], ancho_barra, alto_barra)
            progreso = pygame.Rect(posicion[0], posicion[1], self.salud, alto_barra)
        pygame.draw.rect(pantalla, blanco, barra)
        pygame.draw.rect(pantalla, verde_vd, progreso)

    def dibujar_ataque_especial(self, posicion, espejo=False):
        ancho_barra = 200
        alto_barra = 15
        if espejo:
            barra = pygame.Rect(posicion[0] - ancho_barra, posicion[1], ancho_barra, alto_barra)
            progreso = pygame.Rect(posicion[0] - self.ataque_especial, posicion[1], self.ataque_especial, alto_barra)
        else:
            barra = pygame.Rect(posicion[0], posicion[1], ancho_barra, alto_barra)
            progreso = pygame.Rect(posicion[0], posicion[1], self.ataque_especial, alto_barra)
        pygame.draw.rect(pantalla, blanco, barra)
        pygame.draw.rect(pantalla, amarillos_ps, progreso)


    def dibujar(self):
        imagen_actual = self.animaciones[self.estado][self.frame_actual]
        pantalla.blit(imagen_actual, self.rectan.topleft)
