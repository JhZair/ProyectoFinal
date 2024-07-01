import pygame
import sys
from config import *
import pygame.locals
from menu import mostrar_menu
from arena import plataforma, imagen_plataforma
from peleadores import Samurai, Hanzo

# Inicializar Pygame
pygame.init()

pygame.mixer.init()

# Configuración de la pantalla

pygame.display.set_caption(nombre_juego)

# Configuración del reloj
reloj = pygame.time.Clock()

# Fuente para el temporizador
fuente = pygame.font.Font("assets/fonts/upheavtt.ttf", 60)

# Duración de la partida en segundos
duracion_partida = 360
inicio_tiempo = pygame.time.get_ticks()
        
class Juego:
    def __init__(self):
        self.reiniciar_jugadores()
        self.ejecutando = True
        # Cargar la imagen de fondo
        self.fondo = pygame.image.load("assets/images/img1.jpeg")
        self.fondo = pygame.transform.scale(self.fondo, (pantalla_ancho, pantalla_alto))

    def reiniciar_jugadores(self):
        self.jugador1 = Samurai(pygame.Rect(pantalla_ancho // 2 - 240, 550, 80, 130), pygame.Rect(pantalla_ancho // 2 - 240, 200, 115, 130))
        self.jugador2 = Hanzo(pygame.Rect(pantalla_ancho // 2 + 240, 550, 80, 115), pygame.Rect(pantalla_ancho // 2 + 240, 200, 115, 115))

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
                        self.mostrar_ganador("Jugador 1")
                        return True
                else:
                    if self.jugador2.bajar_salud(30, cantidad_retroceso, direccionj1):
                        print("Jugador 2 ha sido derrotado")
                        self.mostrar_ganador("Jugador 1")
                        return True
            self.jugador1.cooldown = tiempo_actual + self.jugador1.cooldown_inicial

        if teclas[ataque_j2] and tiempo_actual > self.jugador2.cooldown:
            if self.jugador2.aura.colliderect(self.jugador1.aura) and teclas[ataque_j2] and tiempo_actual > self.jugador2.cooldown and not self.jugador2.defendiendo:
                self.jugador2.incrementar_ataque_especial(50)
                cantidad_retroceso = (-20, -15)
                if self.jugador1.defendiendo:
                    if self.jugador1.bajar_salud(10, cantidad_retroceso,direccionj2):
                        print("Jugador 1 ha sido derrotado")
                        self.mostrar_ganador("Jugador 2")
                        return True
                else:
                    if self.jugador1.bajar_salud(30, cantidad_retroceso, direccionj2):
                        print("Jugador 1 ha sido derrotado")
                        self.mostrar_ganador("Jugador 2")
                        return True
            self.jugador2.cooldown = tiempo_actual + self.jugador2.cooldown_inicial

        # Verificar si el jugador cae fuera de la pantalla
        if self.jugador1.rectan.top > pantalla_alto:
            if self.jugador1.vidas == 2:
                self.jugador1.perder_vida()
            else:
                print("Jugador 1 ha sido derrotado")
                self.mostrar_ganador("Jugador 2")
                return True
            
        if self.jugador2.rectan.top > pantalla_alto:
            if self.jugador2.vidas == 2:
                self.jugador2.perder_vida()
            else:
                print("Jugador 2 ha sido derrotado")
                self.mostrar_ganador("Jugador 1")
                return True

        # Comprobar ataques especiales
        if teclas[ataque_especial_j1] and self.jugador1.ataque_especial == 200 and self.jugador1.aura.colliderect(self.jugador2.rectan):
            self.jugador1.ataque_especial = 0
            cantidad_retroceso = (30, -15)
            if self.jugador2.bajar_salud(50, cantidad_retroceso, direccionj1):
                print("Jugador 2 ha sido derrotado")
                self.mostrar_ganador("Jugador 1")
                return True

        if teclas[ataque_especial_j2] and self.jugador2.ataque_especial == 200 and self.jugador2.aura.colliderect(self.jugador1.rectan):
            self.jugador2.ataque_especial = 0
            cantidad_retroceso = (-20, -10)
            if self.jugador1.bajar_salud(50, cantidad_retroceso, direccionj2):
                print("Jugador 1 ha sido derrotado")
                self.mostrar_ganador("Jugador 2")
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
                self.jugador2.animacion_actual = "hit"
                self.jugador2.cooldown_animacion = tiempo_actual + 300
                self.jugador1.proyectiles.remove(proyectil)
                if self.jugador2.bajar_salud(20, (20, -15), direccionj1) and self.jugador2.vidas < 1:
                    print("Jugador 2 ha sido derrotado")
                    self.mostrar_ganador("Jugador 1")
                    return True
            if proyectil.rect.x > pantalla_ancho or proyectil.rect.x < 0:
                self.jugador1.proyectiles.remove(proyectil)

        for proyectil in self.jugador2.proyectiles:
            if proyectil.rect.colliderect(self.jugador1.rectan):
                self.jugador1.animacion_actual = "hit"
                self.jugador1.cooldown_animacion = tiempo_actual + 300
                self.jugador2.proyectiles.remove(proyectil)
                if self.jugador1.bajar_salud(20, (-20, -15), direccionj2) and self.jugador1.vidas < 1:
                    print("Jugador 1 ha sido derrotado")
                    self.mostrar_ganador("Jugador 2")
                    return True
            if proyectil.rect.x > pantalla_ancho or proyectil.rect.x < 0:
                self.jugador2.proyectiles.remove(proyectil)
        return False
    
    def dibujar_tiempo_restante(self, tiempo_restante):
        minutos = tiempo_restante // 60
        segundos = tiempo_restante % 60
        texto_tiempo = fuente.render(f"{minutos:02}:{segundos:02}", True, (0,0,0))
        pantalla.blit(texto_tiempo, (pantalla_ancho // 2 - texto_tiempo.get_width() // 2, 10))

    def ganador_por_tiempo(self):
        if self.jugador1.salud > self.jugador2.salud:
            print("Jugador 1 gana por salud")
            self.mostrar_ganador("Jugador 1")
            self.jugador1.animacion_actual = "intro_vict"
        elif self.jugador2.salud > self.jugador1.salud:
            print("Jugador 2 gana por salud")
            self.mostrar_ganador("Jugador 2")
        else:
            print("Empate")
    
    def mostrar_ganador(self, ganador):
        fuente_ganador = pygame.font.Font("assets/fonts/upheavtt.ttf", 80)
        texto_ganador = fuente_ganador.render(f"{ganador} gana!", True, (255, 255, 255))
        rect_texto = texto_ganador.get_rect(center=(pantalla_ancho // 2, pantalla_alto // 2 - 50))
        pantalla.blit(texto_ganador, rect_texto)
        pygame.display.flip()
        pygame.time.delay(5000)  # Esperar 5 segundos
        self.ejecutando = False  # Terminar el bucle del juego

    def mostrar_contador(self):
        fuente_contador = pygame.font.Font("assets/fonts/upheavtt.ttf", 80)
        fuente_peleen = pygame.font.Font("assets/fonts/upheavtt.ttf", 150)
        for i in range(5, 0, -1):
            pantalla.fill((0, 0, 0))
            texto = fuente_contador.render(str(i), True, (255, 255, 255))
            rect_texto = texto.get_rect(center=(pantalla_ancho // 2, pantalla_alto // 2))
            pantalla.blit(texto, rect_texto)
            pygame.display.flip()
            pygame.time.delay(1000)

        pantalla.fill((0, 0, 0))
        texto = fuente_peleen.render("Peleen!", True, (122,0,0))
        rect_texto = texto.get_rect(center=(pantalla_ancho // 2, pantalla_alto // 2))
        pantalla.blit(texto, rect_texto)
        pygame.display.flip()
        pygame.time.delay(1000)

    def ejecutar(self):
        while True:  # Bucle principal para permitir volver al menú
            if mostrar_menu():
                self.mostrar_contador()
                self.reiniciar_jugadores()
                pygame.mixer.music.load('assets/audios/Y2meta.app - BATTLE AGAINST A TRUE SAMURAI (128 kbps)(pelea).mp3')
                pygame.mixer.music.play(-1)
                inicio_tiempo = pygame.time.get_ticks()

                self.ejecutando = True  # Reiniciar el estado del juego
                while self.ejecutando:
                    for evento in pygame.event.get():
                        if evento.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit()

                    # Obtener el estado de las teclas
                    teclas = pygame.key.get_pressed()

                    # Actualizar los jugadores
                    self.jugador1.actualizar(teclas, pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_s, pygame.K_r,pygame.K_t, pygame.K_y, pygame.K_q, self.jugador2)
                    self.jugador2.actualizar(teclas, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN, pygame.K_i, pygame.K_o, pygame.K_p, pygame.K_k, self.jugador1)

                    # Comprobar colisiones entre las auras y los jugadores, y ataques
                    if self.comprobar_colisiones_y_ataques(teclas, pygame.K_r, pygame.K_i, pygame.K_t, pygame.K_o, pygame.K_y, pygame.K_p):
                        break

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
                        break

                    # Actualizar la pantalla
                    pygame.display.flip()

                    # Controlar la velocidad del juego
                    reloj.tick(60)

# Crear una instancia del juego y ejecutarlo
juego = Juego()
juego.ejecutar()