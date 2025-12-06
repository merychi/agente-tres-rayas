# ui/events.py
import pygame
from ui.config import *
# ------------------------------
    # EVENTOS (scroll y clics)
    # ------------------------------
def manejar_eventos(ui):
    """
        Maneja:
         - QUIT
         - wheel / shift+wheel (árbol)
         - wheel sobre camino_real (scroll_camino)
         - flechas (ambos scroll)
         - clicks (tablero, nueva partida, abrir/cerrar modal)
         - ESC para cerrar modal
        Devuelve: 'SALIR', 'REINICIAR', o índice de casilla (0..8) o None
        """
    for evento in pygame.event.get():
        # QUIT
        if evento.type == pygame.QUIT:
            return 'SALIR'

        # --- ARRASTRE CON MOUSE ---
        if evento.type == pygame.MOUSEMOTION:
            if ui.modal_abierto and ui.arrastrando:
                mx, my = pygame.mouse.get_pos()
                dx = mx - ui.mouse_previo[0]
                dy = my - ui.mouse_previo[1]
                ui.modal_scroll_x += dx
                ui.modal_scroll_y += dy
                ui.mouse_previo = (mx, my)

        if evento.type == pygame.MOUSEBUTTONUP:
            ui.arrastrando = False

        # KEYDOWN: flechas o ESC
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE and ui.modal_abierto:
                ui.modal_abierto = False

            # Flechas: siempre mueven la lista (scroll_camino)
            if not ui.modal_abierto:
                if evento.key == pygame.K_UP:
                    ui.scroll_camino -= ui.scroll_camino_speed
                if evento.key == pygame.K_DOWN:
                    ui.scroll_camino += ui.scroll_camino_speed
                if evento.key == pygame.K_LEFT:
                    ui.scroll_x += ui.scroll_velocidad
                if evento.key == pygame.K_RIGHT:
                    ui.scroll_x -= ui.scroll_velocidad

            # Limites
            ui.scroll_camino = max(ui.scroll_camino_min, min(ui.scroll_camino_max, ui.scroll_camino))
            ui.scroll_x = max(ui.scroll_x_min, min(ui.scroll_x_max, ui.scroll_x))
        
        # MOUSEWHEEL
        if evento.type == pygame.MOUSEWHEEL:
            mx, my = pygame.mouse.get_pos()

            if ui.modal_abierto:
                # modal scroll
                if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                    ui.modal_scroll_x += evento.y * ui.modal_scroll_vel
                else:
                    ui.modal_scroll_y += evento.y * ui.modal_scroll_vel
                # Limites wheel modal
                ui.modal_scroll_x = max(ui.scroll_x_min, min(ui.scroll_x_max, ui.modal_scroll_x))
                ui.modal_scroll_y = max(ui.scroll_y_min, min(ui.scroll_y_max + 800, ui.modal_scroll_y))
                continue

            # Mitad derecha → mueve la lista
            if mx > ANCHO_VENTANA // 2:
                ui.scroll_camino += evento.y * ui.scroll_camino_speed
                ui.scroll_camino = max(ui.scroll_camino_min, min(ui.scroll_camino_max, ui.scroll_camino))
                continue

            # resto de la rueda (árbol horizontal)
            if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                ui.scroll_x += evento.y * ui.scroll_velocidad
            else:
                ui.scroll_y += evento.y * ui.scroll_velocidad
            ui.scroll_x = max(ui.scroll_x_min, min(ui.scroll_x_max, ui.scroll_x))
            ui.scroll_y = max(ui.scroll_y_min, min(ui.scroll_y_max, ui.scroll_y))

        # MOUSEBUTTONDOWN (click)
        if evento.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()

            # Si modal abierto y clic en cerrar
            if ui.modal_abierto:
                margin = 40
                caja = pygame.Rect(margin, margin, ANCHO_VENTANA - margin * 2, ALTO_VENTANA - margin * 2)
                btn_cerrar = pygame.Rect(caja.right - 110, caja.y + 10, 90, 36)
                
                if btn_cerrar.collidepoint(mx, my):
                    ui.modal_abierto = False
                    return None
                
                # Si clic en la caja (y no en cerrar), iniciar arrastre
                if caja.collidepoint(mx, my):
                    ui.arrastrando = True
                    ui.mouse_previo = (mx, my)
                
                return None

            # Nueva partida (botón)
            if ui.rect_boton.collidepoint(mx, my):
                return 'REINICIAR'

            # Botón 'Ver árbol completo'
            if ui.rect_boton_arbol.collidepoint(mx, my):
                ui.modal_abierto = True
                ui.modal_scroll_x = 0
                ui.modal_scroll_y = 0
                return None

            # Clic en tablero principal
            if (ui.inicio_x < mx < ui.inicio_x + ui.ancho_juego and
                    ui.inicio_y < my < ui.inicio_y + ui.ancho_juego):
                col = (mx - ui.inicio_x) // (TAMANO_CASILLA + ESPACIO)
                fila = (my - ui.inicio_y) // (TAMANO_CASILLA + ESPACIO)
                if 0 <= col < 3 and 0 <= fila < 3:
                    return fila * 3 + col
    
    # Limites generales
    ui.modal_scroll_y = max(ui.scroll_y_min, min(ui.scroll_y_max + 1500, ui.modal_scroll_y))

    return None