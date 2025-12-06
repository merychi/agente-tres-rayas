import pygame
from ui.config import *

# ------------------------------
# Mini-tablero con fade-in
# ------------------------------
def dibujar_mini_tablero(pantalla, fuente, x, y, tablero_data, tamano, fade_cache, fade_speed, puntaje=None, nodo_id=None, es_camino=False):
    """
    Dibuja un mini-tablero en (x,y). Usa fade-cache por nodo_id.
    Devuelve (center_x, bottom_y) para conexiones.
    No usa 'self', recibe todo lo necesario como argumentos.
    """
    padding = 2
    ancho_total = (tamano * 3) + (padding * 4)

    # Inicializar alpha (fade in)
    if nodo_id not in fade_cache:
        fade_cache[nodo_id] = 0
    alpha = min(fade_cache[nodo_id] + fade_speed, 255)
    fade_cache[nodo_id] = alpha

    surf = pygame.Surface((ancho_total, ancho_total), pygame.SRCALPHA)

    # Borde por puntaje (si aplica)
    color_borde = COLOR_TABLERO
    if es_camino:
        color_borde = "#33ff33"
    elif puntaje is not None:
        if puntaje > 0:
            color_borde = "#33ff33"
        elif puntaje < 0:
            color_borde = "#ff3333"
        else:
            color_borde = "#cccccc"

    # Dibujo de rectángulos
    pygame.draw.rect(surf, pygame.Color(color_borde), (0, 0, ancho_total, ancho_total), border_radius=4)
    pygame.draw.rect(surf, pygame.Color(COLOR_TABLERO), (2, 2, ancho_total - 4, ancho_total - 4), border_radius=4)
    
    grosor_borde = 3 if es_camino else 2
    pygame.draw.rect(surf, pygame.Color(COLOR_TABLERO), 
                    (grosor_borde, grosor_borde, ancho_total - (grosor_borde*2), ancho_total - (grosor_borde*2)), 
                    border_radius=4)

    # Dibujar casillas y fichas
    for i in range(9):
        fila = i // 3
        col = i % 3
        px = padding + col * (tamano + padding)
        py = padding + fila * (tamano + padding)
        pygame.draw.rect(surf, pygame.Color(COLOR_CASILLA), (px, py, tamano, tamano), border_radius=2)
        if tablero_data[i] != " ":
            color = pygame.Color(COLOR_X if tablero_data[i] == "X" else COLOR_O)
            # Usamos la 'fuente' que nos pasaron
            txt = fuente.render(tablero_data[i], True, color)
            surf.blit(txt, txt.get_rect(center=(px + tamano / 2, py + tamano / 2)))

    surf.set_alpha(alpha)
    pantalla.blit(surf, (x, y))
    
    # Devuelve el punto de conexión inferior
    return (x + ancho_total // 2, y + ancho_total)