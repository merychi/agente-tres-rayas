# ui/interface.py
import pygame
import sys
import os

from ui.config import *
from ui.components import *
from ui.events import *
from ui.assets import *

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class InterfazGrafica:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        pygame.mixer.init()
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

        # Fuentes y sonido
        self.fuentes = cargar_fuentes()
        self.sonidos = cargar_sonidos()
        iniciar_musica_fondo()

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

                pygame.draw.line(self.pantalla, pygame.Color(COLOR_LINEA), (padre_x, padre_y), (padre_x, mid_y), 2)
                pygame.draw.line(self.pantalla, pygame.Color(COLOR_LINEA), (padre_x, mid_y), (hijo_x, mid_y), 2)
                pygame.draw.line(self.pantalla, pygame.Color(COLOR_LINEA), (hijo_x, mid_y), (hijo_x, hijo_y), 2)
                
            es_camino = nodo.get("es_camino", False)
            nodo_id = id(nodo)
            
            punto_conexion_bottom = dibujar_mini_tablero(
                self.pantalla,         
                self.fuentes['mini'],       
                pos_x, pos_y, 
                nodo["tablero"], 
                TAMANO_MINI, 
                self.fade_cache,        
                self.fade_speed,        
                nodo.get("puntaje"), 
                nodo_id, 
                es_camino=es_camino
            )

            p_val = nodo.get("puntaje")
            if p_val is not None:
                col_p = pygame.Color("#ccffcc") if p_val > 0 else (pygame.Color("#ffcccc") if p_val < 0 else pygame.Color("#ffffff"))
                self.pantalla.blit(self.fuentes['ui'].render(str(p_val), True, col_p),
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
            self.pantalla.blit(self.fuentes['ui'].render(turno, True, color), (x_inicio, y))
            y += 20

            p = nodo.get("puntaje", 0)
            col_p = pygame.Color("#ccffcc") if p > 0 else (pygame.Color("#ffcccc") if p < 0 else pygame.Color("#ffffff"))
            self.pantalla.blit(self.fuentes['ui'].render(f"Puntaje: {p}", True, col_p), (x_inicio, y))
            y += 20

            _, bottom = dibujar_mini_tablero(
                self.pantalla, self.fuentes['mini'],
                x_inicio, y, 
                nodo["tablero"], TAMANO_MINI, 
                self.fade_cache, self.fade_speed, 
                p, id(nodo)
            )
            y = bottom + 20

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
        t_tablero = self.fuentes['titulo'].render("Tablero del juego", True, pygame.Color(COLOR_BOTON))
        self.pantalla.blit(t_tablero, t_tablero.get_rect(center=(self.centro_izq, 80)))
        
        # Subtitulo 
        t_turno = self.fuentes['subtitulo'].render(mensaje, True, pygame.Color(COLOR_X))
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

        jugada_detectada = False
        # DETECTAR CAMBIOS
        for i in range(9):
            if self.tablero_previo[i] == " " and tablero[i] != " ":
                self.animaciones_fichas[i] = 0 
                jugada_detectada = True

        if jugada_detectada and 'colocar' in self.sonidos:
            self.sonidos['colocar'].play()        
        
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
                txt = self.fuentes['ficha'].render(tablero[i], True, color)

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
        txt_btn = self.fuentes['boton'].render("Nuevo Juego", True, pygame.Color(COLOR_TEXTO))
        self.pantalla.blit(txt_btn, txt_btn.get_rect(center=self.rect_boton.center))

        # --- SECCIÓN DERECHA ---
        t_agente = self.fuentes['titulo'].render("Decisiones del Agente", True, pygame.Color(COLOR_BOTON))
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
                self.pantalla.blit(self.fuentes['ui'].render(lbl, True, pygame.Color(COLOR_TEXTO)), (self.centro_der + 50, y_lista))

                ancho_n = (TAMANO_MINI * 3) + 8
                _, bottom = dibujar_mini_tablero(
                    self.pantalla, self.fuentes['mini'],
                    self.centro_der - ancho_n//2, y_lista, 
                    nodo["tablero"], TAMANO_MINI, 
                    self.fade_cache, self.fade_speed, 
                    nodo.get("puntaje"), id(nodo)
                )
                y_lista = bottom + 40                
            
        self.pantalla.set_clip(None)

        # Botón Ver Árbol Completo
        color_bm = pygame.Color(COLOR_BOTON_HOVER) if self.rect_boton_arbol.collidepoint(mouse_pos) else pygame.Color(COLOR_BOTON)
        
        pygame.draw.rect(self.pantalla, color_bm, self.rect_boton_arbol, border_radius=15)
        txt_bm = self.fuentes['boton'].render("Ver árbol completo", True, pygame.Color(COLOR_TEXTO))
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
        pygame.draw.rect(self.pantalla, pygame.Color("#202040"), caja, border_radius=12)
        pygame.draw.rect(self.pantalla, pygame.Color(COLOR_LINEA), caja, width=2, border_radius=12)

        # Título y cerrar
        titulo = self.fuentes['subtitulo'].render("Árbol Completo de Decisiones del Agente", True, pygame.Color(COLOR_TEXTO))
        titulo_rect = titulo.get_rect(center=(caja.centerx, caja.y + 25))
        self.pantalla.blit(titulo, titulo_rect)
        
        btn_cerrar = pygame.Rect(caja.right - 110, caja.y + 10, 90, 36)
        color_btn = pygame.Color(COLOR_BOTON_HOVER) if btn_cerrar.collidepoint(pygame.mouse.get_pos()) else pygame.Color(COLOR_BOTON)
        pygame.draw.rect(self.pantalla, color_btn, btn_cerrar, border_radius=8)
        self.pantalla.blit(self.fuentes['ui'].render("Cerrar (Esc)", True, pygame.Color(COLOR_TEXTO)), (btn_cerrar.x + 10, btn_cerrar.y + 8))

        # Área interna
        inner_x = caja.x + 20
        inner_y = caja.y + 60
        inner_w = caja.width - 40
        inner_h = caja.height - 80
        rect_area_dibujo = pygame.Rect(inner_x, inner_y, inner_w, inner_h)

        # Clip y Scroll
        previous_clip = self.pantalla.get_clip()
        self.pantalla.set_clip(rect_area_dibujo)

        backup_x, backup_y = self.scroll_x, self.scroll_y
        self.scroll_x, self.scroll_y = self.modal_scroll_x, self.modal_scroll_y

        ancho_nodo = (TAMANO_MINI * 3) + 8
        centro_x = inner_x + inner_w // 2

        # --- DIBUJAR RAÍZ DEL MODAL (ACTUALIZADO) ---
        punto_raiz = dibujar_mini_tablero(
            self.pantalla, self.fuentes['mini'],
            centro_x - ancho_nodo // 2 + self.scroll_x,
            inner_y + self.scroll_y,
            [" "]*9, TAMANO_MINI, 
            self.fade_cache, self.fade_speed, 
            0, "MODAL_ROOT"
        )

        if estructura_arbol:
            self.dibujar_arbol_recursivo(estructura_arbol, inner_x, inner_x + inner_w, inner_y + ESPACIO_VERTICAL_ARBOL, punto_raiz)

        # Restaurar
        self.scroll_x, self.scroll_y = backup_x, backup_y
        self.pantalla.set_clip(previous_clip)

        # detectamos clic en cerrar si ocurre (lo maneja obtener_evento_usuario)
        # no retornamos nada; el main loop hace flip luego.

    def obtener_evento_usuario(self):
        # Le pasamos 'self' para que la función externa pueda modificar
        # los atributos de esta clase (scrolls, flags, etc.)
        return manejar_eventos(self)

    # ------------------------------
    # cerrar
    # ------------------------------
    def cerrar(self):
        pygame.quit()
        sys.exit()