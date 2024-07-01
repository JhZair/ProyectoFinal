import pygame
import os
from config import *

# Inicializar Pygame
pygame.init()
pygame.mixer.init()

# Configuración de la pantalla
pantalla = pygame.display.set_mode((pantalla_ancho, pantalla_alto))
pygame.display.set_caption(nombre_juego)

# Colores
blanco = (255, 255, 255)
negro = (0, 0, 0)
rojo = (122,0,0)

# Fuente para el menú
fuente_titulo = pygame.font.Font("assets/fonts/upheavtt.ttf", 100)
fuente_opciones = pygame.font.Font("assets/fonts/upheavtt.ttf", 60)

imagen_controles = pygame.image.load('assets/images/controles.jpeg')

# Cargar las imágenes del fondo y redimensionarlas
ruta_cuadros = 'assets/images/Fondo_menu'  # Cambia esto a la ruta de tus cuadros
cuadros = []
for f in sorted(os.listdir(ruta_cuadros)):
    if f.endswith('.jpg'):
        imagen = pygame.image.load(os.path.join(ruta_cuadros, f)).convert_alpha()
        imagen = pygame.transform.scale(imagen, (pantalla_ancho, pantalla_alto))
        cuadros.append(imagen)

# Variables para controlar la animación
indice_cuadro = 0
tiempo_entre_cuadros = 80  # Milisegundos entre cuadros
tiempo_ultimo_cuadro = pygame.time.get_ticks()
def mostrar_controles():
    mostrar_controles_activo = True
    while mostrar_controles_activo:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                return False
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE or evento.key == pygame.K_RETURN:
                    mostrar_controles_activo = False

        pantalla.fill((0, 0, 0))
        pantalla.blit(imagen_controles, (0,0))
        pygame.display.flip()

# Función para mostrar el menú
def mostrar_menu():
    opciones_menu = ['Jugar', 'Controles', 'Salir']
    opcion_actual = 0
    pygame.mixer.music.load('assets/audios/ASGORE THE SHOGUN OF THE MOUNTAIN(interfaz).mp3')
    pygame.mixer.music.play(-1)

    while True:
        # Manejar eventos
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                return False
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_DOWN:
                    opcion_actual = (opcion_actual + 1) % len(opciones_menu)
                elif evento.key == pygame.K_UP:
                    opcion_actual = (opcion_actual - 1) % len(opciones_menu)
                elif evento.key == pygame.K_RETURN:
                    if opcion_actual == 0:
                        print("Iniciar juego")
                        pygame.mixer.music.stop()
                        return True
                    elif opcion_actual == 1:
                        print("Controles")
                        mostrar_controles()
                    elif opcion_actual == 2:
                        pygame.quit()
                        return False

        # Actualiza el cuadro del fondo
        tiempo_actual = pygame.time.get_ticks()
        global indice_cuadro, tiempo_ultimo_cuadro
        if tiempo_actual - tiempo_ultimo_cuadro > tiempo_entre_cuadros:
            indice_cuadro = (indice_cuadro + 1) % len(cuadros)
            tiempo_ultimo_cuadro = tiempo_actual

        # Dibuja el cuadro actual del fondo
        pantalla.blit(cuadros[indice_cuadro], (0, 0))

        titulo = fuente_titulo.render(nombre_juego, True, blanco)
        pantalla.blit(titulo, (pantalla_ancho // 2 - titulo.get_width() // 2, 100))

        for i, opcion in enumerate(opciones_menu):
            color_texto = blanco
            if i == opcion_actual:
                color_texto = rojo

            texto = fuente_opciones.render(opcion, True, color_texto)
            pantalla.blit(texto, (pantalla_ancho // 2 - texto.get_width() // 2, 375 + i * 70))

        pygame.display.update()
