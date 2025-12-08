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

        ruta_fondo = os.path.join(os.path.dirname(__file__), '..', 'assets', 'fondo_tablero.png')
        try:
            self.fondo_juego = pygame.image.load(ruta_fondo)
            self.fondo_juego = pygame.transform.scale(self.fondo_juego, (ANCHO_VENTANA, ALTO_VENTANA))
        except FileNotFoundError:
            print("AVISO: No se encontró fondo_juego.png. Usando color sólido.")
            self.fondo_juego = None

        # Layout tablero
        self.centro_izq = ANCHO_VENTANA * 0.25
        self.centro_der = ANCHO_VENTANA * 0.75
        self.ancho_juego = (TAMANO_CASILLA * 3) + (ESPACIO * 2) 

        self.inicio_x = int(self.centro_izq - (self.ancho_juego / 2))
        y_arriba = 130
        y_abajo = ALTO_VENTANA - 80
        punto_medio_vertical = (y_arriba + y_abajo) / 2
        self.inicio_y = int(punto_medio_vertical - (self.ancho_juego / 2))

        # Botones
        self.rect_boton = pygame.Rect(0, 0, 200, 50)
        self.rect_boton.center = (self.centro_izq, ALTO_VENTANA - 80)

        self.rect_boton_arbol = pygame.Rect(0, 0, 220, 50)
        self.rect_boton_arbol.center = (self.centro_der, ALTO_VENTANA - 80)

        self.rect_boton_salir = pygame.Rect(0, 0, 140, 50)
        self.rect_boton_salir.bottomright = (ANCHO_VENTANA - 30, ALTO_VENTANA - 30)

        # Camino real ancho fijo
        self.ancho_camino = 220

        self.arrastrando = False
        self.mouse_previo = (0, 0)

        self.tablero_previo = [" "] * 9  # Para comparar y detectar jugadas
        self.animaciones_fichas = {}     # Diccionario {indice: escala_actual}

    # ------------------------------
    # AUXILIAR: Extraer camino lineal del árbol
    # ------------------------------
    def _extraer_camino_lineal(self, arbol):
        """
        Recorre la estructura de árbol buscando los nodos marcados como 'es_camino_ganador'
        para reconstruir la lista lineal que se muestra a la derecha.
        """
        camino = []
        if not arbol:
            return camino
        
        # En el primer nivel (hermanos), buscamos el ganador
        nodo_actual = None
        for nodo in arbol:
            if nodo.get("es_camino_ganador"):
                nodo_actual = nodo
                break
        
        # Si no hay ganador marcado en la raíz, tomamos el primero (fallback)
        if not nodo_actual and arbol:
            nodo_actual = arbol[0]

        # Recorrer hacia abajo
        while nodo_actual:
            camino.append(nodo_actual)
            
            # Buscar el siguiente en las sub_ramas
            siguiente = None
            if nodo_actual.get("sub_ramas"):
                for hijo in nodo_actual["sub_ramas"]:
                    if hijo.get("es_camino_ganador"):
                        siguiente = hijo
                        break
                # Si no encontramos uno marcado, tomamos el primero (fallback visual)
                if not siguiente and nodo_actual["sub_ramas"]:
                    siguiente = nodo_actual["sub_ramas"][0]
            
            nodo_actual = siguiente
            
        return camino

    def _es_turno_ia(self, tablero):
        """Deduce de quién fue el turno basado en el conteo de fichas."""
        x_count = tablero.count("X")
        o_count = tablero.count("O")
        # Si hay más X que O, el último movimiento fue X (IA)
        return x_count > o_count

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
                
            # Determinar si es camino ganador para resaltarlo
            es_camino = nodo.get("es_camino_ganador", False)
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
                lbl_puntaje = self.fuentes['numeros'].render(str(p_val), True, col_p)
                self.pantalla.blit(lbl_puntaje, (pos_x + ancho_nodo_px + 3, pos_y + 10))

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
        Solo muestra la etiqueta de turno y el mini-tablero, sin puntaje.
        """
        if not camino_real:
            return
        
        y = y_inicio + self.scroll_camino
        
        for depth, nodo in enumerate(camino_real):
            # Deducir turno
            es_turno_ia = self._es_turno_ia(nodo["tablero"])
            turno = "IA" if es_turno_ia else "Humano"
            color = (255, 255, 255) if es_turno_ia else (255, 255, 255)
            
            self.pantalla.blit(self.fuentes['ui'].render(turno, True, color), (x_inicio, y))
            y += 20

            # Mini-tablero 
            _, bottom = dibujar_mini_tablero(
                self.pantalla, self.fuentes['mini'],
                x_inicio, y, 
                nodo["tablero"], TAMANO_MINI, 
                self.fade_cache, self.fade_speed, 
                None, id(nodo)
            )
            y = bottom + 20

            if depth < len(camino_real) - 1:
                pygame.draw.line(self.pantalla, pygame.Color(200, 200, 200),
                                 (x_inicio + 40, y - 10), (x_inicio + 40, y + 5), 2)

    # ------------------------------
    # DIBUJAR INTERFAZ (principal)
    # ------------------------------
    def dibujar_interfaz(self, tablero, mensaje, tablero_raiz=None, estructura_arbol=None, camino_real=None):
        """
        Dibuja toda la pantalla.
        """
        # 1. Extraer el camino lineal del árbol (ya que camino_real viene vacío de main)
        camino_visual = self._extraer_camino_lineal(estructura_arbol)

        if self.fondo_juego:
            self.pantalla.blit(self.fondo_juego, (0, 0))
        else:
            self.pantalla.fill(pygame.Color(COLOR_FONDO))

        # --- SECCIÓN IZQUIERDA (TABLERO) ---
        t_tablero = self.fuentes['titulo'].render("TABLERO DEL JUEGO", True, pygame.Color(COLOR_BOTON))
        self.pantalla.blit(t_tablero, t_tablero.get_rect(center=(self.centro_izq, 80)))
        
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

        # Detectar jugada para sonido
        jugada_detectada = False
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

            # Sombra y Casilla
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

        self.dibujar_boton_redondo(self.rect_boton, "Nuevo Juego")

        # --- SECCIÓN DERECHA (HISTORIAL) ---
        t_agente = self.fuentes['subtitulo'].render("Decisiones del Agente", True, pygame.Color(COLOR_BOTON))
        self.pantalla.blit(t_agente, t_agente.get_rect(center=(self.centro_der, 80)))

        altura_clip = ALTO_VENTANA - 140 - 140 
        clip_rect = pygame.Rect(ANCHO_VENTANA//2, 140, ANCHO_VENTANA//2, altura_clip)
        self.pantalla.set_clip(clip_rect)

        # Dibujamos el camino reconstruido
        self.dibujar_camino_real(camino_visual, self.centro_der - 100, 160)
            
        self.pantalla.set_clip(None)

        self.dibujar_boton_redondo(self.rect_boton_arbol, "Ver árbol completo")
        self.dibujar_boton_redondo(self.rect_boton_salir, "Salir")

        # --- MODAL (Overlay) ---
        if self.modal_abierto:
            self._dibujar_modal_arbol(estructura_arbol)

        pygame.display.flip()

    # --------------------
    # Modal para ver el árbol completo
    # --------------------
    def _dibujar_modal_arbol(self, estructura_arbol):
        overlay = pygame.Surface((ANCHO_VENTANA, ALTO_VENTANA), pygame.SRCALPHA)
        overlay.fill((10, 10, 10, 220)) 
        self.pantalla.blit(overlay, (0, 0))

        margin = 40
        caja = pygame.Rect(margin, margin, ANCHO_VENTANA - margin * 2, ALTO_VENTANA - margin * 2)
        pygame.draw.rect(self.pantalla, pygame.Color("#202040"), caja, border_radius=12)
        pygame.draw.rect(self.pantalla, pygame.Color(COLOR_LINEA), caja, width=2, border_radius=12)

        titulo = self.fuentes['subtitulo'].render("Árbol Completo de Decisiones del Agente", True, pygame.Color(COLOR_TEXTO))
        titulo_rect = titulo.get_rect(center=(caja.centerx, caja.y + 25))
        self.pantalla.blit(titulo, titulo_rect)
        
        btn_cerrar = pygame.Rect(caja.right - 160, caja.y + 10, 140, 50)
        color_btn = pygame.Color(COLOR_BOTON_HOVER) if btn_cerrar.collidepoint(pygame.mouse.get_pos()) else pygame.Color(COLOR_BOTON)
        pygame.draw.rect(self.pantalla, color_btn, btn_cerrar, border_radius=12)   
        txt_cerrar = self.fuentes['ui'].render("Cerrar (Esc)", True, pygame.Color(COLOR_TEXTO))
        rect_txt = txt_cerrar.get_rect(center=btn_cerrar.center) 
        self.pantalla.blit(txt_cerrar, rect_txt)     

        inner_x = caja.x + 20
        inner_y = caja.y + 60
        inner_w = caja.width - 40
        inner_h = caja.height - 80
        rect_area_dibujo = pygame.Rect(inner_x, inner_y, inner_w, inner_h)

        previous_clip = self.pantalla.get_clip()
        self.pantalla.set_clip(rect_area_dibujo)

        backup_x, backup_y = self.scroll_x, self.scroll_y
        self.scroll_x, self.scroll_y = self.modal_scroll_x, self.modal_scroll_y

        # Dibujar árbol recursivo usando la lista completa de hermanos de nivel 0
        if estructura_arbol:
            self.dibujar_arbol_recursivo(estructura_arbol, inner_x, inner_x + inner_w, inner_y + 50)

        self.scroll_x, self.scroll_y = backup_x, backup_y
        self.pantalla.set_clip(previous_clip)

    def obtener_evento_usuario(self):
        return manejar_eventos(self)
    
    def dibujar_boton_redondo(self, rect, texto):
        mouse_pos = pygame.mouse.get_pos()
        es_hover = rect.collidepoint(mouse_pos)
        
        color_base = (44, 44, 84)
        color_hover = (70, 70, 130)
        color_sombra = (79, 87, 175)
        
        color_actual = color_hover if es_hover else color_base
        elevacion = 4 if es_hover else 0
        
        rect_sombra = rect.copy()
        rect_sombra.y += 6 
        pygame.draw.rect(self.pantalla, color_sombra, rect_sombra, border_radius=25)
        
        rect_visual = rect.copy()
        rect_visual.y -= elevacion
        pygame.draw.rect(self.pantalla, color_actual, rect_visual, border_radius=25)
        
        txt_surf = self.fuentes['boton'].render(texto, True, (255, 255, 255))
        txt_rect = txt_surf.get_rect(center=rect_visual.center)
        self.pantalla.blit(txt_surf, txt_rect)

    def cerrar(self):
        pygame.quit()
        sys.exit()