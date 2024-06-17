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

# Configuración del reloj
reloj = pygame.time.Clock()

# Fuente para el temporizador
fuente = pygame.font.Font(None, 74)

# Duración de la partida en segundos
duracion_partida = 120
inicio_tiempo = pygame.time.get_ticks()

# Plataforma
plataforma = pygame.Rect(200, 550, pantalla_ancho - 400, 200)

class Jugador:
    def __init__(self, color, rectan, aura, velocidad=5, fuerza_salto=10, gravedad=0.7):
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

    def actualizar(self, teclas, izq, derecha, salto, defensa, otro_jugador):
        if teclas[izq]:
            self.rectan.x -= self.velocidad
            self.aura.x -= self.velocidad
        if teclas[derecha]:
            self.rectan.x += self.velocidad
            self.aura.x += self.velocidad

        if teclas[salto] and self.en_plataforma:
            self.velocidad_y = -self.fuerza_salto
            self.en_plataforma = False

        # Aplicar gravedad
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
        else:
            self.velocidad = 5

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

class Juego:
    def __init__(self):
        self.jugador1 = Jugador(amarillo, pygame.Rect(pantalla_ancho // 2 - 250, 500, 30, 80), pygame.Rect(pantalla_ancho // 2 - 270, 380, 70, 120))
        self.jugador2 = Jugador(naranja, pygame.Rect(pantalla_ancho // 2 + 220, 500, 30, 80), pygame.Rect(pantalla_ancho // 2 + 200, 380, 70, 120))
        self.ejecutando = True
        # Cargar la imagen de fondo
        self.fondo = pygame.image.load("assets/images/img3.jpeg")
        self.fondo = pygame.transform.scale(self.fondo, (pantalla_ancho, pantalla_alto))

    def comprobar_colisiones_y_ataques(self, teclas, ataque_j1, ataque_j2, ataque_especial_j1, ataque_especial_j2):
        tiempo_actual = pygame.time.get_ticks()

        if self.jugador1.aura.colliderect(self.jugador2.rectan) and teclas[ataque_j1] and tiempo_actual > self.jugador1.cooldown and not self.jugador1.defendiendo:
            self.jugador1.cooldown = tiempo_actual + 1000
            self.jugador1.incrementar_ataque_especial(50)
            if self.jugador2.defendiendo:
                if self.jugador2.bajar_salud(10):
                    print("Jugador 2 ha sido derrotado")
                    return True
            else:
                if self.jugador2.bajar_salud(30):
                    print("Jugador 2 ha sido derrotado")
                    return True

        if self.jugador2.aura.colliderect(self.jugador1.rectan) and teclas[ataque_j2] and tiempo_actual > self.jugador2.cooldown and not self.jugador2.defendiendo:
            self.jugador2.cooldown = tiempo_actual + 1000
            self.jugador2.incrementar_ataque_especial(50)
            if self.jugador1.defendiendo:
                if self.jugador1.bajar_salud(10):
                    print("Jugador 1 ha sido derrotado")
                    return True
            else:
                if self.jugador1.bajar_salud(30):
                    print("Jugador 1 ha sido derrotado")
                    return True

        # Comprobar ataques especiales
        if teclas[ataque_especial_j1] and self.jugador1.ataque_especial == 200 and not self.jugador1.defendiendo:
            self.jugador1.ataque_especial = 0
            if self.jugador2.bajar_salud(50):
                print("Jugador 2 ha sido derrotado")
                return True

        if teclas[ataque_especial_j2] and self.jugador2.ataque_especial == 200 and not self.jugador2.defendiendo:
            self.jugador2.ataque_especial = 0
            if self.jugador1.bajar_salud(50):
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
                self.jugador1.actualizar(teclas, pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_s, self.jugador2)
                self.jugador2.actualizar(teclas, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN, self.jugador1)

                # Comprobar colisiones entre las auras y los jugadores, y ataques
                if self.comprobar_colisiones_y_ataques(teclas, pygame.K_r, pygame.K_i, pygame.K_t, pygame.K_o):
                    self.ejecutando = False
                
                 # Dibujar la imagen de fondo
                pantalla.blit(self.fondo, (0, 0))

                # Dibujar todo en la pantalla
                #pantalla.fill(celeste)
                pygame.draw.rect(pantalla, self.jugador1.color, self.jugador1.rectan)
                pygame.draw.rect(pantalla, self.jugador2.color, self.jugador2.rectan)
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

## Falta agregar ataque a distancia, evento de muerte al caer de la plataforma, solucionar bug al pegarse a la plataforma por los costados,
# falta contador inicial para iniciar el juego, falta pantalla final al ganar un jugador o quedar en empate o por tiempo, faltan agregar personajes distintos con
# características diferentes, interfaz de inicio del juego, interfaz de pausa, interfaz de selección de personajes, añadir animaciones distintas para cada personaje,
# agregar dos vidas para cada jugador, agregar mecánica de empuje al recibir daño y agregar efectos de sonifo y música de fondo.