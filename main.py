import pygame
import sys

# Inicializar Pygame
pygame.init()

# Configuración de la pantalla
pantalla_ancho = 1200
pantalla_alto = 800
pantalla = pygame.display.set_mode((pantalla_ancho, pantalla_alto))
pygame.display.set_caption("Pelea de dioses")

# Colores
blanco = (255, 255, 255)
negro = (0, 0, 0)
rojo = (255, 0, 0)
azul = (0, 0, 255)
amarillo = (255, 233, 0)
naranja = (255, 165, 0)

# Configuración del reloj
reloj = pygame.time.Clock()

# Plataforma
plataforma = pygame.Rect(200, 450, pantalla_ancho-400, 200)

# Configuración de los jugadores
jugador1 = {
    "color": amarillo,
    "rectan": pygame.Rect(pantalla_ancho//2-250, 400, 30, 80),
    "velocidad": 5,
    "fuerza_salto": 10,
    "gravedad": 0.7,
    "velocidad_y": 0,
    "en_plataforma": False,
}

jugador2 = {
    "color": naranja,
    "rectan": pygame.Rect(pantalla_ancho//2+220, 400, 30, 80),
    "velocidad": 5,
    "fuerza_salto": 10,
    "gravedad": 0.7,
    "velocidad_y": 0,
    "en_plataforma": False,
}

def actualizar_jugador(jugador, llave, izq, derecha, salto):
    if llave[izq]:
        jugador["rectan"].x -= jugador["velocidad"]
    if llave[derecha]:
        jugador["rectan"].x += jugador["velocidad"]
    
    if llave[salto] and jugador["en_plataforma"]:
        jugador["velocidad_y"] = -jugador["fuerza_salto"]
        jugador["en_plataforma"] = False

    # Aplicar gravedad
    jugador["rectan"].y += jugador["velocidad_y"]
    jugador["velocidad_y"] += jugador["gravedad"]

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
    actualizar_jugador(jugador1, llaves, pygame.K_a, pygame.K_d, pygame.K_w)
    actualizar_jugador(jugador2, llaves, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP)

    # Dibujar todo en la pantalla
    pantalla.fill(negro)
    pygame.draw.rect(pantalla, jugador1["color"], jugador1["rectan"])
    pygame.draw.rect(pantalla, jugador2["color"], jugador2["rectan"])
    pygame.draw.rect(pantalla, blanco, plataforma)

    # Actualizar la pantalla
    pygame.display.flip()

    # Controlar la velocidad del juego
    reloj.tick(60)

pygame.quit()
sys.exit()