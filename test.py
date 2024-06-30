import pygame
import sys
from config import *
import pygame.locals
from menu import mostrar_menu
from arena import plataforma, imagen_plataforma

# Inicializar Pygame
pygame.init()

# Configuración de la pantalla
pantalla = pygame.display.set_mode((pantalla_ancho, pantalla_alto))
pygame.display.set_caption("God's Fight")

# Colores
blanco = (255, 255, 255)
negro = (0, 0, 0)
gris = (117, 117, 117)
amarillo_vd = (255, 233, 0)
naranja = (255, 165, 0)
verde_aura = (0, 255, 0, 128)
verde_vd = (1, 233, 12)
azul_ats = (42, 144, 255)
fondo_samurai = (192, 192, 192)
fondo = (64,176,72)
color_tinte1 = (158,28,26)
color_tinte2 = (58,6,4)
color_tinte_proyectil = (215,88,44)

# Configuración del reloj
reloj = pygame.time.Clock()

# Fuente para el temporizador
fuente = pygame.font.Font(None, 74)

# Duración de la partida en segundos
duracion_partida = 120
inicio_tiempo = pygame.time.get_ticks()

def cargar_sprites(hoja, num_sprites, ancho_sprite, alto_sprite, color):
    sprites = []
    for i in range(num_sprites):
        sprite = hoja.subsurface(pygame.Rect(i * ancho_sprite, 0, ancho_sprite, alto_sprite))
        sprite.set_colorkey(color)
        sprites.append(sprite)

    return sprites

def pintar_superficie(surface, color):
    tinted_surface = surface.copy()
    tinted_surface.fill((0, 0, 0, 255), None, pygame.BLEND_RGBA_MULT)
    tinted_surface.fill(color[0:3] + (0,), None, pygame.BLEND_RGBA_ADD)
    return tinted_surface

class Jugador:
    def __init__(self, rectan, aura, velocidad=2, fuerza_salto=7.5, cooldown_inicial=1500):
        self.rectan = rectan
        self.aura = aura
        self.velocidad = velocidad
        self.velocidad_inicial = velocidad
        self.fuerza_salto = fuerza_salto
        self.gravedad = 0.3
        self.velocidad_y = 0
        self.en_plataforma = False
        self.max_salud = 700
        self.salud = self.max_salud
        self.vidas = 2
        self.reapareciendo = False
        self.cooldown_inicial = cooldown_inicial
        self.cooldown = 0
        self.ataque_especial = 0
        self.defendiendo = False
        self.retroceso_x = 0
        self.retroceso_y = 0
        self.proyectiles = []
        self.doble_salto = False

    def actualizar_animacion(self):
        ahora = pygame.time.get_ticks()
        if ahora - self.tiempo_ultimo_sprite > self.tiempo_entre_sprites:
            self.tiempo_ultimo_sprite = ahora
            self.indice_sprite += 1
            if self.indice_sprite >= len(self.animaciones[self.animacion_actual]):
                self.indice_sprite = 0
            self.imagen = self.animaciones[self.animacion_actual][self.indice_sprite]

    def actualizar(self, teclas, izq, derecha, salto, defensa, ataque, ataque_f, otro_jugador):
        tiempo = pygame.time.get_ticks()
        if teclas[izq]:
            if self.en_plataforma:
                self.animacion_actual = "run_b"
            self.rectan.x -= self.velocidad
            self.aura.x -= self.velocidad
            if self.rectan.colliderect(plataforma):
                self.rectan.left = plataforma.right
                self.aura.left = plataforma.right
    
        if teclas[derecha]:
            if self.en_plataforma:
                self.animacion_actual = "run"
            self.rectan.x += self.velocidad
            self.aura.x += self.velocidad
            if self.rectan.colliderect(plataforma):
                self.rectan.right = plataforma.left
                self.aura.right = plataforma.left

        # Manejar los saltos (implementado en las subclases)
        self.manejar_saltos(teclas, salto)

        if not self.en_plataforma and otro_jugador.animacion_actual != 'attack':
            self.animacion_actual = "jump"
        
        if teclas[ataque]:
            self.animacion_actual = "attack"
            if otro_jugador.rectan.colliderect(self.rectan):
                otro_jugador.animacion_actual = "hit"

        self.defendiendo = teclas[defensa]
        if self.defendiendo:
            self.velocidad = self.velocidad_inicial * 0.2
            self.animacion_actual = "defense"
        else:
            self.velocidad = self.velocidad_inicial
        
        if self.reapareciendo:
            self.animacion_actual = "death"

        if self.cooldown < tiempo and not (teclas[izq] or teclas[derecha] or teclas[salto] or teclas[defensa]) and otro_jugador.animacion_actual != 'attack' and self.en_plataforma:
            self.animacion_actual = "idle"

        # Aplicar gravedad
        self.rectan.y += self.velocidad_y
        self.aura.y += self.velocidad_y
        self.velocidad_y += self.gravedad
        if self.velocidad_y > 2:
            self.en_plataforma = False

        # Aplicar retroceso
        self.rectan.x += self.retroceso_x
        self.rectan.y += self.retroceso_y
        self.aura.x += self.retroceso_x
        self.aura.y += self.retroceso_y

        # Reducir el retroceso gradualmente
        self.retroceso_x *= 0.9
        self.retroceso_y *= 0.9

        # Colisión con la plataforma
        if self.rectan.colliderect(plataforma):
            if self.velocidad_y > 0:  # Sólo ajustar si el jugador está cayendo
                self.rectan.bottom = plataforma.top
                self.aura.bottom = plataforma.top
                self.velocidad_y = 0
                self.en_plataforma = True
                self.reapareciendo = False
            else:
                self.en_plataforma = False

        # Actualizar animación
        self.actualizar_animacion()
    
    def manejar_saltos(self, teclas, salto):
        if teclas[salto] and self.en_plataforma:
            self.velocidad_y = -self.fuerza_salto
            self.en_plataforma = False

    def bajar_salud(self, dano, direccion_retroceso):
        self.salud -= dano
        if self.salud <= 0:
            if self.vidas == 2:
                self.perder_vida()
            else:
                self.salud = 0
                return True
        # Aplicar retroceso basado en la dirección del ataque
        self.retroceso_x = direccion_retroceso[0]
        self.retroceso_y = direccion_retroceso[1]
        return False
    
    def perder_vida(self):
        self.vidas -= 1
        if self.vidas > 0:
            self.salud = self.max_salud
            self.reapareciendo = True
            self.rectan.y = -self.rectan.height
            self.aura.y = -self.aura.height
            self.rectan.x = pantalla_ancho // 2 - self.rectan.width * 0.2
            self.aura.x = pantalla_ancho // 2 - self.aura.width * 0.2

    def incrementar_ataque_especial(self, incremento):
        self.ataque_especial += incremento
        if self.ataque_especial > 200:
            self.ataque_especial = 200

    def dibujar_barra_salud(self, posicion, espejo=False):
        ancho_barra = self.max_salud
        alto_barra = 30
        if self.vidas == 2:
            if espejo:
                barra = pygame.Rect(posicion[0] - ancho_barra, posicion[1], ancho_barra, alto_barra)
                progreso_primera_vida = pygame.Rect(posicion[0] - self.salud, posicion[1], self.salud, alto_barra)
            else:
                barra = pygame.Rect(posicion[0], posicion[1], ancho_barra, alto_barra)
                progreso_primera_vida = pygame.Rect(posicion[0], posicion[1], self.salud, alto_barra)
            pygame.draw.rect(pantalla, verde_vd, barra)  # Dibujar el contorno de la barra
            pygame.draw.rect(pantalla, amarillo_vd, progreso_primera_vida)  # Barra amarilla para la primera vida
        elif self.vidas == 1:
            if espejo:
                barra = pygame.Rect(posicion[0] - ancho_barra, posicion[1], ancho_barra, alto_barra)
                progreso = pygame.Rect(posicion[0] - self.salud, posicion[1], self.salud, alto_barra)
            else:
                barra = pygame.Rect(posicion[0], posicion[1], ancho_barra, alto_barra)
                progreso = pygame.Rect(posicion[0], posicion[1], self.salud, alto_barra)
            pygame.draw.rect(pantalla, blanco, barra)  # Dibujar el contorno de la barra
            pygame.draw.rect(pantalla, verde_vd, progreso)  # Barra roja para la vida restante

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
        pygame.draw.rect(pantalla, azul_ats, progreso)
    
    def disparar_proyectil(self, otro_jugador):
        direccion = 1 if self.rectan.x < otro_jugador.rectan.x else -1
        velocidad = 5
        posicion = (self.rectan.x + 5,self.rectan.y + 50)
        proyectil = Proyectil(posicion, velocidad, direccion)
        self.proyectiles.append(proyectil)

    def actualizar_proyectiles(self):
        for proyectil in self.proyectiles:
            proyectil.actualizar()

    def dibujar_proyectiles(self):
        for proyectil in self.proyectiles:
            proyectil.dibujar()

# Definición de las subclases
class Samurai(Jugador):
    def __init__(self, rectan, aura):
        super().__init__(rectan, aura, velocidad=4.5, fuerza_salto=7)
        self.saltos_maximos = 2
        self.dobles_saltos_restantes = self.saltos_maximos
        self.tiempo_ultimo_salto = 0
        self.animacion_actual = "idle"
        self.animaciones = {
            "idle": [pintar_superficie(sprite, color_tinte1) for sprite in cargar_sprites(pygame.image.load('assets/anims/samurai/idle_samurai.png').convert_alpha(), 10, 107.6, 140, fondo_samurai)],
            "run": [pintar_superficie(sprite, color_tinte1) for sprite in cargar_sprites(pygame.image.load('assets/anims/samurai/caminar_samurai.png').convert_alpha(), 8, 110, 140, fondo_samurai)],
            "run_b": [pintar_superficie(sprite, color_tinte1) for sprite in cargar_sprites(pygame.image.load('assets/anims/samurai/caminata_atras_samurai.png').convert_alpha(), 8, 110, 140, fondo_samurai)],
            "jump": [pintar_superficie(sprite, color_tinte1) for sprite in cargar_sprites(pygame.image.load('assets/anims/samurai/salto_samurai.png').convert_alpha(), 5, 108.2, 140, fondo_samurai)],
            "attack": [pintar_superficie(sprite, color_tinte1) for sprite in cargar_sprites(pygame.image.load('assets/anims/samurai/ataque_samurai.png').convert_alpha(), 5, 140, 140, fondo_samurai)],
            "defense": [pintar_superficie(sprite, color_tinte1) for sprite in cargar_sprites(pygame.image.load('assets/anims/samurai/bloqueo_samurai.png').convert_alpha(), 2, 100, 140, fondo_samurai)],
            'hit': [pintar_superficie(sprite, color_tinte1) for sprite in cargar_sprites(pygame.image.load('assets/anims/samurai/dañado_samurai.png').convert_alpha(), 5, 121.6, 140, fondo_samurai)],
            'shoot': [pintar_superficie(sprite, color_tinte1) for sprite in cargar_sprites(pygame.image.load('assets/anims/samurai/disparo_samurai.png').convert_alpha(), 7, 195, 140, fondo_samurai)],
            'death': [pintar_superficie(sprite, color_tinte1) for sprite in cargar_sprites(pygame.image.load('assets/anims/samurai/muerte_samurai.png').convert_alpha(), 9, 155, 120, fondo_samurai)]
        }
        self.indice_sprite = 0
        self.imagen = self.animaciones[self.animacion_actual][self.indice_sprite]
        self.tiempo_ultimo_sprite = pygame.time.get_ticks()
        self.tiempo_entre_sprites = 100  # Milisegundos entre cada frame de la animación
    
    def manejar_saltos(self, teclas, salto):
        tiempo_actual = pygame.time.get_ticks()
        if teclas[salto]: 
            if self.dobles_saltos_restantes > 0 and (tiempo_actual - self.tiempo_ultimo_salto >= 500):
                self.velocidad_y = -self.fuerza_salto
                self.dobles_saltos_restantes -= 1
                self.tiempo_ultimo_salto = tiempo_actual
                if self.rectan.bottom > plataforma.top - 5:
                    self.en_plataforma = False
    
    def actualizar(self, teclas, izq, derecha, salto, defensa, ataque, ataque_f, otro_jugador):
        super().actualizar(teclas, izq, derecha, salto, defensa, ataque, ataque_f, otro_jugador)
        if self.en_plataforma:
            self.dobles_saltos_restantes = self.saltos_maximos

class Hanzo(Jugador):
    def __init__(self, rectan, aura):
        super().__init__(rectan, aura, velocidad=4, fuerza_salto=10)
        # Animaciones
        self.cooldown_inicial = 1000
        self.animacion_actual = "idle"
        self.animaciones = {
            "idle": [pintar_superficie(sprite, color_tinte2) for sprite in cargar_sprites(pygame.image.load('assets/anims/hanzo/Idle_Hanzo.png').convert_alpha(), 10, 100, 118, fondo)],
            "run": [pintar_superficie(sprite, color_tinte2) for sprite in cargar_sprites(pygame.image.load('assets/anims/hanzo/caminata_Hanzo.png').convert_alpha(), 10, 110, 120, fondo)],
            "run_b": [pintar_superficie(sprite, color_tinte2) for sprite in cargar_sprites(pygame.image.load('assets/anims/hanzo/caminataparaatras_Hanzo.png').convert_alpha(), 10, 100, 130, fondo)],
            "jump": [pintar_superficie(sprite, color_tinte2) for sprite in cargar_sprites(pygame.image.load('assets/anims/hanzo/salto_Hanzo.png').convert_alpha(), 6, 80, 150, fondo)],
            "attack": [pintar_superficie(sprite, color_tinte2) for sprite in cargar_sprites(pygame.image.load('assets/anims/hanzo/ataque_Hanzo.png').convert_alpha(), 6, 140, 120, fondo)],
            "defense": [pintar_superficie(sprite, color_tinte2) for sprite in cargar_sprites(pygame.image.load('assets/anims/hanzo/bloqueo_Hanzo.png').convert_alpha(), 2, 110, 120, fondo)],
            'hit': [pintar_superficie(sprite, color_tinte2) for sprite in cargar_sprites(pygame.image.load('assets/anims/hanzo/daño_Hanzo.png').convert_alpha(), 2, 100, 110, fondo)],
            'shoot': [pintar_superficie(sprite, color_tinte2) for sprite in cargar_sprites(pygame.image.load('assets/anims/hanzo/ataquep_Hanzo.png').convert_alpha(), 5, 155, 120, fondo)],
            'death': [pintar_superficie(sprite, color_tinte2) for sprite in cargar_sprites(pygame.image.load('assets/anims/hanzo/muerte_Hanzo.png').convert_alpha(), 9, 130, 110, fondo)]
        }
        self.indice_sprite = 0
        self.imagen = self.animaciones[self.animacion_actual][self.indice_sprite]
        self.tiempo_ultimo_sprite = pygame.time.get_ticks()
        self.tiempo_entre_sprites = 100  # Milisegundos entre cada frame de la animación

    def disparar_proyectil(self, otro_jugador):
        direccion = 1 if self.rectan.x < otro_jugador.rectan.x else -1
        velocidad = 5
        proyectil1 = Proyectil((self.rectan.centerx -20, self.rectan.centery), velocidad, direccion)
        proyectil2 = Proyectil((self.rectan.centerx, self.rectan.centery - 30), velocidad, direccion)
        self.proyectiles.append(proyectil1)
        self.proyectiles.append(proyectil2)

class Proyectil:
    def __init__(self, posicion, velocidad, direccion, sprites=None):
        self.rect = pygame.Rect(posicion, (70, 10))
        self.velocidad = velocidad
        self.direccion = direccion
        self.sprites = sprites
        self.animacion_actual = "disparo"
        self.animaciones = {
            "disparo": [pintar_superficie(sprite, color_tinte_proyectil) for sprite in cargar_sprites(pygame.image.load('assets/anims/hanzo/proyectil_Hanzo.png').convert_alpha(), 1, 60, 30, fondo)],
        }
        self.sprite_index = 0
        self.image = self.animaciones[self.animacion_actual][self.sprite_index]
        self.tiempo_ultimo_sprite = pygame.time.get_ticks()
        self.tiempo_entre_sprites = 3000  # Milisegundos entre cada frame de la animación

    def actualizar(self):
        self.rect.x += self.velocidad * self.direccion

    def dibujar(self):
        imagen_actual = self.animaciones[self.animacion_actual][self.sprite_index]
        pantalla.blit(imagen_actual, self.rect.topleft)
        
class Juego:
    def __init__(self):
        self.jugador1 = Samurai(pygame.Rect(pantalla_ancho // 2 - 240, 550, 80, 130), pygame.Rect(pantalla_ancho // 2 - 240, 200, 115, 130))
        self.jugador2 = Hanzo(pygame.Rect(pantalla_ancho // 2 + 240, 550, 80, 115), pygame.Rect(pantalla_ancho // 2 + 240, 200, 115, 130))
        self.ejecutando = True
        # Cargar la imagen de fondo
        self.fondo = pygame.image.load("assets/images/img1.jpeg")
        self.fondo = pygame.transform.scale(self.fondo, (pantalla_ancho, pantalla_alto))

    def comprobar_colisiones_y_ataques(self, teclas, ataque_j1, ataque_j2, ataque_especial_j1, ataque_especial_j2, proyectil_j1, proyectil_j2):
        tiempo_actual = pygame.time.get_ticks()
        if teclas[ataque_j1] and tiempo_actual > self.jugador1.cooldown:
            if self.jugador1.aura.colliderect(self.jugador2.aura) and teclas[ataque_j1] and tiempo_actual > self.jugador1.cooldown and not self.jugador1.defendiendo:
                self.jugador1.incrementar_ataque_especial(50)
                direccion_retroceso = (10, -5)
                if self.jugador2.defendiendo:
                    if self.jugador2.bajar_salud(10, direccion_retroceso):
                        print("Jugador 2 ha sido derrotado")
                        return True
                else:
                    if self.jugador2.bajar_salud(30, direccion_retroceso):
                        print("Jugador 2 ha sido derrotado")
                        return True
            self.jugador1.cooldown = tiempo_actual + self.jugador1.cooldown_inicial

        if teclas[ataque_j2] and tiempo_actual > self.jugador2.cooldown:
            if self.jugador2.aura.colliderect(self.jugador1.aura) and teclas[ataque_j2] and tiempo_actual > self.jugador2.cooldown and not self.jugador2.defendiendo:
                self.jugador2.incrementar_ataque_especial(50)
                direccion_retroceso = (-10, -5)
                if self.jugador1.defendiendo:
                    if self.jugador1.bajar_salud(10, direccion_retroceso):
                        print("Jugador 1 ha sido derrotado")
                        return True
                else:
                    if self.jugador1.bajar_salud(30, direccion_retroceso):
                        print("Jugador 1 ha sido derrotado")
                        return True
            self.jugador2.cooldown = tiempo_actual + self.jugador2.cooldown_inicial

        # Verificar si el jugador cae fuera de la pantalla
        if self.jugador1.rectan.top > pantalla_alto:
            if self.jugador1.vidas == 2:
                self.jugador1.perder_vida()
            else:
                print("Jugador 1 ha sido derrotado")
                return True
            
        if self.jugador2.rectan.top > pantalla_alto:
            if self.jugador2.vidas == 2:
                self.jugador2.perder_vida()
            else:
                print("Jugador 2 ha sido derrotado")
                return True

        # Comprobar ataques especiales
        if teclas[ataque_especial_j1] and self.jugador1.ataque_especial == 200 and not self.jugador1.defendiendo and self.jugador1.aura.colliderect(self.jugador2.rectan):
            self.jugador1.ataque_especial = 0
            direccion_retroceso = (20, -10)
            if self.jugador2.bajar_salud(50, direccion_retroceso):
                print("Jugador 2 ha sido derrotado")
                return True

        if teclas[ataque_especial_j2] and self.jugador2.ataque_especial == 200 and not self.jugador2.defendiendo and self.jugador2.aura.colliderect(self.jugador1.rectan):
            self.jugador2.ataque_especial = 0
            direccion_retroceso = (-20, -10)
            if self.jugador1.bajar_salud(50, direccion_retroceso):
                print("Jugador 1 ha sido derrotado")
                return True

        # Comprobar ataques con proyectil
        if teclas[proyectil_j1] and self.jugador1.cooldown < tiempo_actual:
            self.jugador1.disparar_proyectil(self.jugador2)
            self.jugador1.cooldown = tiempo_actual + self.jugador1.cooldown_inicial * 1.5
        if teclas[proyectil_j2] and self.jugador2.cooldown < tiempo_actual:
            self.jugador2.disparar_proyectil(self.jugador1)
            self.jugador2.cooldown = tiempo_actual + self.jugador2.cooldown_inicial * 1.5

        # Actualizar proyectiles y comprobar colisiones con jugadores
        self.jugador1.actualizar_proyectiles()
        self.jugador2.actualizar_proyectiles()

        for proyectil in self.jugador1.proyectiles:
            if proyectil.rect.colliderect(self.jugador2.rectan):
                self.jugador1.proyectiles.remove(proyectil)
                if self.jugador2.bajar_salud(20, (10, -5)):
                    print("Jugador 2 ha sido derrotado")
                    return True

        for proyectil in self.jugador2.proyectiles:
            if proyectil.rect.colliderect(self.jugador1.rectan):
                self.jugador2.proyectiles.remove(proyectil)
                if self.jugador1.bajar_salud(20, (-10, -10)):
                    print("Jugador 1 ha sido derrotado")
                    return True

        return False
    
    def dibujar_tiempo_restante(self, tiempo_restante):
        minutos = tiempo_restante // 60
        segundos = tiempo_restante % 60
        texto_tiempo = fuente.render(f"{minutos:02}:{segundos:02}", True, blanco)
        pantalla.blit(texto_tiempo, (pantalla_ancho // 2 - texto_tiempo.get_width() // 2, 10))

    def determinar_ganador(self):
        if self.jugador1.salud > self.jugador2.salud:
            print("Jugador 1 gana por salud")
        elif self.jugador2.salud > self.jugador1.salud:
            print("Jugador 2 gana por salud")
        else:
            print("Empate")

    def ejecutar(self):
        if mostrar_menu():
            inicio_tiempo = pygame.time.get_ticks()

            while self.ejecutando:
                for evento in pygame.event.get():
                    if evento.type == pygame.QUIT:
                        self.ejecutando = False

                # Obtener el estado de las teclas
                teclas = pygame.key.get_pressed()

                # Actualizar los jugadores
                self.jugador1.actualizar(teclas, pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_s, pygame.K_r,pygame.K_t, self.jugador2)
                self.jugador2.actualizar(teclas, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN, pygame.K_i, pygame.K_o, self.jugador1)

                # Comprobar colisiones entre las auras y los jugadores, y ataques
                if self.comprobar_colisiones_y_ataques(teclas, pygame.K_r, pygame.K_i, pygame.K_t, pygame.K_o, pygame.K_y, pygame.K_p):
                    self.ejecutando = False
                
                # Dibujar la imagen de fondo
                pantalla.blit(self.fondo, (0, 0))

                # Dibujar todo en la pantalla
                pantalla.blit(self.jugador1.imagen, self.jugador1.rectan.topleft)
                pantalla.blit(self.jugador2.imagen, self.jugador2.rectan.topleft)
                pantalla.blit(imagen_plataforma, plataforma)

                # Dibujar las auras para visualización (opcional)
                # pygame.draw.rect(pantalla, verde_transparente, self.jugador1.aura)
                # pygame.draw.rect(pantalla, verde_transparente, self.jugador2.aura)

                # Dibujar la salud de los jugadores
                self.jugador1.dibujar_barra_salud((10, 10))
                self.jugador2.dibujar_barra_salud((pantalla_ancho - 10, 10), espejo=True)

                # Dibujar la barra de ataque especial
                self.jugador1.dibujar_ataque_especial((10, 50))
                self.jugador2.dibujar_ataque_especial((pantalla_ancho - 10, 50), espejo=True)

                # Dibujar proyectiles
                self.jugador1.dibujar_proyectiles()
                self.jugador2.dibujar_proyectiles()

                # Calcular y dibujar el tiempo restante
                tiempo_transcurrido = (pygame.time.get_ticks() - inicio_tiempo) // 1000
                tiempo_restante = duracion_partida - tiempo_transcurrido
                self.dibujar_tiempo_restante(tiempo_restante)
                
                # Verificar si el tiempo se ha agotado
                if tiempo_restante <= 0:
                    self.determinar_ganador()
                    self.ejecutando = False

                # Actualizar la pantalla
                pygame.display.flip()

                # Controlar la velocidad del juego
                reloj.tick(60)

            pygame.quit()
            sys.exit()

# Crear una instancia del juego y ejecutarlo
juego = Juego()
juego.ejecutar()

# Mecánicas:
# agregar direcciones a cada personaje,
# Animaciones:
# terminar de añadir animaciones para Hanzo; hacer que las animaciones tengan su espejo; mejorar animación de bloqueo de samurai; 
# segun que dirección tenga es pj es una animación en espejo o no; añadir animación de ataque especial samurai
# Interfaces:
# Interfaz de selección de personajes; mejorar interfaz de inicio del juego; agregar interfaz de pausa; mejorar las barras de vida, contadores y fuentes;
# agregar pantall de muerte al caer de la plataforma.
# General:
# Falta contador inicial para iniciar el juego; falta pantalla final al ganar un jugador; dividir las funcionalidades por archivos;
# agregar efectos de sonido y música de fondo; mejorar imagen de plataforma.