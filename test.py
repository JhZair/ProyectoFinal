import pygame
import sys
from config import *
import pygame.locals
from menu import mostrar_menu
from arena import plataforma, imagen_plataforma
from peleadores import Samurai, Hanzo

# Inicializar Pygame
pygame.init()

# Configuración de la pantalla

pygame.display.set_caption("God's Fight")

# Colores
blanco = (255, 255, 255)

# Configuración del reloj
reloj = pygame.time.Clock()

# Fuente para el temporizador
fuente = pygame.font.Font(None, 74)

# Duración de la partida en segundos
duracion_partida = 120
inicio_tiempo = pygame.time.get_ticks()
        
class Juego:
    def __init__(self):
        self.jugador1 = Samurai(pygame.Rect(pantalla_ancho // 2 - 240, 550, 80, 130), pygame.Rect(pantalla_ancho // 2 - 240, 200, 115, 130))
        self.jugador2 = Hanzo(pygame.Rect(pantalla_ancho // 2 + 240, 550, 80, 115), pygame.Rect(pantalla_ancho // 2 + 240, 200, 115, 115))
        self.ejecutando = True
        # Cargar la imagen de fondo
        self.fondo = pygame.image.load("assets/images/img1.jpeg")
        self.fondo = pygame.transform.scale(self.fondo, (pantalla_ancho, pantalla_alto))

    def comprobar_colisiones_y_ataques(self, teclas, ataque_j1, ataque_j2, ataque_especial_j1, ataque_especial_j2, proyectil_j1, proyectil_j2):
        tiempo_actual = pygame.time.get_ticks()
        direccionj1 = 1 if self.jugador1.rectan.x < self.jugador2.rectan.x else -1
        direccionj2 = 1 if self.jugador2.rectan.x > self.jugador1.rectan.x else -1
        if teclas[ataque_j1] and tiempo_actual > self.jugador1.cooldown:
            if self.jugador1.aura.colliderect(self.jugador2.aura) and teclas[ataque_j1] and tiempo_actual > self.jugador1.cooldown and not self.jugador1.defendiendo:
                self.jugador1.incrementar_ataque_especial(50)
                cantidad_retroceso = (20, -15)
                if self.jugador2.defendiendo:
                    if self.jugador2.bajar_salud(10, cantidad_retroceso, direccionj1):
                        print("Jugador 2 ha sido derrotado")
                        return True
                else:
                    if self.jugador2.bajar_salud(30, cantidad_retroceso, direccionj1):
                        print("Jugador 2 ha sido derrotado")
                        return True
            self.jugador1.cooldown = tiempo_actual + self.jugador1.cooldown_inicial

        if teclas[ataque_j2] and tiempo_actual > self.jugador2.cooldown:
            if self.jugador2.aura.colliderect(self.jugador1.aura) and teclas[ataque_j2] and tiempo_actual > self.jugador2.cooldown and not self.jugador2.defendiendo:
                self.jugador2.incrementar_ataque_especial(50)
                cantidad_retroceso = (-20, -15)
                if self.jugador1.defendiendo:
                    if self.jugador1.bajar_salud(10, cantidad_retroceso,direccionj2):
                        print("Jugador 1 ha sido derrotado")
                        return True
                else:
                    if self.jugador1.bajar_salud(30, cantidad_retroceso, direccionj2):
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
        if teclas[ataque_especial_j1] and self.jugador1.ataque_especial == 200 and self.jugador1.aura.colliderect(self.jugador2.rectan):
            self.jugador1.ataque_especial = 0
            cantidad_retroceso = (30, -15)
            if self.jugador2.bajar_salud(50, cantidad_retroceso, direccionj1):
                print("Jugador 2 ha sido derrotado")
                return True

        if teclas[ataque_especial_j2] and self.jugador2.ataque_especial == 200 and self.jugador2.aura.colliderect(self.jugador1.rectan):
            self.jugador2.ataque_especial = 0
            cantidad_retroceso = (-20, -10)
            if self.jugador1.bajar_salud(50, cantidad_retroceso, direccionj2):
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
                if self.jugador2.bajar_salud(20, (20, -15), direccionj1):
                    print("Jugador 2 ha sido derrotado")
                    return True

        for proyectil in self.jugador2.proyectiles:
            if proyectil.rect.colliderect(self.jugador1.rectan):
                self.jugador2.proyectiles.remove(proyectil)
                if self.jugador1.bajar_salud(20, (-20, -15), direccionj2):
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
                self.jugador1.actualizar(teclas, pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_s, pygame.K_r,pygame.K_t, pygame.K_y, self.jugador2)
                self.jugador2.actualizar(teclas, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN, pygame.K_i, pygame.K_o, pygame.K_p, self.jugador1)

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

# Animaciones:
# terminar de añadir animaciones para Hanzo y samurai(ataques fuerte y distancia); mejorar animación de bloqueo de samurai; 
# Interfaces:
# Interfaz de selección de personajes; mejorar interfaz de inicio del juego; agregar interfaz de pausa; mejorar las barras de vida, contadores y fuentes;
# General:
# Falta contador inicial para iniciar el juego; falta pantalla final al ganar un jugador; dividir las funcionalidades por archivos;
# agregar efectos de sonido y música de fondo.