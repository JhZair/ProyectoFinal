import pygame
import sys

# Inicializar Pygame
pygame.init()
# Configuración de la pantalla
pantalla_ancho = 1600
pantalla_alto = 900
pantalla = pygame.display.set_mode((pantalla_ancho, pantalla_alto))
pygame.display.set_caption("Pelea de dioses")
# Configuración del reloj (fotogramas)
reloj = pygame.time.Clock()

# Colores
blanco = (255, 255, 255)
gris = (66, 66, 66)
celeste = (0, 170, 228)
amarillo = (255, 233, 0)
naranja = (255, 165, 0)

# Plataforma
plataforma = pygame.Rect(200, 550, pantalla_ancho-400, 200)

# Configuración de los jugadores (características)
jugador1 = {
    "color": amarillo,
    "rectan": pygame.Rect(pantalla_ancho//2-250, 500, 30, 80),
    "velocidad": 6,
    "fuerza_salto": 10,
    "gravedad": 0.7,
    "velocidad_y": 0,
    "en_plataforma": False,
}
jugador2 = {
    "color": naranja,
    "rectan": pygame.Rect(pantalla_ancho//2+220, 500, 30, 80),
    "velocidad": 6,
    "fuerza_salto": 10,
    "gravedad": 0.7,
    "velocidad_y": 0,
    "en_plataforma": False,
}

def movimiento_jugador(jugador, llave, izq, derecha, salto):
    # Aplicar gravedad
    jugador["rectan"].y += jugador["velocidad_y"]
    jugador["velocidad_y"] += jugador["gravedad"]

    # Movimiento de izquierda y derecha
    if llave[izq]:
        jugador["rectan"].x -= jugador["velocidad"]
    if llave[derecha]:
        jugador["rectan"].x += jugador["velocidad"]
    # Movimiento de salto
    if llave[salto] and jugador["en_plataforma"]:
        jugador["velocidad_y"] = -jugador["fuerza_salto"]
        jugador["en_plataforma"] = False
    # Colisión con la plataforma
    if jugador["rectan"].colliderect(plataforma):
        jugador["rectan"].bottom = plataforma.top
        jugador["velocidad_y"] = 0
        jugador["en_plataforma"] = True

# Bucle principal del juego
ejecutando = True
while ejecutando:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ejecutando = False

    # Obtener el estado de las teclas
    llaves = pygame.key.get_pressed()

    # Actualizar los jugadores
    movimiento_jugador(jugador1, llaves, pygame.K_a, pygame.K_d, pygame.K_w)
    movimiento_jugador(jugador2, llaves, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP)

    # Dibujar todo en la pantalla
    pantalla.fill(celeste)
    pygame.draw.rect(pantalla, jugador1["color"], jugador1["rectan"])
    pygame.draw.rect(pantalla, jugador2["color"], jugador2["rectan"])
    pygame.draw.rect(pantalla, gris, plataforma)

    # Actualizar la pantalla
    pygame.display.flip()

    # Controlar la velocidad del juego
    reloj.tick(60)

pygame.quit()
sys.exit()