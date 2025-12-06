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
COLOR_CASILLA_SOMBRA_3D = "#353b75"
COLOR_CASILLA_HOVER = "#533483"

# --- DIMENSIONES ---
ANCHO_VENTANA = 1260
ALTO_VENTANA = 760
TAMANO_CASILLA = 105
TAMANO_MINI = 26
ESPACIO = 20
ESPACIO_VERTICAL_ARBOL = 130
PADDING_TABLERO = 35
PADDING_LATERAL = 45

# --- ANIMACIONES ---
SECUENCIA_PLOP = [0.1, 0.5, 1.1, 1.35, 1.15, 0.95, 1.02, 1.0] 

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
        ruta_fuente = os.path.join(os.path.dirname(__file__), '..', 'assets', 'Boogaloo-Regular.ttf')

        try:
            self.fuente_titulo = pygame.font.Font(ruta_fuente, 45) 
            self.fuente_sub_tutilo = pygame.font.Font(ruta_fuente, 35) 
            self.fuente_ficha  = pygame.font.Font(ruta_fuente, 65)
            self.fuente_boton  = pygame.font.Font(ruta_fuente, 22)

            self.fuente_mini   = pygame.font.Font(ruta_fuente, 18)
            self.fuente_ui     = pygame.font.Font(ruta_fuente, 16)
        except FileNotFoundError:
            print("AVISO: No se encontró Boogaloo-Regular.ttf en /assets. Usando fuente del sistema.")
            self.fuente_titulo = pygame.font.SysFont("Arial", 32, bold=True)
            self.fuente_ficha  = pygame.font.SysFont("Arial", 60, bold=True)
            self.fuente_boton  = pygame.font.SysFont("Arial", 18, bold=True)
            self.fuente_mini   = pygame.font.SysFont("Arial", 16, bold=True)
            self.fuente_ui     = pygame.font.SysFont("Arial", 14)


        # Layout tablero
        self.centro_izq = ANCHO_VENTANA * 0.25
        self.centro_der = ANCHO_VENTANA * 0.75
        self.ancho_juego = (TAMANO_CASILLA * 3) + (ESPACIO * 2) 

        self.inicio_x = int(self.centro_izq - (self.ancho_juego / 2))
        y_arriba = 130
        y_abajo = ALTO_VENTANA - 80
        punto_medio_vertical = (y_arriba + y_abajo) / 2
        self.inicio_y = int(punto_medio_vertical - (self.ancho_juego / 2))

        # Boton reiniciar
        self.rect_boton = pygame.Rect(0, 0, 200, 50)
        self.rect_boton.center = (self.centro_izq, ALTO_VENTANA - 80)

        # Boton ver arbol
        self.rect_boton_arbol = pygame.Rect(0, 0, 220, 50)
        self.rect_boton_arbol.center = (self.centro_der, ALTO_VENTANA - 80)

        # Camino real ancho fijo
        self.ancho_camino = 220

        self.arrastrando = False
        self.mouse_previo = (0, 0)

        self.tablero_previo = [" "] * 9  # Para comparar y detectar jugadas
        self.animaciones_fichas = {}     # Diccionario {indice: escala_actual}

    # ------------------------------
    # Mini-tablero con fade-in
    # ------------------------------
    def dibujar_mini_tablero(self, x, y, tablero_data, tamano, puntaje=None, nodo_id=None, es_camino=False):
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

        if es_camino:
            color_borde = "#33ff33"

        if puntaje is not None:
            if puntaje > 0:
                color_borde = "#33ff33"
            elif puntaje < 0:
                color_borde = "#ff3333"
            else:
                color_borde = "#cccccc"

        pygame.draw.rect(surf, pygame.Color(color_borde), (0, 0, ancho_total, ancho_total), border_radius=4)
        pygame.draw.rect(surf, pygame.Color(COLOR_TABLERO), (2, 2, ancho_total - 4, ancho_total - 4), border_radius=4)

        grosor_borde = 3 if es_camino else 2
        pygame.draw.rect(surf, pygame.Color(COLOR_TABLERO), 
                        (grosor_borde, grosor_borde, ancho_total - (grosor_borde*2), ancho_total - (grosor_borde*2)), 
                        border_radius=4)

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
        if not nodos: return

        cantidad = len(nodos)
        ancho_nodo_px = (TAMANO_MINI * 3) + 8
        
        # Espacio fijo entre nodos hermanos
        ESPACIO_ENTRE_HERMANOS = 140 
        
        centro_area = (x_min + x_max) / 2
        ancho_total_grupo = cantidad * ESPACIO_ENTRE_HERMANOS
        x_inicio = centro_area - (ancho_total_grupo / 2)

        for i, nodo in enumerate(nodos):
            center_x_nodo = x_inicio + (i * ESPACIO_ENTRE_HERMANOS) + (ESPACIO_ENTRE_HERMANOS / 2)
            
            # Posición final
            pos_x = center_x_nodo - (ancho_nodo_px / 2) + self.scroll_x
            pos_y = y_nivel + self.scroll_y
            
            punto_conexion_top = (pos_x + ancho_nodo_px / 2, pos_y)

            # --- DIBUJAR LÍNEAS ---
            if padre_pos:
                padre_x, padre_y = padre_pos
                hijo_x, hijo_y = punto_conexion_top
                
                mid_y = (padre_y + hijo_y) // 2

                pygame.draw.line(self.pantalla, pygame.Color(COLOR_LINEA), 
                                 (padre_x, padre_y), (padre_x, mid_y), 2)
                
                pygame.draw.line(self.pantalla, pygame.Color(COLOR_LINEA), 
                                 (padre_x, mid_y), (hijo_x, mid_y), 2)
                
                pygame.draw.line(self.pantalla, pygame.Color(COLOR_LINEA), 
                                 (hijo_x, mid_y), (hijo_x, hijo_y), 2)
                
            es_camino = nodo.get("es_camino", False)
            nodo_id = id(nodo)
            punto_conexion_bottom = self.dibujar_mini_tablero(
                pos_x, pos_y, nodo["tablero"], TAMANO_MINI, nodo.get("puntaje"), nodo_id, es_camino=es_camino
            )

            p_val = nodo.get("puntaje")
            if p_val is not None:
                col_p = pygame.Color("#ccffcc") if p_val > 0 else (pygame.Color("#ffcccc") if p_val < 0 else pygame.Color("#ffffff"))
                self.pantalla.blit(self.fuente_ui.render(str(p_val), True, col_p),
                                   (pos_x + ancho_nodo_px + 3, pos_y + 10))

            if nodo.get("sub_ramas"):
                ancho_virtual = 4000 
                self.dibujar_arbol_recursivo(
                    nodo["sub_ramas"], 
                    center_x_nodo - ancho_virtual,
                    center_x_nodo + ancho_virtual, 
                    y_nivel + ESPACIO_VERTICAL_ARBOL, 
                    punto_conexion_bottom
                )
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
            # etiqueta MAX/MIN
            turno = "MAX (X)" if nodo["es_turno_ia"] else "MIN (O)"
            color = (180, 220, 255) if nodo["es_turno_ia"] else (255, 200, 220)
            self.pantalla.blit(self.fuente_ui.render(turno, True, color), (x_inicio, y))
            y += 20

            # puntaje
            p = nodo.get("puntaje", 0)
            col_p = pygame.Color("#ccffcc") if p > 0 else (pygame.Color("#ffcccc") if p < 0 else pygame.Color("#ffffff"))
            self.pantalla.blit(self.fuente_ui.render(f"Puntaje: {p}", True, col_p), (x_inicio, y))
            y += 20

            # mini-tablero idéntico al del árbol
            _, bottom = self.dibujar_mini_tablero(x_inicio, y, nodo["tablero"],
                                                  TAMANO_MINI, p, id(nodo))
            y = bottom + 20   # espacio después del tablero

            # línea vertical
            if depth < len(camino_real) - 1:
                pygame.draw.line(self.pantalla, pygame.Color(200, 200, 200),
                                 (x_inicio + 40, y - 10), (x_inicio + 40, y + 5), 2)

    # ------------------------------
    # DIBUJAR INTERFAZ (principal)
    # ------------------------------
    def dibujar_interfaz(self, tablero, mensaje, tablero_raiz=None, estructura_arbol=None, camino_real=None):
        self.pantalla.fill(pygame.Color(COLOR_FONDO))
        """
        dibujar_interfaz ahora acepta camino_real (lista de nodos) además del árbol.
        """
        mouse_pos = pygame.mouse.get_pos()

                # --- SECCIÓN IZQUIERDA ---
        # Titulo
        t_tablero = self.fuente_titulo.render("Tablero del juego", True, pygame.Color(COLOR_BOTON))
        self.pantalla.blit(t_tablero, t_tablero.get_rect(center=(self.centro_izq, 80)))
        
        # Subtitulo 
        t_turno = self.fuente_sub_tutilo.render(mensaje, True, pygame.Color(COLOR_X))
        self.pantalla.blit(t_turno, t_turno.get_rect(center=(self.centro_izq, 130)))

        ancho_fondo = self.ancho_juego + (PADDING_LATERAL * 2)
        alto_fondo = self.ancho_juego + (PADDING_TABLERO * 2)
        
        fondo_rect = pygame.Rect(
            self.inicio_x - PADDING_LATERAL, 
            self.inicio_y - PADDING_TABLERO, 
            ancho_fondo, 
            alto_fondo
        )
        
        pygame.draw.rect(self.pantalla, pygame.Color(COLOR_TABLERO), fondo_rect, border_radius=45)


        # DETECTAR CAMBIOS
        for i in range(9):
            if self.tablero_previo[i] == " " and tablero[i] != " ":
                self.animaciones_fichas[i] = 0 
        
        self.tablero_previo = list(tablero)

        for i in range(9):
            fila = i // 3
            col = i % 3
            x = self.inicio_x + col * (TAMANO_CASILLA + ESPACIO)
            y = self.inicio_y + fila * (TAMANO_CASILLA + ESPACIO)

            rect_sombra = pygame.Rect(x, y + 10, TAMANO_CASILLA, TAMANO_CASILLA)
            pygame.draw.rect(self.pantalla, pygame.Color(COLOR_CASILLA_SOMBRA_3D), rect_sombra, border_radius=25)

            casilla_rect = pygame.Rect(x, y, TAMANO_CASILLA, TAMANO_CASILLA)
            pygame.draw.rect(self.pantalla, pygame.Color(COLOR_CASILLA), casilla_rect, border_radius=25)

            if tablero[i] != " ":
                color = pygame.Color(COLOR_X if tablero[i] == "X" else COLOR_O)
                txt = self.fuente_ficha.render(tablero[i], True, color)

                escala = 1.0

                if i in self.animaciones_fichas:
                    frame_actual = int(self.animaciones_fichas[i])
                    
                    if frame_actual < len(SECUENCIA_PLOP):
                        escala = SECUENCIA_PLOP[frame_actual]
                        self.animaciones_fichas[i] += 1 
                    else:
                        del self.animaciones_fichas[i]
                        escala = 1.0

                if escala != 1.0:
                    txt = pygame.transform.rotozoom(txt, 0, escala)

                rect_texto = txt.get_rect(center=(x + TAMANO_CASILLA / 2, y + TAMANO_CASILLA / 2))
                self.pantalla.blit(txt, rect_texto)

        # BOTÓN Nueva partida
        mouse_pos = pygame.mouse.get_pos()
        color_btn = pygame.Color(COLOR_BOTON_HOVER) if self.rect_boton.collidepoint(mouse_pos) else pygame.Color(COLOR_BOTON)
        pygame.draw.rect(self.pantalla, color_btn, self.rect_boton, border_radius=15)
        txt_btn = self.fuente_boton.render("Nuevo Juego", True, pygame.Color(COLOR_TEXTO))
        self.pantalla.blit(txt_btn, txt_btn.get_rect(center=self.rect_boton.center))

        # --- SECCIÓN DERECHA ---
        t_agente = self.fuente_titulo.render("Decisiones del Agente", True, pygame.Color(COLOR_BOTON))
        self.pantalla.blit(t_agente, t_agente.get_rect(center=(self.centro_der, 80)))

        altura_clip = ALTO_VENTANA - 140 - 140 
        clip_rect = pygame.Rect(ANCHO_VENTANA//2, 140, ANCHO_VENTANA//2, altura_clip)
        self.pantalla.set_clip(clip_rect)

        y_lista = 160 + self.scroll_camino
        if camino_real:
            for i, nodo in enumerate(camino_real):
                # Línea conectora
                if i > 0:
                    pygame.draw.line(self.pantalla, pygame.Color(COLOR_LINEA), (self.centro_der, y_lista - 30), (self.centro_der, y_lista), 2)

                lbl = "IA" if nodo.get("es_turno_ia") else "TÚ"
                self.pantalla.blit(self.fuente_ui.render(lbl, True, pygame.Color(COLOR_TEXTO)), (self.centro_der + 50, y_lista))

                ancho_n = (TAMANO_MINI * 3) + 8
                _, bottom = self.dibujar_mini_tablero(self.centro_der - ancho_n//2, y_lista, nodo["tablero"], TAMANO_MINI, nodo.get("puntaje"), id(nodo))
                y_lista = bottom + 40
            
        self.pantalla.set_clip(None)

        # Botón Ver Árbol Completo
        color_bm = pygame.Color(COLOR_BOTON_HOVER) if self.rect_boton_arbol.collidepoint(mouse_pos) else pygame.Color(COLOR_BOTON)
        
        pygame.draw.rect(self.pantalla, color_bm, self.rect_boton_arbol, border_radius=15)
        txt_bm = self.fuente_boton.render("Ver árbol completo", True, pygame.Color(COLOR_TEXTO))
        self.pantalla.blit(txt_bm, txt_bm.get_rect(center=self.rect_boton_arbol.center))

        # --- MODAL (Overlay) ---
        if self.modal_abierto:
            self._dibujar_modal_arbol(estructura_arbol)

        pygame.display.flip()

    # --------------------
    # Modal para ver el árbol completo (pantalla completa)
    # ------------------------------
    def _dibujar_modal_arbol(self, estructura_arbol):
        # Fondo translúcido
        overlay = pygame.Surface((ANCHO_VENTANA, ALTO_VENTANA), pygame.SRCALPHA)
        overlay.fill((10, 10, 10, 220)) 
        self.pantalla.blit(overlay, (0, 0))

        # Caja central
        margin = 40
        caja = pygame.Rect(margin, margin, ANCHO_VENTANA - margin * 2, ALTO_VENTANA - margin * 2)
        pygame.draw.rect(self.pantalla, pygame.Color("#202040"), caja, border_radius=12) # Fondo caja un poco diferente
        pygame.draw.rect(self.pantalla, pygame.Color(COLOR_LINEA), caja, width=2, border_radius=12)

        # Título y cerrar
        titulo = self.fuente_sub_tutilo.render("Árbol Completo de Decisiones del Agente", True, pygame.Color(COLOR_TEXTO))
        titulo_rect = titulo.get_rect(center=(caja.centerx, caja.y + 25))
        self.pantalla.blit(titulo, titulo_rect)
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
        rect_area_dibujo = pygame.Rect(inner_x, inner_y, inner_w, inner_h)

        # Clip para la zona del árbol (para evitar dibujar fuera)
        previous_clip = self.pantalla.get_clip()
        self.pantalla.set_clip(rect_area_dibujo)

        backup_x, backup_y = self.scroll_x, self.scroll_y
        self.scroll_x, self.scroll_y = self.modal_scroll_x, self.modal_scroll_y

        # Dibujar raíz en posición con scroll modal
        ancho_nodo = (TAMANO_MINI * 3) + 8
        
        # Raíz (modal)
        # usamos fade cache compartida
        centro_x = inner_x + inner_w // 2
        punto_raiz = self.dibujar_mini_tablero(
            centro_x - ancho_nodo // 2 + self.scroll_x,
            inner_y + self.scroll_y,
            [" "]*9, TAMANO_MINI, 0, "MODAL_ROOT"
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

            # --- ARRASTRE CON MOUSE ---
            if evento.type == pygame.MOUSEMOTION:
                if self.modal_abierto and self.arrastrando:
                    mx, my = pygame.mouse.get_pos()
                    dx = mx - self.mouse_previo[0]
                    dy = my - self.mouse_previo[1]
                    self.modal_scroll_x += dx
                    self.modal_scroll_y += dy
                    self.mouse_previo = (mx, my)

            if evento.type == pygame.MOUSEBUTTONUP:
                self.arrastrando = False

            # KEYDOWN: flechas o ESC
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE and self.modal_abierto:
                    self.modal_abierto = False

                # Flechas: siempre mueven la lista (scroll_camino)
                if not self.modal_abierto:
                    if evento.key == pygame.K_UP:
                        self.scroll_camino -= self.scroll_camino_speed
                    if evento.key == pygame.K_DOWN:
                        self.scroll_camino += self.scroll_camino_speed
                    if evento.key == pygame.K_LEFT:
                        self.scroll_x += self.scroll_velocidad
                    if evento.key == pygame.K_RIGHT:
                        self.scroll_x -= self.scroll_velocidad

                # Limites
                self.scroll_camino = max(self.scroll_camino_min, min(self.scroll_camino_max, self.scroll_camino))
                self.scroll_x = max(self.scroll_x_min, min(self.scroll_x_max, self.scroll_x))
            
            # MOUSEWHEEL
            if evento.type == pygame.MOUSEWHEEL:
                mx, my = pygame.mouse.get_pos()

                if self.modal_abierto:
                    # modal scroll
                    if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                        self.modal_scroll_x += evento.y * self.modal_scroll_vel
                    else:
                        self.modal_scroll_y += evento.y * self.modal_scroll_vel
                    # Limites wheel modal
                    self.modal_scroll_x = max(self.scroll_x_min, min(self.scroll_x_max, self.modal_scroll_x))
                    self.modal_scroll_y = max(self.scroll_y_min, min(self.scroll_y_max + 800, self.modal_scroll_y))
                    continue

                # Mitad derecha → mueve la lista
                if mx > ANCHO_VENTANA // 2:
                    self.scroll_camino += evento.y * self.scroll_camino_speed
                    self.scroll_camino = max(self.scroll_camino_min, min(self.scroll_camino_max, self.scroll_camino))
                    continue

                # resto de la rueda (árbol horizontal)
                if pygame.key.get_mods() & pygame.KMOD_SHIFT:
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
                    
                    # Si clic en la caja (y no en cerrar), iniciar arrastre
                    if caja.collidepoint(mx, my):
                        self.arrastrando = True
                        self.mouse_previo = (mx, my)
                    
                    return None

                # Nueva partida (botón)
                if self.rect_boton.collidepoint(mx, my):
                    return 'REINICIAR'

                # Botón 'Ver árbol completo'
                if self.rect_boton_arbol.collidepoint(mx, my):
                    self.modal_abierto = True
                    # Reiniciar posición al centro
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
        
        # Limites generales al final para asegurar que el arrastre no se pierda
        self.modal_scroll_y = max(self.scroll_y_min, min(self.scroll_y_max + 1500, self.modal_scroll_y))

        return None

    # ------------------------------
    # cerrar
    # ------------------------------
    def cerrar(self):
        pygame.quit()
        sys.exit()



