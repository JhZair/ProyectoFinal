import pygame
from sprites import cargar_sprites ,pintar_superficie
from config import *
from arena import plataforma

blanco = (255, 255, 255)
gris = (117, 117, 117)
amarillo_vd = (255, 233, 0)
verde_aura = (0, 255, 0, 128)
verde_vd = (1, 233, 12)
azul_ats = (42, 144, 255)
fondo_samurai = (192, 192, 192)
fondo_hanzo = (64,176,72)
color_tinte1 = (158,28,26)
color_tinte2 = (58,6,4)
color_tinte_proyectil = (215,88,44)

class Jugador:
    def __init__(self, rectan, aura, velocidad=7, fuerza_salto=15, cooldown_inicial=1500):
        self.rectan = rectan
        self.aura = aura
        self.velocidad = velocidad
        self.velocidad_inicial = velocidad
        self.fuerza_salto = fuerza_salto
        self.__gravedad = 1.9
        self.velocidad_y = 0
        self.en_plataforma = False
        self.max_salud = 700
        self.salud = self.max_salud
        self.vidas = 2
        self.imagen_primera_vida = pygame.image.load('assets/images/barra_de_vida2.png').convert_alpha()
        self.imagen_segunda_vida = pygame.image.load('assets/images/barra_de_vida.png').convert_alpha()
        self.imagen_barra_ataque = pygame.image.load('assets/images/barra_de_ataque.png').convert_alpha()
        self.imagen_barra_margen = pygame.image.load('assets/images/barra.png').convert_alpha()
        self.reapareciendo = False
        self.cooldown_inicial = cooldown_inicial
        self.cooldown = 0
        self.ataque_especial = 0
        self.defendiendo = False
        self.retroceso_x = 0
        self.retroceso_y = 0
        self.proyectiles = []
        self.cooldown_animacion = 0

    def actualizar(self, teclas, izq, derecha, salto, defensa, ataque, ataque_s, ataque_p, emote, otro_jugador):
        tiempo = pygame.time.get_ticks()
        # Resetear animación a idle al inicio de la actualización si no hay otro cooldown activo
        if self.cooldown <= tiempo and self.cooldown_animacion <= tiempo and not self.reapareciendo:
            self.animacion_actual = "idle"

        # Animación de movimiento hacia la izquierda
        if teclas[izq]:
            if self.en_plataforma:
                self.animacion_actual = "run_b"
            self.rectan.x -= self.velocidad
            self.aura.x -= self.velocidad
            if self.rectan.colliderect(plataforma):
                self.rectan.left = plataforma.right
                self.aura.left = plataforma.right
    
        # Animación de movimiento hacia la derecha
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

        # Animación de salto
        if not self.en_plataforma and self.animacion_actual not in ["attack", "attack_s", "shoot"] and not self.proyectiles:
            self.animacion_actual = "jump"

        # Animación de ataque
        if teclas[ataque] and self.cooldown_animacion <= tiempo:
            self.animacion_actual = "attack"
            self.cooldown_animacion = tiempo + 300
            if self.rectan.colliderect(otro_jugador.rectan):
                otro_jugador.animacion_actual = "hit"
                otro_jugador.cooldown_animacion = tiempo + 500

        # Animación de ataque especial
        if teclas[ataque_s] and self.ataque_especial == 200 and self.rectan.colliderect(otro_jugador.rectan) and self.cooldown_animacion <= tiempo:
            self.animacion_actual = "attack_s"
            self.cooldown_animacion = tiempo + 800 
            otro_jugador.animacion_actual = "hit"
            otro_jugador.cooldown_animacion = tiempo + 500

        # Animación de disparo
        if teclas[ataque_p] and self.cooldown_animacion <= tiempo:
            self.animacion_actual = "shoot"
            self.cooldown_animacion = tiempo + 100

        # Animación de defensa
        self.defendiendo = teclas[defensa]
        if self.defendiendo:
            self.velocidad = self.velocidad_inicial * 0.2
            self.animacion_actual = "defense"
        else:
            self.velocidad = self.velocidad_inicial

        # Animación de muerte
        if self.reapareciendo:
            self.animacion_actual = "death"
            self.cooldown_animacion = tiempo + 150

        if teclas[emote] and self.cooldown_animacion <= tiempo:
            self.animacion_actual = "intro_vict"
            self.cooldown_animacion = tiempo + 200

        # Aplicar gravedad
        self.rectan.y += self.velocidad_y
        self.aura.y += self.velocidad_y
        self.velocidad_y += self.__gravedad
        if self.velocidad_y > 20:
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
        if tiempo - self.tiempo_ultimo_sprite > self.tiempo_entre_sprites:
            self.tiempo_ultimo_sprite = tiempo
            self.indice_sprite += 1
                # Actualizar la dirección de la animación
        if self.rectan.x > otro_jugador.rectan.x:
            self.espejado = True
        else:
            self.espejado = False
        # Cambiar la animación según la dirección
        if self.espejado:
            self.animaciones = self.animaciones_espejadas
        else:
            self.animaciones = self.cargar_animaciones(False)
        # Asegurarse de que el índice del sprite esté dentro del rango
        if self.indice_sprite >= len(self.animaciones[self.animacion_actual]):
            self.indice_sprite = 0
        self.imagen = self.animaciones[self.animacion_actual][self.indice_sprite]
    
    def manejar_saltos(self, teclas, salto):
        if teclas[salto] and self.en_plataforma:
            self.velocidad_y = -self.fuerza_salto
            self.en_plataforma = False

    def bajar_salud(self, dano, cantidad_retroceso, dirección):
        self.salud -= dano
        if self.salud <= 0:
            if self.vidas == 2:
                self.perder_vida()
            else:
                self.salud = 0
                return True
        # Aplicar retroceso basado en la dirección del ataque
        self.retroceso_x = cantidad_retroceso[0] * dirección
        self.retroceso_y = cantidad_retroceso[1]
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
        # Dibujar la barra de margen detrás de todas las barras de vida
        imagen_margen = pygame.transform.scale(self.imagen_barra_margen, (ancho_barra + 61, alto_barra + 20))
        if espejo:
            imagen_margen = pygame.transform.flip(imagen_margen, True, False)
            pantalla.blit(imagen_margen, (posicion[0] - ancho_barra - 29, 0))
        else:
            pantalla.blit(imagen_margen, (-22,0))

        if self.vidas == 2:
            # Primera barra de vida completa
            progreso_ancho = self.salud
            progreso = pygame.transform.scale(self.imagen_primera_vida, (progreso_ancho, alto_barra))
            progreso_barra2 = pygame.transform.scale(self.imagen_segunda_vida, (ancho_barra, alto_barra))
            if espejo:
                progreso_barra2 = pygame.transform.flip(progreso_barra2, True, False)
                progreso = pygame.transform.flip(progreso, True, False)
                pantalla.blit(progreso_barra2, (posicion[0] - ancho_barra, posicion[1]))
                pantalla.blit(progreso, (posicion[0] - progreso_ancho, posicion[1]))
            else:
                pantalla.blit(progreso_barra2, posicion)
                pantalla.blit(progreso, posicion)
        elif self.vidas == 1:
            # Segunda barra de vida
            progreso_ancho = self.salud
            progreso = pygame.transform.scale(self.imagen_segunda_vida, (progreso_ancho, alto_barra))
            if espejo:
                progreso = pygame.transform.flip(progreso, True, False)
                pantalla.blit(progreso, (posicion[0] - progreso_ancho, posicion[1]))
            else:
                pantalla.blit(progreso, posicion)

    def dibujar_ataque_especial(self, posicion, espejo=False):
        ancho_barra = 200
        alto_barra = 15
        progreso_ancho = self.ataque_especial
        # Dibujar la barra de margen detrás de la barra de ataque especial
        imagen_margen = pygame.transform.scale(self.imagen_barra_margen, (ancho_barra + 26, alto_barra + 9))
        if espejo:
            imagen_margen = pygame.transform.flip(imagen_margen, True, False)
            pantalla.blit(imagen_margen, (posicion[0] - ancho_barra - 12, posicion[1] - 4))
        else:
            pantalla.blit(imagen_margen, (-4, 46))
        progreso = pygame.transform.scale(self.imagen_barra_ataque, (progreso_ancho, alto_barra))
        if espejo:
            progreso = pygame.transform.flip(progreso, True, False)
            pantalla.blit(progreso, (posicion[0] - progreso_ancho, posicion[1]))
        else:
            pantalla.blit(progreso, posicion)

    def disparar_proyectil(self, otro_jugador):
        direccion = 1 if self.rectan.x < otro_jugador.rectan.x else -1
        velocidad = 20
        espejo = True if direccion < 0 else False
        posicion = (self.rectan.x + 5,self.rectan.y + 50)
        proyectil = Proyectil(posicion, velocidad, direccion, espejo)
        self.proyectiles.append(proyectil)

    def actualizar_proyectiles(self):
        for proyectil in self.proyectiles:
            proyectil.actualizar()

    def dibujar_proyectiles(self):
        for proyectil in self.proyectiles:
            proyectil.dibujar()

class Samurai(Jugador):
    def __init__(self, rectan, aura):
        super().__init__(rectan, aura, velocidad=13, fuerza_salto=15)
        self.cooldown_inicial = 600
        self.saltos_maximos = 2
        self.dobles_saltos_restantes = self.saltos_maximos
        self.tiempo_ultimo_salto = 0
        self.espejado = False
        self.animacion_actual = "idle"
        self.animaciones = self.cargar_animaciones(False)
        self.animaciones_espejadas = self.cargar_animaciones(True)
        self.indice_sprite = 0
        self.imagen = self.animaciones[self.animacion_actual][self.indice_sprite]
        self.tiempo_ultimo_sprite = pygame.time.get_ticks()
        self.tiempo_entre_sprites = 70  # Milisegundos entre cada frame de la animación
    
    def cargar_animaciones(self, espejo):
        return {
            "idle": [pintar_superficie(sprite, color_tinte1) for sprite in cargar_sprites(pygame.image.load('assets/anims/samurai/idle_samurai.png').convert_alpha(), 10, 107.6, 140, fondo_samurai, espejo)],
            "run": [pintar_superficie(sprite, color_tinte1) for sprite in cargar_sprites(pygame.image.load('assets/anims/samurai/caminar_samurai.png').convert_alpha(), 8, 110, 140, fondo_samurai, espejo)],
            "run_b": [pintar_superficie(sprite, color_tinte1) for sprite in cargar_sprites(pygame.image.load('assets/anims/samurai/caminata_atras_samurai.png').convert_alpha(), 8, 110, 140, fondo_samurai, espejo)],
            "jump": [pintar_superficie(sprite, color_tinte1) for sprite in cargar_sprites(pygame.image.load('assets/anims/samurai/salto_samurai.png').convert_alpha(), 5, 108.2, 140, fondo_samurai, espejo)],
            "attack": [pintar_superficie(sprite, color_tinte1) for sprite in cargar_sprites(pygame.image.load('assets/anims/samurai/ataque_samurai.png').convert_alpha(), 5, 140, 140, fondo_samurai, espejo)],
            "attack_s": [pintar_superficie(sprite, color_tinte1) for sprite in cargar_sprites(pygame.image.load('assets/anims/samurai/ataque_especial_samurai.png').convert_alpha(), 12, 160, 140, fondo_samurai, espejo)],
            "defense": [pintar_superficie(sprite, color_tinte1) for sprite in cargar_sprites(pygame.image.load('assets/anims/samurai/bloqueo_samurai.png').convert_alpha(), 1, 90, 140, fondo_samurai, espejo)],
            'hit': [pintar_superficie(sprite, color_tinte1) for sprite in cargar_sprites(pygame.image.load('assets/anims/samurai/dañado_samurai.png').convert_alpha(), 5, 121.6, 140, fondo_samurai, espejo)],
            'shoot': [pintar_superficie(sprite, color_tinte1) for sprite in cargar_sprites(pygame.image.load('assets/anims/samurai/disparo_samurai.png').convert_alpha(), 7, 195, 140, fondo_samurai, espejo)],
            'intro_vict': [pintar_superficie(sprite, color_tinte1) for sprite in cargar_sprites(pygame.image.load('assets/anims/samurai/victoria_samurai.png').convert_alpha(), 3, 90, 140, fondo_samurai, espejo)],
            'death': [pintar_superficie(sprite, color_tinte1) for sprite in cargar_sprites(pygame.image.load('assets/anims/samurai/muerte_samurai.png').convert_alpha(), 9, 155, 120, fondo_samurai, espejo)]
        }
    
    def manejar_saltos(self, teclas, salto):
        tiempo_actual = pygame.time.get_ticks()
        if teclas[salto]: 
            if self.dobles_saltos_restantes > 0 and (tiempo_actual - self.tiempo_ultimo_salto >= 500):
                self.velocidad_y = -self.fuerza_salto
                self.dobles_saltos_restantes -= 1
                self.tiempo_ultimo_salto = tiempo_actual
                if self.rectan.bottom > plataforma.top - 5:
                    self.en_plataforma = False
    
    def actualizar(self, teclas, izq, derecha, salto, defensa, ataque, ataque_s, ataque_p, emote, otro_jugador):
        super().actualizar(teclas, izq, derecha, salto, defensa, ataque, ataque_s,ataque_p,  emote, otro_jugador)
        if self.en_plataforma:
            self.dobles_saltos_restantes = self.saltos_maximos

class Hanzo(Jugador):
    def __init__(self, rectan, aura):
        super().__init__(rectan, aura, velocidad=9, fuerza_salto=19)
        self.cooldown_inicial = 1000
        self.espejado = False
        self.animacion_actual = "idle"
        self.animaciones = self.cargar_animaciones(False)
        self.animaciones_espejadas = self.cargar_animaciones(True)
        self.indice_sprite = 0
        self.imagen = self.animaciones[self.animacion_actual][self.indice_sprite]
        self.tiempo_ultimo_sprite = pygame.time.get_ticks()
        self.tiempo_entre_sprites = 130  # Milisegundos entre cada frame de la animación

    def cargar_animaciones(self, espejo):
        return {
            "idle": [pintar_superficie(sprite, color_tinte2) for sprite in cargar_sprites(pygame.image.load('assets/anims/hanzo/Idle_Hanzo.png').convert_alpha(), 10, 100, 118, fondo_hanzo, espejo)],
            "run": [pintar_superficie(sprite, color_tinte2) for sprite in cargar_sprites(pygame.image.load('assets/anims/hanzo/caminata_Hanzo.png').convert_alpha(), 10, 110, 120, fondo_hanzo, espejo)],
            "run_b": [pintar_superficie(sprite, color_tinte2) for sprite in cargar_sprites(pygame.image.load('assets/anims/hanzo/caminataparaatras_Hanzo.png').convert_alpha(), 10, 100, 130, fondo_hanzo, espejo)],
            "jump": [pintar_superficie(sprite, color_tinte2) for sprite in cargar_sprites(pygame.image.load('assets/anims/hanzo/salto_Hanzo.png').convert_alpha(), 6, 80, 150, fondo_hanzo, espejo)],
            "attack": [pintar_superficie(sprite, color_tinte2) for sprite in cargar_sprites(pygame.image.load('assets/anims/hanzo/ataque_Hanzo.png').convert_alpha(), 6, 140, 120, fondo_hanzo, espejo)],
            "attack_s": [pintar_superficie(sprite, color_tinte2) for sprite in cargar_sprites(pygame.image.load('assets/anims/hanzo/ataquespecial_Hanzo.png').convert_alpha(), 10, 130, 140, fondo_hanzo, espejo)],
            "defense": [pintar_superficie(sprite, color_tinte2) for sprite in cargar_sprites(pygame.image.load('assets/anims/hanzo/bloqueo_Hanzo.png').convert_alpha(), 1, 110, 120, fondo_hanzo, espejo)],
            'hit': [pintar_superficie(sprite, color_tinte2) for sprite in cargar_sprites(pygame.image.load('assets/anims/hanzo/daño_Hanzo.png').convert_alpha(), 2, 110, 120, fondo_hanzo, espejo)],
            'shoot': [pintar_superficie(sprite, color_tinte2) for sprite in cargar_sprites(pygame.image.load('assets/anims/hanzo/ataquep_Hanzo.png').convert_alpha(), 5, 155, 120, fondo_hanzo, espejo)],
            'intro_vict': [pintar_superficie(sprite, color_tinte2) for sprite in cargar_sprites(pygame.image.load('assets/anims/hanzo/victoria_Hanzo.png').convert_alpha(), 6, 86, 120, fondo_hanzo, espejo)],
            'death': [pintar_superficie(sprite, color_tinte2) for sprite in cargar_sprites(pygame.image.load('assets/anims/hanzo/muerte_Hanzo.png').convert_alpha(), 9, 130, 110, fondo_hanzo, espejo)]
        }

    def disparar_proyectil(self, otro_jugador):
        direccion = 1 if self.rectan.x < otro_jugador.rectan.x else -1
        espejo = True if direccion < 0 else False
        velocidad = 25
        proyectil1 = Proyectil((self.rectan.centerx -20, self.rectan.centery), velocidad, direccion, espejo)
        proyectil2 = Proyectil((self.rectan.centerx, self.rectan.centery - 30), velocidad, direccion, espejo)
        self.proyectiles.append(proyectil1)
        self.proyectiles.append(proyectil2)

class Proyectil:
    def __init__(self, posicion, velocidad, direccion, espejo=False):
        self.rect = pygame.Rect(posicion, (70, 10))
        self.velocidad = velocidad
        self.direccion = direccion
        self.espejo = espejo
        self.animacion_actual = "disparo"
        self.animaciones = {
            "disparo": [pintar_superficie(sprite, color_tinte_proyectil) for sprite in cargar_sprites(pygame.image.load('assets/anims/hanzo/proyectil_Hanzo.png').convert_alpha(), 1, 60, 30, fondo_hanzo, espejo)],
        }
        self.sprite_index = 0
        self.image = self.animaciones[self.animacion_actual][self.sprite_index]
        self.tiempo_ultimo_sprite = pygame.time.get_ticks()
        self.tiempo_entre_sprites = 4000  # Milisegundos entre cada frame de la animación

    def actualizar(self):
        self.rect.x += self.velocidad * self.direccion

    def dibujar(self):
        imagen_actual = self.animaciones[self.animacion_actual][self.sprite_index]
        pantalla.blit(imagen_actual, self.rect.topleft)