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
amarillo = (255, 233, 0)
naranja = (255, 165, 0)
celeste = (0, 170, 228)
verde_transparente = (0, 255, 0, 128)  # Verde semitransparente para las auras

# Configuración del reloj
reloj = pygame.time.Clock()

# Plataforma
plataforma = pygame.Rect(200, 450, pantalla_ancho - 400, 200)

# Configuración de los jugadores
jugador1 = {
    "color": amarillo,
    "rectan": pygame.Rect(pantalla_ancho // 2 - 250, 400, 30, 80),
    "velocidad": 5,
    "fuerza_salto": 10,
    "gravedad": 0.7,
    "velocidad_y": 0,
    "en_plataforma": False,
    "salud": 100,  # Salud inicial
    "aura": pygame.Rect(pantalla_ancho // 2 - 270, 380, 70, 120)  # Aura del jugador
}

jugador2 = {
    "color": naranja,
    "rectan": pygame.Rect(pantalla_ancho // 2 + 220, 400, 30, 80),
    "velocidad": 5,
    "fuerza_salto": 10,
    "gravedad": 0.7,
    "velocidad_y": 0,
    "en_plataforma": False,
    "salud": 100,  # Salud inicial
    "aura": pygame.Rect(pantalla_ancho // 2 + 200, 380, 70, 120)  # Aura del jugador
}

def actualizar_jugador(jugador, llaves, izq, derecha, salto):
    if llaves[izq]:
        jugador["rectan"].x -= jugador["velocidad"]
        jugador["aura"].x -= jugador["velocidad"]
    if llaves[derecha]:
        jugador["rectan"].x += jugador["velocidad"]
        jugador["aura"].x += jugador["velocidad"]

    if llaves[salto] and jugador["en_plataforma"]:
        jugador["velocidad_y"] = -jugador["fuerza_salto"]
        jugador["en_plataforma"] = False

    # Aplicar gravedad
    jugador["rectan"].y += jugador["velocidad_y"]
    jugador["aura"].y += jugador["velocidad_y"]
    jugador["velocidad_y"] += jugador["gravedad"]

    # Colisión con la plataforma
    if jugador["rectan"].colliderect(plataforma):
        jugador["rectan"].bottom = plataforma.top
        jugador["aura"].bottom = plataforma.top
        jugador["velocidad_y"] = 0
        jugador["en_plataforma"] = True

def manejar_salud(jugador, dano):
    jugador["salud"] -= dano
    if jugador["salud"] <= 0:
        jugador["salud"] = 0
        return True
    return False

def dibujar_salud(jugador, posicion):
    fuente = pygame.font.Font(None, 36)
    texto_salud = fuente.render(f'Salud: {jugador["salud"]}', True, blanco)
    pantalla.blit(texto_salud, posicion)

def comprobar_colisiones_y_ataques(jugador1, jugador2, llaves, ataque_j1, ataque_j2):
    if jugador1["aura"].colliderect(jugador2["rectan"]) and llaves[ataque_j1]:
        if manejar_salud(jugador2, 1):  # Infligir 10 puntos de daño
            print("Jugador 2 ha sido derrotado")
            return False

    if jugador2["aura"].colliderect(jugador1["rectan"]) and llaves[ataque_j2]:
        if manejar_salud(jugador1, 1):  # Infligir 10 puntos de daño
            print("Jugador 1 ha sido derrotado")
            return False

    return True

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

    # Comprobar colisiones entre las auras y los jugadores, y ataques
    if not comprobar_colisiones_y_ataques(jugador1, jugador2, llaves, pygame.K_r, pygame.K_i):
        ejecutando = False

    # Dibujar todo en la pantalla
    pantalla.fill(celeste)
    pygame.draw.rect(pantalla, jugador1["color"], jugador1["rectan"])
    pygame.draw.rect(pantalla, jugador2["color"], jugador2["rectan"])
    pygame.draw.rect(pantalla, blanco, plataforma)

    # Dibujar las auras para visualización (opcional)
    # pygame.draw.rect(pantalla, verde_transparente, jugador1["aura"])
    # pygame.draw.rect(pantalla, verde_transparente, jugador2["aura"])

    # Dibujar la salud de los jugadores
    dibujar_salud(jugador1, (10, 10))
    dibujar_salud(jugador2, (pantalla_ancho - 150, 10))

    # Actualizar la pantalla
    pygame.display.flip()

    # Controlar la velocidad del juego
    reloj.tick(60)

pygame.quit()
sys.exit()
