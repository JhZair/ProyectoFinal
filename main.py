import pygame
import sys
from menu import mostrar_menu

# Inicializar Pygame
pygame.init()

# Configuración de la pantalla
pantalla_ancho = 1700
pantalla_alto = 1000
pantalla = pygame.display.set_mode((pantalla_ancho, pantalla_alto))
pygame.display.set_caption("Pelea de dioses")

# Colores
blanco = (255, 255, 255)
negro = (0, 0, 0)
gris = (117, 117, 117)
amarillo = (255, 233, 0)
naranja = (255, 165, 0)
celeste = (0, 170, 228)
verde_transparente = (0, 255, 0, 128)
verde_vd = (1, 233, 12)
amarillos_ps = (255, 243, 78)
fondo_hanzo = (64,176,72)

# Configuración del reloj
reloj = pygame.time.Clock()

# Fuente para el temporizador
fuente = pygame.font.Font(None, 74)

# Duración de la partida en segundos
duracion_partida = 120
inicio_tiempo = pygame.time.get_ticks()

# Plataforma
plataforma = pygame.Rect(200, 550, pantalla_ancho - 400, 200)

def cargar_sprites(hoja, num_sprites, ancho_sprite, alto_sprite, color, espejo=False):
    sprites = []
    for i in range(num_sprites):
        sprite = hoja.subsurface(pygame.Rect(i * ancho_sprite, 0, ancho_sprite, alto_sprite))
        sprite.set_colorkey(color)
        if espejo:
            sprite = pygame.transform.flip(sprite, True, False)  # Espejo horizontal
        sprites.append(sprite)
    return sprites

class Jugador:
    def __init__(self, color, rectan, aura, velocidad=5, fuerza_salto=15, cooldown_inicial=1500):
        self.rectan = rectan
        self.aura = aura
        self.velocidad = velocidad
        self.velocidad_inicial = velocidad
        self.fuerza_salto = fuerza_salto
        self.gravedad = 1.3
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
        self.animaciones = self.cargar_animaciones(False)
        self.animaciones_espejadas = self.cargar_animaciones(True)
        # Animaciones
        self.animacion_actual = "idle"
        self.indice_sprite = 0
        self.imagen = self.animaciones[self.animacion_actual][self.indice_sprite]
        self.tiempo_ultimo_sprite = pygame.time.get_ticks()
        self.tiempo_entre_sprites = 75  # Milisegundos entre cada frame de la animación
    def cargar_animaciones(self, espejo):
        return {
            "idle": cargar_sprites(pygame.image.load('assets/anims/hanzo/Idle_Hanzo.png').convert_alpha(), 10, 100, 118, fondo_hanzo, espejo),
            "run": cargar_sprites(pygame.image.load('assets/anims/hanzo/caminata_Hanzo.png').convert_alpha(), 10, 110, 120, fondo_hanzo, espejo),
            "run_b": cargar_sprites(pygame.image.load('assets/anims/hanzo/caminataparaatras_Hanzo.png').convert_alpha(), 10, 100, 120, fondo_hanzo, espejo),
            "jump": cargar_sprites(pygame.image.load('assets/anims/hanzo/salto_Hanzo.png').convert_alpha(), 6, 80, 150, fondo_hanzo, espejo),
            "attack": cargar_sprites(pygame.image.load('assets/anims/hanzo/ataque_Hanzo.png').convert_alpha(), 6, 140, 120, fondo_hanzo, espejo),
            "defense": cargar_sprites(pygame.image.load('assets/anims/hanzo/bloqueo_Hanzo.png').convert_alpha(), 1, 110, 120, fondo_hanzo, espejo),
            'hit': cargar_sprites(pygame.image.load('assets/anims/hanzo/daño_Hanzo.png').convert_alpha(), 2, 100, 110, fondo_hanzo, espejo),
            'shoot': cargar_sprites(pygame.image.load('assets/anims/hanzo/ataquep_Hanzo.png').convert_alpha(), 5, 155, 120, fondo_hanzo, espejo),
            'death': cargar_sprites(pygame.image.load('assets/anims/hanzo/muerte_Hanzo.png').convert_alpha(), 9, 130, 110, fondo_hanzo, espejo)
        }


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

    def bajar_salud(self, dano, direccion_retroceso):
        self.salud -= dano
        if self.salud <= 0:
            self.salud = 0
            return True
        # Aplicar retroceso basado en la dirección del ataque
        self.retroceso_x = direccion_retroceso[0]
        self.retroceso_y = direccion_retroceso[1]
        
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

class Juego:
    def __init__(self):
        self.jugador1 = Jugador(amarillo, pygame.Rect(pantalla_ancho // 2 - 250, 500, 80, 120), pygame.Rect(pantalla_ancho // 2 - 270, 380, 70, 120))
        self.jugador2 = Jugador(naranja, pygame.Rect(pantalla_ancho // 2 + 220, 500, 80, 120), pygame.Rect(pantalla_ancho // 2 + 200, 380, 70, 120))
        self.ejecutando = True
        # Cargar la imagen de fondo
        self.fondo = pygame.image.load("assets/images/img3.jpeg")
        self.fondo = pygame.transform.scale(self.fondo, (pantalla_ancho, pantalla_alto))

    def comprobar_colisiones_y_ataques(self, teclas, ataque_j1, ataque_j2, ataque_especial_j1, ataque_especial_j2):
        tiempo_actual = pygame.time.get_ticks()
        if teclas[ataque_j1] and tiempo_actual > self.jugador1.cooldown:
            if self.jugador1.aura.colliderect(self.jugador2.rectan) and teclas[ataque_j1] and tiempo_actual > self.jugador1.cooldown and not self.jugador1.defendiendo:
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
            self.jugador1.cooldown = tiempo_actual + 1000

        if teclas[ataque_j2] and tiempo_actual > self.jugador2.cooldown:
            if self.jugador2.aura.colliderect(self.jugador1.rectan) and teclas[ataque_j2] and tiempo_actual > self.jugador2.cooldown and not self.jugador2.defendiendo:
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
            self.jugador2.cooldown = tiempo_actual + 1000

        # Comprobar ataques especiales
        if teclas[ataque_especial_j1] and self.jugador1.ataque_especial == 200 and not self.jugador1.defendiendo:
            self.jugador1.ataque_especial = 0
            direccion_retroceso = (20, -10)
            if self.jugador2.bajar_salud(50, direccion_retroceso):
                print("Jugador 2 ha sido derrotado")
                return True

        if teclas[ataque_especial_j2] and self.jugador2.ataque_especial == 200 and not self.jugador2.defendiendo:
            self.jugador2.ataque_especial = 0
            direccion_retroceso = (-20, -10)
            if self.jugador1.bajar_salud(50, direccion_retroceso):
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
                self.jugador1.actualizar(teclas, pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_s, pygame.K_r, self.jugador2, self.jugador1)
                self.jugador2.actualizar(teclas, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN, pygame.K_i, self.jugador1, self.jugador2)

                # Comprobar colisiones entre las auras y los jugadores, y ataques
                if self.comprobar_colisiones_y_ataques(teclas, pygame.K_r, pygame.K_i, pygame.K_t, pygame.K_o):
                    self.ejecutando = False
                
                 # Dibujar la imagen de fondo
                pantalla.blit(self.fondo, (0, 0))

                # Dibujar todo en la pantalla
                pantalla.blit(self.jugador1.imagen, self.jugador1.rectan.topleft)
                pantalla.blit(self.jugador2.imagen, self.jugador2.rectan.topleft)
                pygame.draw.rect(pantalla, gris, plataforma)

                # Dibujar las auras para visualización (opcional)
                # pygame.draw.rect(pantalla, verde_transparente, self.jugador1.aura)
                # pygame.draw.rect(pantalla, verde_transparente, self.jugador2.aura)

                # Dibujar la salud de los jugadores
                self.jugador1.dibujar_barra_salud((10, 10))
                self.jugador2.dibujar_barra_salud((pantalla_ancho - 10, 10), espejo=True)

                # Dibujar la barra de ataque especial
                self.jugador1.dibujar_ataque_especial((10, 50))
                self.jugador2.dibujar_ataque_especial((pantalla_ancho - 10, 50), espejo=True)

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
# Falta arreglar ataque a distancia;  solucionar bug al pegarse a la plataforma por los costados; faltan agregar personajes distintos con características diferentes;
# evento de muerte al caer de la plataforma; agregar dos vidas para cada jugador.
# Animaciones:
# Continuar añadiendo animaciones distintas para cada personaje; hacer para que las animaciones tengan su espejo; corregir las imágenes de las animaciones
# cambiar animación de bloqueo de samurai 
# Interfaces:
# Interfaz de selección de personajes; mejorar interfaz de inicio del juego; agregar interfaz de pausa; mejorar las barras de vida, contadores y fuentes
# General:
# Falta contador inicial para iniciar el juego; falta pantalla final al ganar un jugador; dividir las funcionalidades por archivos; agregar imagen a plataforma;
# agregar efectos de sonido y música de fondo.