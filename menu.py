import pygame
import sys

# Inicializar Pygame
pygame.init()

# Configuración de la pantalla
ancho_pantalla = 1600
alto_pantalla = 900
pantalla = pygame.display.set_mode((ancho_pantalla, alto_pantalla))
pygame.display.set_caption("Pelea de dioses")

# Colores
blanco = (255, 255, 255)
negro = (0, 0, 0)
celeste = (135, 206, 235)

# Fuente para el menú
fuente = pygame.font.Font(None, 50)

# Función para mostrar el menú
def mostrar_menu():
    opciones_menu = ['Jugar', 'Opciones', 'Salir']
    opcion_actual = 0

    while True:
        pantalla.fill(celeste)
        titulo = fuente.render('Pelea de Dioses', True, blanco)
        pantalla.blit(titulo, (ancho_pantalla // 2 - titulo.get_width() // 2, 100))

        for i, opcion in enumerate(opciones_menu):
            color_texto = blanco  # Color por defecto
            if i == opcion_actual:
                color_texto = negro  # Resaltar en negro si es la opción actual

            texto = fuente.render(opcion, True, color_texto)
            pantalla.blit(texto, (ancho_pantalla // 2 - texto.get_width() // 2, 250 + i * 50))

        pygame.display.update()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_DOWN:
                    opcion_actual = (opcion_actual + 1) % len(opciones_menu)
                elif evento.key == pygame.K_UP:
                    opcion_actual = (opcion_actual - 1) % len(opciones_menu)
                elif evento.key == pygame.K_RETURN:
                    if opcion_actual == 0:  # Jugar
                        print("Iniciar juego")
                        return True
                    elif opcion_actual == 1:  # Opciones
                        print("Ver opciones")
                        # Aquí iría la función para mostrar opciones
                    elif opcion_actual == 2:  # Salir
                        pygame.quit()
                        sys.exit()
