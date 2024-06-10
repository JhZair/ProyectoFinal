import pygame
import sys

# Inicializar Pygame
pygame.init()

# Configuración de la pantalla
pantalla_ancho = 1600
pantalla_alto = 900
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

# Configuración de los jugadores
jugador1 = {
    "color": amarillo,
    "rectan": pygame.Rect(pantalla_ancho // 2 - 250, 500, 40, 90),
    "velocidad": 5,
    "fuerza_salto": 10,
    "gravedad": 0.7,
    "velocidad_y": 0,
    "en_plataforma": False,
    "salud": 500,
    "aura": pygame.Rect(pantalla_ancho // 2 - 270, 380, 70, 120),
    "cooldown": 0,
    "ataque_especial": 0,
    "defendiendo": False
}

jugador2 = {
    "color": naranja,
    "rectan": pygame.Rect(pantalla_ancho // 2 + 220, 500, 40, 90),
    "velocidad": 5,
    "fuerza_salto": 10,
    "gravedad": 0.7,
    "velocidad_y": 0,
    "en_plataforma": False,
    "salud": 500,
    "aura": pygame.Rect(pantalla_ancho // 2 + 200, 380, 70, 120),
    "cooldown": 0,
    "ataque_especial": 0,
    "defendiendo": False
}

def actualizar_jugador(jugador,otro_jugador, teclas, izq, derecha, salto, defensa):
    if teclas[izq]:
        jugador["rectan"].x -= jugador["velocidad"]
        jugador["aura"].x -= jugador["velocidad"]
    if teclas[derecha]:
        jugador["rectan"].x += jugador["velocidad"]
        jugador["aura"].x += jugador["velocidad"]

    if teclas[salto] and jugador["en_plataforma"]:
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
    
    # Colisión con el otro jugador
    if jugador["rectan"].colliderect(otro_jugador["rectan"]):
        if teclas[izq]:
            jugador["rectan"].x = otro_jugador["rectan"].right
            jugador["aura"].x = otro_jugador["rectan"].right + 20
        if teclas[derecha]:
            jugador["rectan"].x = otro_jugador["rectan"].left - jugador["rectan"].width
            jugador["aura"].x = otro_jugador["rectan"].left - jugador["aura"].width - 20

    # Actualizar estado de defensa y velocidad de movimiento
    jugador["defendiendo"] = teclas[defensa]
    if jugador["defendiendo"]:
        jugador["velocidad"] = 2
    if not jugador["defendiendo"]:
        jugador["velocidad"] = 5


def bajar_salud(jugador, dano):
    jugador["salud"] -= dano
    if jugador["salud"] <= 0:
        jugador["salud"] = 0
        return True
    return False

def incrementar_ataque_especial(jugador, incremento):
    jugador["ataque_especial"] += incremento
    if jugador["ataque_especial"] > 200:
        jugador["ataque_especial"] = 200

def dibujar_barra_salud(jugador, posicion, espejo=False):
    ancho_barra = 500
    alto_barra = 30
    if espejo:
        barra = pygame.Rect(posicion[0] - ancho_barra, posicion[1], ancho_barra, alto_barra)
        progreso = pygame.Rect(posicion[0] - jugador["salud"], posicion[1], jugador["salud"], alto_barra)
    else:
        barra = pygame.Rect(posicion[0], posicion[1], ancho_barra, alto_barra)
        progreso = pygame.Rect(posicion[0], posicion[1], jugador["salud"], alto_barra)
    pygame.draw.rect(pantalla, blanco, barra)
    pygame.draw.rect(pantalla, verde_vd, progreso)

def dibujar_ataque_especial(jugador, posicion, espejo=False):
    ancho_barra = 200
    alto_barra = 15
    if espejo:
        barra = pygame.Rect(posicion[0] - ancho_barra, posicion[1], ancho_barra, alto_barra)
        progreso = pygame.Rect(posicion[0] - jugador["ataque_especial"], posicion[1], jugador["ataque_especial"], alto_barra)
    else:
        barra = pygame.Rect(posicion[0], posicion[1], ancho_barra, alto_barra)
        progreso = pygame.Rect(posicion[0], posicion[1], jugador["ataque_especial"], alto_barra)
    pygame.draw.rect(pantalla, blanco, barra)
    pygame.draw.rect(pantalla, amarillos_ps, progreso)

def dibujar_tiempo_restante(tiempo_restante):
    minutos = tiempo_restante // 60
    segundos = tiempo_restante % 60
    texto_tiempo = fuente.render(f"{minutos:02}:{segundos:02}", True, blanco)
    pantalla.blit(texto_tiempo, (pantalla_ancho // 2 - texto_tiempo.get_width() // 2, 10))

def determinar_ganador(jugador1, jugador2):
    if jugador1["salud"] > jugador2["salud"]:
        print("Jugador 1 gana por salud")
    elif jugador2["salud"] > jugador1["salud"]:
        print("Jugador 2 gana por salud")
    else:
        print("Empate")

def comprobar_colisiones_y_ataques(jugador1, jugador2, teclas, ataque_j1, ataque_j2, ataque_especial_j1, ataque_especial_j2):
    tiempo_actual = pygame.time.get_ticks()

    if jugador1["aura"].colliderect(jugador2["rectan"]) and teclas[ataque_j1] and tiempo_actual > jugador1["cooldown"] and not jugador1["defendiendo"]:
        jugador1["cooldown"] = tiempo_actual + 1000
        incrementar_ataque_especial(jugador1, 50)
        if jugador2["defendiendo"]:
            if bajar_salud(jugador2, 10):
                print("Jugador 2 ha sido derrotado")
                return True
        else:
            if bajar_salud(jugador2, 30):
                print("Jugador 2 ha sido derrotado")
                return True

    if jugador2["aura"].colliderect(jugador1["rectan"]) and teclas[ataque_j2] and tiempo_actual > jugador2["cooldown"] and not jugador2["defendiendo"]:
        jugador2["cooldown"] = tiempo_actual + 1000
        incrementar_ataque_especial(jugador2, 50)
        if jugador1["defendiendo"]:
            if bajar_salud(jugador1, 10):
                print("Jugador 1 ha sido derrotado")
                return True
        else:
            if bajar_salud(jugador1, 30):
                print("Jugador 1 ha sido derrotado")
                return True

    # Comprobar ataques especiles
    if teclas[ataque_especial_j1] and jugador1["ataque_especial"] == 200 and not jugador1["defendiendo"]:
        jugador1["ataque_especial"] = 0
        if bajar_salud(jugador2, 50):
            print("Jugador 2 ha sido derrotado")
            return True

    if teclas[ataque_especial_j2] and jugador2["ataque_especial"] == 200 and not jugador2["defendiendo"]:
        jugador2["ataque_especial"] = 0
        if bajar_salud(jugador1, 50):
            print("Jugador 1 ha sido derrotado")
            return True

    return False

# Bucle principal del juego
ejecutando = True
while ejecutando:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ejecutando = False

    # Obtener el estado de las teclas
    teclas = pygame.key.get_pressed()

    # Actualizar los jugadores
    actualizar_jugador(jugador1, jugador2, teclas, pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_s)
    actualizar_jugador(jugador2, jugador1, teclas, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN)

    # Comprobar colisiones entre las auras y los jugadores, y ataques
    if comprobar_colisiones_y_ataques(jugador1, jugador2, teclas, pygame.K_r, pygame.K_i, pygame.K_t, pygame.K_o):
        ejecutando = False

    # Dibujar todo en la pantalla
    pantalla.fill(celeste)
    pygame.draw.rect(pantalla, jugador1["color"], jugador1["rectan"])
    pygame.draw.rect(pantalla, jugador2["color"], jugador2["rectan"])
    pygame.draw.rect(pantalla, gris, plataforma)

    # Dibujar las auras para visualización (opcional)
    pygame.draw.rect(pantalla, verde_transparente, jugador1["aura"])
    pygame.draw.rect(pantalla, verde_transparente, jugador2["aura"])

    # Dibujar la salud de los jugadores
    dibujar_barra_salud(jugador1, (10, 10))
    dibujar_barra_salud(jugador2, (pantalla_ancho - 10, 10), espejo=True)

    # Dibujar la barra de ataque especial
    dibujar_ataque_especial(jugador1, (10, 50))
    dibujar_ataque_especial(jugador2, (pantalla_ancho - 10, 50), espejo=True)

    # Calcular y dibujar el tiempo restante
    tiempo_transcurrido = (pygame.time.get_ticks() - inicio_tiempo) // 1000
    tiempo_restante = duracion_partida - tiempo_transcurrido
    dibujar_tiempo_restante(tiempo_restante)
    
    # Verificar si el tiempo se ha agotado
    if tiempo_restante <= 0:
        determinar_ganador(jugador1, jugador2)
        ejecutando = False

    # Actualizar la pantalla
    pygame.display.flip()

    # Controlar la velocidad del juego
    reloj.tick(60)

pygame.quit()
sys.exit()


##Falta arreglar colisiones de aura, agregar evento de muerte al caer de la plataforma, solucionar bug al pegarse a la plataforma por los costados,
# falta contador inicial para iniciar el juego, falta pantalla final al ganar un jugador o quedar en empate o por tiempo, faltan agregar personajes distintos con
# características diferentes, interfaz de inicio del juego, interfaz de pausa, interfaz de selección de personajes, añadir animaciones distintas para cada personaje, etc 