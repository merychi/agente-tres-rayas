# ui/interface.py
import pygame
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# --- COLORES ---
COLOR_FONDO = "#929df6"
COLOR_TABLERO = "#373a7f"
COLOR_CASILLA = "#4f57af"
COLOR_X = "#ebbaef"
COLOR_O = "#e0e9e0"
COLOR_TEXTO = "#FFFFFF"
COLOR_LINEA = "#5c6bc0"
COLOR_BOTON = "#2c2f66"
COLOR_BOTON_HOVER = "#3e4291"

# --- DIMENSIONES ---
ANCHO_VENTANA = 1360
ALTO_VENTANA = 760
TAMANO_CASILLA = 90
TAMANO_MINI = 26
ESPACIO = 10
ESPACIO_VERTICAL_ARBOL = 130
ANCHO_SECCION_ARBOL = 850


class InterfazGrafica:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        self.pantalla = pygame.display.set_mode((ANCHO_VENTANA, ALTO_VENTANA))
        pygame.display.set_caption("Tres en Raya - Minimax")

        # --- Fade / animaciones ---
        self.fade_cache = {}           # id_nodo -> alpha
        self.fade_speed = 12           # incremento alpha por frame
        self.fade_cache_camino = {}    # fade independiente para camino real

        # --- Scrolls ---
        # Árbol completo (X,Y)
        self.scroll_x = 0
        self.scroll_y = 0
        self.scroll_velocidad = 40
        self.scroll_y_min = -2500
        self.scroll_y_max = 200
        self.scroll_x_min = -1200
        self.scroll_x_max = 300

        # Camino real (solo vertical)
        self.scroll_camino = 0
        self.scroll_camino_speed = 30
        self.scroll_camino_min = -2000
        self.scroll_camino_max = 200

        # Modal (pantalla completa) para árbol
        self.modal_abierto = False
        self.modal_scroll_x = 0
        self.modal_scroll_y = 0
        self.modal_scroll_vel = 40

        # Fuentes
        self.fuente_titulo = pygame.font.SysFont("Arial", 28, bold=True)
        self.fuente_ficha = pygame.font.SysFont("Arial", 60, bold=True)
        self.fuente_mini = pygame.font.SysFont("Arial", 16, bold=True)
        self.fuente_ui = pygame.font.SysFont("Arial", 14)

        # Layout tablero
        self.ancho_juego = (TAMANO_CASILLA * 3) + (ESPACIO * 4)
        self.inicio_x = 50
        self.inicio_y = 150
        self.rect_boton = pygame.Rect(50, ALTO_VENTANA - 90, 200, 50)

        # Camino real ancho fijo
        self.ancho_camino = 220

        # Colors preconverted
        self._color_text = pygame.Color(COLOR_TEXTO)

    # ------------------------------
    # Mini-tablero con fade-in
    # ------------------------------
    def dibujar_mini_tablero(self, x, y, tablero_data, tamano, puntaje=None, nodo_id=None):
        """
        Dibuja un mini-tablero en (x,y). Usa fade-cache por nodo_id.
        Devuelve (center_x, bottom_y) para conexiones.
        """
        padding = 2
        ancho_total = (tamano * 3) + (padding * 4)

        # inicializar alpha
        if nodo_id not in self.fade_cache:
            self.fade_cache[nodo_id] = 0
        alpha = min(self.fade_cache[nodo_id] + self.fade_speed, 255)
        self.fade_cache[nodo_id] = alpha

        surf = pygame.Surface((ancho_total, ancho_total), pygame.SRCALPHA)

        # Borde por puntaje (si aplica)
        color_borde = COLOR_TABLERO
        if puntaje is not None:
            if puntaje > 0:
                color_borde = "#33ff33"
            elif puntaje < 0:
                color_borde = "#ff3333"
            else:
                color_borde = "#cccccc"

        pygame.draw.rect(surf, pygame.Color(color_borde), (0, 0, ancho_total, ancho_total), border_radius=4)
        pygame.draw.rect(surf, pygame.Color(COLOR_TABLERO), (2, 2, ancho_total - 4, ancho_total - 4), border_radius=4)

        for i in range(9):
            fila = i // 3
            col = i % 3
            px = padding + col * (tamano + padding)
            py = padding + fila * (tamano + padding)
            pygame.draw.rect(surf, pygame.Color(COLOR_CASILLA), (px, py, tamano, tamano), border_radius=2)
            if tablero_data[i] != " ":
                color = pygame.Color(COLOR_X if tablero_data[i] == "X" else COLOR_O)
                txt = self.fuente_mini.render(tablero_data[i], True, color)
                surf.blit(txt, txt.get_rect(center=(px + tamano / 2, py + tamano / 2)))

        surf.set_alpha(alpha)
        self.pantalla.blit(surf, (x, y))
        return (x + ancho_total // 2, y + ancho_total)

    # ------------------------------
    # ÁRBOL recursivo (usa scroll_x, scroll_y)
    # ------------------------------
    def dibujar_arbol_recursivo(self, nodos, x_min, x_max, y_nivel, padre_pos=None):
        if not nodos:
            return

        cantidad = len(nodos)
        ancho_nodo_px = (TAMANO_MINI * 3) + 8

        if cantidad == 1 and padre_pos:
            espacio_por_nodo = 0
        else:
            ancho_disponible = (x_max - x_min)
            espacio_por_nodo = ancho_disponible / max(cantidad, 1)

        for i, nodo in enumerate(nodos):
            # Calcula pos_x con scroll_x
            if cantidad == 1 and padre_pos:
                pos_x = padre_pos[0] - (ancho_nodo_px / 2) + self.scroll_x
            else:
                center_x = x_min + (i * espacio_por_nodo) + (espacio_por_nodo / 2)
                pos_x = center_x - (ancho_nodo_px / 2) + self.scroll_x

            pos_y = y_nivel + self.scroll_y
            punto_conexion_top = (pos_x + ancho_nodo_px / 2, pos_y)

            # Dibujar líneas hacia el nodo
            if padre_pos:
                mid_y = pos_y - (ESPACIO_VERTICAL_ARBOL / 2)
                pygame.draw.line(self.pantalla, pygame.Color(COLOR_LINEA),
                                 (padre_pos[0], padre_pos[1]), (padre_pos[0], mid_y), 2)
                pygame.draw.line(self.pantalla, pygame.Color(COLOR_LINEA),
                                 (padre_pos[0], mid_y), (punto_conexion_top[0], mid_y), 2)
                pygame.draw.line(self.pantalla, pygame.Color(COLOR_LINEA),
                                 (punto_conexion_top[0], mid_y), punto_conexion_top, 2)

            # Mini-tablero del nodo (fade)
            nodo_id = id(nodo)
            punto_conexion_bottom = self.dibujar_mini_tablero(
                pos_x, pos_y, nodo["tablero"], TAMANO_MINI, nodo.get("puntaje"), nodo_id
            )

            # Puntaje textual
            p_val = nodo.get("puntaje")
            if p_val is not None:
                col_p = pygame.Color("#ccffcc") if p_val > 0 else (pygame.Color("#ffcccc") if p_val < 0 else pygame.Color("#ffffff"))
                self.pantalla.blit(self.fuente_ui.render(str(p_val), True, col_p),
                                   (pos_x + ancho_nodo_px + 3, pos_y + 10))

            # Recursividad
            if nodo.get("sub_ramas"):
                if cantidad == 1:
                    self.dibujar_arbol_recursivo(nodo["sub_ramas"], x_min, x_max, y_nivel + ESPACIO_VERTICAL_ARBOL, punto_conexion_bottom)
                else:
                    x_min_hijo = x_min + (i * espacio_por_nodo)
                    x_max_hijo = x_min + ((i + 1) * espacio_por_nodo)
                    self.dibujar_arbol_recursivo(nodo["sub_ramas"], x_min_hijo, x_max_hijo, y_nivel + ESPACIO_VERTICAL_ARBOL, punto_conexion_bottom)

    # ------------------------------
    # CAMINO REAL (columna con scroll propio)
    # ------------------------------
    def dibujar_camino_real(self, camino_real, x_inicio, y_inicio):
        """
        Dibuja la columna del CAMINO REAL con scroll independiente.
        Cada nodo muestra: etiqueta (MAX/MIN), puntaje y mini-tablero con fade.
        """
        if not camino_real:
            return

        y = y_inicio + self.scroll_camino

        for depth, nodo in enumerate(camino_real):
            # Etiqueta (MAX / MIN)
            turno = "MAX (X)" if depth % 2 == 0 else "MIN (O)"
            color_turno = (180, 220, 255) if depth % 2 == 0 else (255, 200, 220)
            txt = self.fuente_ui.render(turno, True, color_turno)
            self.pantalla.blit(txt, (x_inicio, y))
            y += 20

            # Puntaje
            puntaje = nodo.get("puntaje", 0)
            col_p = pygame.Color("#ccffcc") if puntaje > 0 else (pygame.Color("#ffcccc") if puntaje < 0 else pygame.Color("#ffffff"))
            txt_p = self.fuente_ui.render(f"Puntaje: {puntaje}", True, col_p)
            self.pantalla.blit(txt_p, (x_inicio, y))
            y += 20

            # Mini-tablero con fade (cache propio)
            nodo_id = id(nodo)
            if nodo_id not in self.fade_cache_camino:
                self.fade_cache_camino[nodo_id] = 0
            alpha = min(255, self.fade_cache_camino[nodo_id] + self.fade_speed)
            self.fade_cache_camino[nodo_id] = alpha

            surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.rect(surf, pygame.Color(40, 40, 80), (0, 0, 120, 120), border_radius=6)

            # Mini tablero dentro de surf (3x3)
            cuadro_tam = 30
            padding = 5
            for i in range(9):
                fila = i // 3
                col = i % 3
                px = padding + col * (cuadro_tam + padding)
                py = padding + fila * (cuadro_tam + padding)
                pygame.draw.rect(surf, pygame.Color(COLOR_CASILLA), (px, py, cuadro_tam, cuadro_tam), border_radius=4)
                val = nodo["tablero"][i]
                if val != " ":
                    color = pygame.Color(COLOR_X if val == "X" else COLOR_O)
                    txt_v = self.fuente_mini.render(val, True, color)
                    surf.blit(txt_v, txt_v.get_rect(center=(px + cuadro_tam / 2, py + cuadro_tam / 2)))

            surf.set_alpha(alpha)
            self.pantalla.blit(surf, (x_inicio, y))
            y += 140

            # Línea vertical conectando al siguiente (si existe)
            if depth < len(camino_real) - 1:
                x_line = x_inicio + 60
                pygame.draw.line(self.pantalla, pygame.Color(200, 200, 200), (x_line, y - 10), (x_line, y + 20), 2)

    # ------------------------------
    # DIBUJAR INTERFAZ (principal)
    # ------------------------------
    def dibujar_interfaz(self, tablero, mensaje, tablero_raiz=None, estructura_arbol=None, camino_real=None):
        """
        dibujar_interfaz ahora acepta camino_real (lista de nodos) además del árbol.
        """
        self.pantalla.fill(pygame.Color(COLOR_FONDO))

        # IZQUIERDA: TABLERO PRINCIPAL
        self.pantalla.blit(self.fuente_titulo.render(mensaje, True, pygame.Color(COLOR_TEXTO)), (self.inicio_x, 80))
        pygame.draw.rect(self.pantalla, pygame.Color(COLOR_TABLERO),
                         (self.inicio_x, self.inicio_y, self.ancho_juego, self.ancho_juego), border_radius=20)

        for i in range(9):
            fila = i // 3
            col = i % 3
            x = self.inicio_x + ESPACIO + col * (TAMANO_CASILLA + ESPACIO)
            y = self.inicio_y + ESPACIO + fila * (TAMANO_CASILLA + ESPACIO)
            pygame.draw.rect(self.pantalla, pygame.Color(COLOR_CASILLA), (x, y, TAMANO_CASILLA, TAMANO_CASILLA), border_radius=15)
            if tablero[i] != " ":
                color = pygame.Color(COLOR_X if tablero[i] == "X" else COLOR_O)
                txt = self.fuente_ficha.render(tablero[i], True, color)
                self.pantalla.blit(txt, txt.get_rect(center=(x + TAMANO_CASILLA / 2, y + TAMANO_CASILLA / 2)))

        # BOTÓN Nueva partida
        color_btn = pygame.Color(COLOR_BOTON_HOVER) if self.rect_boton.collidepoint(pygame.mouse.get_pos()) else pygame.Color(COLOR_BOTON)
        pygame.draw.rect(self.pantalla, color_btn, self.rect_boton, border_radius=10)
        self.pantalla.blit(self.fuente_ui.render("Nueva Partida", True, pygame.Color(COLOR_TEXTO)),
                           (self.rect_boton.x + 55, self.rect_boton.y + 17))

        # COLUMNA CAMINO REAL (centro-der)
        camino_x = self.inicio_x + self.ancho_juego + 40
        if camino_real is not None:
            self.pantalla.blit(self.fuente_titulo.render("Camino Real", True, pygame.Color(COLOR_TEXTO)),
                               (camino_x, 40))
            self.dibujar_camino_real(camino_real, camino_x, 100)

        # BOTÓN Ver árbol completo (abre modal)
        boton_modal = pygame.Rect(camino_x, ALTO_VENTANA - 90, 180, 40)
        color_bm = pygame.Color(COLOR_BOTON_HOVER) if boton_modal.collidepoint(pygame.mouse.get_pos()) else pygame.Color(COLOR_BOTON)
        pygame.draw.rect(self.pantalla, color_bm, boton_modal, border_radius=8)
        self.pantalla.blit(self.fuente_ui.render("Ver árbol completo", True, pygame.Color(COLOR_TEXTO)),
                           (boton_modal.x + 18, boton_modal.y + 10))

        # ARBOL COMPLETO (derecha)
        titulo_arbol = self.fuente_titulo.render("Árbol de Decisiones", True, pygame.Color(COLOR_TEXTO))
        self.pantalla.blit(titulo_arbol, (ANCHO_VENTANA - ANCHO_SECCION_ARBOL // 2 - 150, 40))

        inicio_arbol_x = ANCHO_VENTANA - ANCHO_SECCION_ARBOL - 20
        fin_arbol_x = ANCHO_VENTANA - 20
        centro_arbol_x = inicio_arbol_x + (ANCHO_SECCION_ARBOL // 2)

        tablero_a_usar = tablero_raiz if tablero_raiz else tablero
        ancho_nodo = (TAMANO_MINI * 3) + 8

        # Raíz (se dibuja con fade también)
        punto_raiz = self.dibujar_mini_tablero(
            centro_arbol_x - ancho_nodo // 2 + self.scroll_x,
            100 + self.scroll_y,
            tablero_a_usar,
            TAMANO_MINI,
            puntaje=0,
            nodo_id="ROOT"
        )

        if estructura_arbol:
            self.dibujar_arbol_recursivo(
                estructura_arbol,
                inicio_arbol_x, fin_arbol_x,
                100 + ESPACIO_VERTICAL_ARBOL,
                punto_raiz
            )

        # Si el modal está abierto, dibuja overlay + ventana del árbol a pantalla completa
        if self.modal_abierto:
            self._dibujar_modal_arbol(estructura_arbol)

        pygame.display.flip()

    # ------------------------------
    # Modal para ver el árbol completo (pantalla completa)
    # ------------------------------
    def _dibujar_modal_arbol(self, estructura_arbol):
        # Fondo translúcido
        overlay = pygame.Surface((ANCHO_VENTANA, ALTO_VENTANA), pygame.SRCALPHA)
        overlay.fill((10, 10, 10, 180))
        self.pantalla.blit(overlay, (0, 0))

        # Caja central
        margin = 40
        caja = pygame.Rect(margin, margin, ANCHO_VENTANA - margin * 2, ALTO_VENTANA - margin * 2)
        pygame.draw.rect(self.pantalla, pygame.Color(30, 30, 60), caja, border_radius=12)

        # Título y cerrar
        titulo = self.fuente_titulo.render("Árbol Completo", True, pygame.Color(COLOR_TEXTO))
        self.pantalla.blit(titulo, (caja.x + 20, caja.y + 12))
        btn_cerrar = pygame.Rect(caja.right - 110, caja.y + 10, 90, 36)
        color_btn = pygame.Color(COLOR_BOTON_HOVER) if btn_cerrar.collidepoint(pygame.mouse.get_pos()) else pygame.Color(COLOR_BOTON)
        pygame.draw.rect(self.pantalla, color_btn, btn_cerrar, border_radius=8)
        self.pantalla.blit(self.fuente_ui.render("Cerrar (Esc)", True, pygame.Color(COLOR_TEXTO)),
                           (btn_cerrar.x + 10, btn_cerrar.y + 8))

        # Área interna donde se debe dibujar el árbol con scroll modal
        inner_x = caja.x + 20
        inner_y = caja.y + 60
        inner_w = caja.width - 40
        inner_h = caja.height - 80

        # Clip para la zona del árbol (para evitar dibujar fuera)
        clip_rect = pygame.Rect(inner_x, inner_y, inner_w, inner_h)
        previous_clip = self.pantalla.get_clip()
        self.pantalla.set_clip(clip_rect)

        # Dibujar raíz en posición con scroll modal
        ancho_nodo = (TAMANO_MINI * 3) + 8
        centro_x = inner_x + inner_w // 2

        # Raíz (modal)
        # usamos fade cache compartida
        punto_raiz = self.dibujar_mini_tablero(
            centro_x - ancho_nodo // 2 + self.modal_scroll_x,
            inner_y + self.modal_scroll_y,
            [" " for _ in range(9)],
            TAMANO_MINI,
            puntaje=0,
            nodo_id="MODAL_ROOT"
        )

        # Dibujar árbol recursivo con offsets del modal
        # Guardamos scroll temporal actual y restauramos al final
        real_scroll_x, real_scroll_y = self.scroll_x, self.scroll_y
        self.scroll_x, self.scroll_y = self.modal_scroll_x, self.modal_scroll_y

        if estructura_arbol:
            self.dibujar_arbol_recursivo(estructura_arbol, inner_x, inner_x + inner_w, inner_y + ESPACIO_VERTICAL_ARBOL, punto_raiz)

        # restaurar scroll
        self.scroll_x, self.scroll_y = real_scroll_x, real_scroll_y

        # restaurar clip
        self.pantalla.set_clip(previous_clip)

        # detectamos clic en cerrar si ocurre (lo maneja obtener_evento_usuario)
        # no retornamos nada; el main loop hace flip luego.

    # ------------------------------
    # EVENTOS (scroll y clics)
    # ------------------------------
    def obtener_evento_usuario(self):
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

            # KEYDOWN: flechas o ESC
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE and self.modal_abierto:
                    self.modal_abierto = False
                if evento.key == pygame.K_UP:
                    # sube árbol / modal (si modal abierto actúa sobre modal)
                    if self.modal_abierto:
                        self.modal_scroll_y += self.modal_scroll_vel
                    else:
                        self.scroll_y += self.scroll_velocidad
                if evento.key == pygame.K_DOWN:
                    if self.modal_abierto:
                        self.modal_scroll_y -= self.modal_scroll_vel
                    else:
                        self.scroll_y -= self.scroll_velocidad
                if evento.key == pygame.K_LEFT:
                    if self.modal_abierto:
                        self.modal_scroll_x += self.modal_scroll_vel
                    else:
                        self.scroll_x += self.scroll_velocidad
                if evento.key == pygame.K_RIGHT:
                    if self.modal_abierto:
                        self.modal_scroll_x -= self.modal_scroll_vel
                    else:
                        self.scroll_x -= self.scroll_velocidad

                # aplicar límites
                self.scroll_x = max(self.scroll_x_min, min(self.scroll_x_max, self.scroll_x))
                self.scroll_y = max(self.scroll_y_min, min(self.scroll_y_max, self.scroll_y))
                self.modal_scroll_x = max(self.scroll_x_min, min(self.scroll_x_max, self.modal_scroll_x))
                # Límites verticales modal un poco más suaves
                self.modal_scroll_y = max(self.scroll_y_min, min(self.scroll_y_max + 800, self.modal_scroll_y))

            # MOUSEWHEEL
            if evento.type == pygame.MOUSEWHEEL:
                mods = pygame.key.get_mods()
                mx, my = pygame.mouse.get_pos()

                # Si modal abierto: controla scroll del modal (rueda siempre para modal)
                if self.modal_abierto:
                    if mods & pygame.KMOD_SHIFT:
                        self.modal_scroll_x += evento.y * self.modal_scroll_vel
                    else:
                        self.modal_scroll_y += evento.y * self.modal_scroll_vel

                    self.modal_scroll_x = max(self.scroll_x_min, min(self.scroll_x_max, self.modal_scroll_x))
                    self.modal_scroll_y = max(self.scroll_y_min, min(self.scroll_y_max + 800, self.modal_scroll_y))
                    continue

                # Si el mouse está sobre la columna CAMINO REAL -> scroll_camino
                camino_x = self.inicio_x + self.ancho_juego + 40
                if camino_x <= mx <= camino_x + self.ancho_camino:
                    self.scroll_camino += evento.y * self.scroll_camino_speed
                    self.scroll_camino = max(self.scroll_camino_min, min(self.scroll_camino_max, self.scroll_camino))
                    continue

                # SHIFT + wheel -> scroll horizontal del árbol
                if mods & pygame.KMOD_SHIFT:
                    self.scroll_x += evento.y * self.scroll_velocidad
                else:
                    self.scroll_y += evento.y * self.scroll_velocidad

                self.scroll_x = max(self.scroll_x_min, min(self.scroll_x_max, self.scroll_x))
                self.scroll_y = max(self.scroll_y_min, min(self.scroll_y_max, self.scroll_y))

            # MOUSEBUTTONDOWN (click)
            if evento.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()

                # Si modal abierto y clic en cerrar
                if self.modal_abierto:
                    # cerrar si clic fuera de la caja o en botón cerrar
                    margin = 40
                    caja = pygame.Rect(margin, margin, ANCHO_VENTANA - margin * 2, ALTO_VENTANA - margin * 2)
                    btn_cerrar = pygame.Rect(caja.right - 110, caja.y + 10, 90, 36)
                    if btn_cerrar.collidepoint(mx, my):
                        self.modal_abierto = False
                        return None
                    # clic fuera de caja no cierra para evitar cierres accidentales
                    return None

                # Nueva partida (botón)
                if self.rect_boton.collidepoint(mx, my):
                    return 'REINICIAR'

                # Botón 'Ver árbol completo'
                camino_x = self.inicio_x + self.ancho_juego + 40
                boton_modal = pygame.Rect(camino_x, ALTO_VENTANA - 90, 180, 40)
                if boton_modal.collidepoint(mx, my):
                    self.modal_abierto = True
                    # reset modal scroll apuntando a top
                    self.modal_scroll_x = 0
                    self.modal_scroll_y = 0
                    return None

                # Clic en tablero principal
                if (self.inicio_x < mx < self.inicio_x + self.ancho_juego and
                        self.inicio_y < my < self.inicio_y + self.ancho_juego):
                    col = (mx - self.inicio_x) // (TAMANO_CASILLA + ESPACIO)
                    fila = (my - self.inicio_y) // (TAMANO_CASILLA + ESPACIO)
                    if 0 <= col < 3 and 0 <= fila < 3:
                        return fila * 3 + col

        return None

    # ------------------------------
    # cerrar
    # ------------------------------
    def cerrar(self):
        pygame.quit()
        sys.exit()



