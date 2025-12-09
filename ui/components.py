# COMPONENTS.PY: CONTIENE LOS COMPONENTES UTILIZADOS EN LA INTERFAZ DEL JUEGO"

import pygame
from ui.config import *

# ------------------------------
# Mini-tablero con fade-in
# Dibuja un mini-tablero en (x,y). Usa fade-cache por nodo_id.
# Devuelve (center_x, bottom_y) para conexiones.
# No usa 'self', recibe todo lo necesario como argumentos.
# ------------------------------
def dibujar_mini_tablero(pantalla, fuente, x, y, tablero_data, tamano, fade_cache, fade_speed, puntaje=None, nodo_id=None, es_camino=False):
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

# ------------------------------
# dibujar_boton_redondo
# Botón ovalado con sombra y efecto hover; devuelve True si el mouse está encima.
# ------------------------------
def dibujar_boton_redondo(pantalla, rect, texto, fuente_boton):
    mouse_pos = pygame.mouse.get_pos()
    es_hover = rect.collidepoint(mouse_pos)
    
    color_base = (44, 44, 84)
    color_hover = (70, 70, 130)
    color_sombra = (79, 87, 175)
    
    color_actual = color_hover if es_hover else color_base
    elevacion = 4 if es_hover else 0
    
    rect_sombra = rect.copy()
    rect_sombra.y += 6 
    pygame.draw.rect(pantalla, color_sombra, rect_sombra, border_radius=25)
    
    rect_visual = rect.copy()
    rect_visual.y -= elevacion
    pygame.draw.rect(pantalla, color_actual, rect_visual, border_radius=25)
    
    txt_surf = fuente_boton.render(texto, True, (255, 255, 255))
    txt_rect = txt_surf.get_rect(center=rect_visual.center)
    pantalla.blit(txt_surf, txt_rect)

    return es_hover
# ------------------------------
# dibujar_boton_salir
# Dibuja el botón casita con techo, pared y puerta; devuelve True si se hovered.
# ------------------------------
def dibujar_boton_salir(pantalla, rect):
    mouse_pos = pygame.mouse.get_pos()
    es_hover = rect.collidepoint(mouse_pos)
    
    color_base = (44, 44, 84)
    color_hover = (70, 70, 130)
    color_sombra = (79, 87, 175)
    color_icono = (255, 255, 255)
    
    color_actual = color_hover if es_hover else color_base
    elevacion = 3 if es_hover else 0
    
    # 1. SOMBRA
    rect_sombra = rect.copy()
    rect_sombra.y += 5 
    pygame.draw.rect(pantalla, color_sombra, rect_sombra, border_radius=15)
    
    # 2. BOTÓN VISUAL
    rect_visual = rect.copy()
    rect_visual.y -= elevacion
    pygame.draw.rect(pantalla, color_actual, rect_visual, border_radius=15)
    
    # --- 3. DIBUJAR ÍCONO DE CASITA ---
    cx, cy = rect_visual.centerx, rect_visual.centery
    
    puntos_techo = [
        (cx, cy - 8),                       
        (cx - 12, cy + 2),      
        (cx + 12, cy + 2)       
    ]
    pygame.draw.polygon(pantalla, color_icono, puntos_techo)
    
    pygame.draw.rect(pantalla, color_icono, (cx - 8, cy + 2, 16, 14))
    
    pygame.draw.rect(pantalla, color_actual, (cx - 3, cy + 8, 6, 8), 
                     border_top_left_radius=2, border_top_right_radius=2)

    return es_hover