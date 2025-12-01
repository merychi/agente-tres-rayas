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
COLOR_WIN_PATH = "#FFD700" 

# --- DIMENSIONES ---
ANCHO_VENTANA = 1200 
ALTO_VENTANA = 760
TAMANO_CASILLA = 90
TAMANO_MINI = 26      
ESPACIO_VERTICAL_ARBOL = 120 
LIMITE_IZQUIERDO_ARBOL = 380 

class InterfazGrafica:
    def __init__(self):
        pygame.init()
        self.pantalla = pygame.display.set_mode((ANCHO_VENTANA, ALTO_VENTANA))
        pygame.display.set_caption("Tres en Raya - Minimax")
        
        self.fuente_titulo = pygame.font.SysFont("Arial", 28, bold=True)
        self.fuente_ficha = pygame.font.SysFont("Arial", 60, bold=True)
        self.fuente_mini = pygame.font.SysFont("Arial", 16, bold=True)
        self.fuente_ui = pygame.font.SysFont("Arial", 14)
        self.fuente_flechas = pygame.font.SysFont("Arial", 30, bold=True)

        self.ancho_juego = (TAMANO_CASILLA * 3) + 40
        self.inicio_x = 50
        self.inicio_y = 150
        self.rect_boton = pygame.Rect(50, ALTO_VENTANA - 90, 200, 50)

        self.scroll_y = 0
        self.rect_up = pygame.Rect(ANCHO_VENTANA - 50, ALTO_VENTANA // 2 - 60, 40, 40)
        self.rect_down = pygame.Rect(ANCHO_VENTANA - 50, ALTO_VENTANA // 2 + 10, 40, 40)

    def dibujar_mini_tablero(self, x, y, nodo_data, tamano):
        padding = 2
        ancho_total = (tamano * 3) + (padding * 4)
        tablero = nodo_data["tablero"]
        es_ganador = nodo_data.get("es_camino_ganador", False)
        puntaje = nodo_data.get("puntaje", "")

        if es_ganador:
            color_borde = COLOR_WIN_PATH
            grosor = 3
            pygame.draw.rect(self.pantalla, "#FFFFAA", (x-2, y-2, ancho_total+4, ancho_total+4), border_radius=5)
        else:
            color_borde = "#5555aa"
            grosor = 1

        pygame.draw.rect(self.pantalla, color_borde, (x, y, ancho_total, ancho_total), border_radius=4)
        pygame.draw.rect(self.pantalla, COLOR_TABLERO, (x+grosor, y+grosor, ancho_total-(grosor*2), ancho_total-(grosor*2)), border_radius=4)

        for i in range(9):
            fila, col = i // 3, i % 3
            px = x + padding + col * (tamano + padding)
            py = y + padding + fila * (tamano + padding)
            pygame.draw.rect(self.pantalla, COLOR_CASILLA, (px, py, tamano, tamano), border_radius=2)
            if tablero[i] != " ":
                c = COLOR_X if tablero[i] == "X" else COLOR_O
                t = self.fuente_mini.render(tablero[i], True, c)
                self.pantalla.blit(t, t.get_rect(center=(px + tamano/2, py + tamano/2)))
        
        if es_ganador and str(puntaje) != "":
             self.pantalla.blit(self.fuente_ui.render(str(puntaje), True, COLOR_WIN_PATH), (x + ancho_total - 10, y - 15))
        
        return (x + ancho_total // 2, y + ancho_total)

    def dibujar_arbol_unificado(self, trayectoria, arbol_futuro, centro_x):
        # 1. APLANAR
        niveles_a_dibujar = []
        if trayectoria:
            for paso in trayectoria: niveles_a_dibujar.append(paso)
        
        if arbol_futuro:
             mejor_futuro = None
             for n in arbol_futuro:
                 if n.get("es_camino_ganador"):
                     mejor_futuro = n; break
             if not mejor_futuro and arbol_futuro: mejor_futuro = arbol_futuro[0]

             if mejor_futuro:
                 niveles_a_dibujar.append({"elegido": mejor_futuro, "hermanos": arbol_futuro})
                 if mejor_futuro.get("sub_ramas"):
                     siguientes = mejor_futuro["sub_ramas"]
                     mejor_sig = None
                     for n in siguientes:
                         if n.get("es_camino_ganador"): mejor_sig = n; break
                     if not mejor_sig and siguientes: mejor_sig = siguientes[0]
                     niveles_a_dibujar.append({"elegido": mejor_sig, "hermanos": siguientes})

        # 2. SCROLL
        y_base = 100
        y_inicio = y_base - self.scroll_y

        ultimo_punto_conexion = None
        ancho_nodo = (TAMANO_MINI * 3) + 8
        espacio_h = 8 
        
        # Variable para recordar dónde cayó la columna dorada
        x_columna_vertebral = centro_x

        for i, nivel in enumerate(niveles_a_dibujar):
            pos_y = y_inicio + (i * ESPACIO_VERTICAL_ARBOL)
            
            if pos_y < -50: 
                ultimo_punto_conexion = (x_columna_vertebral, pos_y + ancho_nodo)
                continue
            if pos_y > ALTO_VENTANA + 50: break 

            elegido = nivel["elegido"]
            hermanos_raw = nivel["hermanos"]

            # === FILTRO DE VISUALIZACIÓN (EL EMBUDO) ===
            # Si es Nivel 0 o 1, mostramos todos.
            # Si es Nivel 2 o superior, SOLO mostramos al elegido (borramos a los otros).
            if i <= 1:
                hermanos = hermanos_raw
            else:
                hermanos = [elegido] # Solo queda el camino dorado

            # Ordenar (solo relevante para el nivel 1)
            hermanos = sorted(hermanos, key=lambda x: x["movimiento"] if x["movimiento"] is not None else -1)

            # === ALINEACIÓN ===
            
            if i <= 1:
                # Lógica de ABANICO (Nivel 1)
                # Centramos el bloque entero en la pantalla
                cantidad = len(hermanos)
                ancho_total_bloque = (cantidad * ancho_nodo) + ((cantidad - 1) * espacio_h)
                start_x = centro_x - (ancho_total_bloque / 2)
                
                # Barras horizontales
                primer_hijo_cx = start_x + (ancho_nodo / 2)
                ultimo_hijo_cx = start_x + ancho_total_bloque - (ancho_nodo / 2)
                mid_y = pos_y - (ESPACIO_VERTICAL_ARBOL / 2)

                if ultimo_punto_conexion:
                    pygame.draw.line(self.pantalla, COLOR_WIN_PATH, ultimo_punto_conexion, (ultimo_punto_conexion[0], mid_y), 3)
                    if cantidad > 1:
                        pygame.draw.line(self.pantalla, COLOR_LINEA, (primer_hijo_cx, mid_y), (ultimo_hijo_cx, mid_y), 2)

                punto_conexion_para_siguiente = None

                for idx, nodo in enumerate(hermanos):
                    pos_x = start_x + (idx * (ancho_nodo + espacio_h))
                    center_top = (pos_x + ancho_nodo/2, pos_y)
                    
                    if ultimo_punto_conexion:
                        es_el_ganador = (nodo == elegido or nodo["movimiento"] == elegido["movimiento"])
                        color_l = COLOR_WIN_PATH if es_el_ganador else COLOR_LINEA
                        grosor_l = 3 if es_el_ganador else 2
                        
                        pygame.draw.line(self.pantalla, color_l, (center_top[0], mid_y), center_top, grosor_l)
                        
                        if es_el_ganador:
                            pygame.draw.line(self.pantalla, COLOR_WIN_PATH, (ultimo_punto_conexion[0], mid_y), (center_top[0], mid_y), 3)

                    centro_inf = self.dibujar_mini_tablero(pos_x, pos_y, nodo, TAMANO_MINI)

                    if nodo == elegido or nodo["movimiento"] == elegido["movimiento"]:
                        punto_conexion_para_siguiente = centro_inf

                # Actualizamos el eje de la columna vertebral
                if punto_conexion_para_siguiente:
                    ultimo_punto_conexion = punto_conexion_para_siguiente
                    x_columna_vertebral = punto_conexion_para_siguiente[0]
                else:
                    ultimo_punto_conexion = (centro_x, pos_y + ancho_nodo)

            else:
                # LÓGICA DE COLUMNA ÚNICA (Nivel 2+)
                # Dibujamos solo al elegido en el eje x_columna_vertebral
                pos_x = x_columna_vertebral - (ancho_nodo // 2)
                center_top = (x_columna_vertebral, pos_y)
                
                if ultimo_punto_conexion:
                    pygame.draw.line(self.pantalla, COLOR_WIN_PATH, ultimo_punto_conexion, center_top, 3)
                
                centro_inf = self.dibujar_mini_tablero(pos_x, pos_y, elegido, TAMANO_MINI)
                
                ultimo_punto_conexion = centro_inf

    def dibujar_controles_scroll(self):
        color_up = COLOR_BOTON_HOVER if self.rect_up.collidepoint(pygame.mouse.get_pos()) else COLOR_BOTON
        pygame.draw.rect(self.pantalla, color_up, self.rect_up, border_radius=5)
        txt_up = self.fuente_flechas.render("^", True, COLOR_TEXTO)
        self.pantalla.blit(txt_up, txt_up.get_rect(center=self.rect_up.center))

        color_down = COLOR_BOTON_HOVER if self.rect_down.collidepoint(pygame.mouse.get_pos()) else COLOR_BOTON
        pygame.draw.rect(self.pantalla, color_down, self.rect_down, border_radius=5)
        txt_down = self.fuente_flechas.render("v", True, COLOR_TEXTO)
        self.pantalla.blit(txt_down, txt_down.get_rect(center=self.rect_down.center))

    def dibujar_interfaz(self, tablero, mensaje, trayectoria=None, arbol_futuro=None):
        self.pantalla.fill(COLOR_FONDO)
        self.pantalla.blit(self.fuente_titulo.render(mensaje, True, COLOR_TEXTO), (self.inicio_x, 80))
        pygame.draw.rect(self.pantalla, COLOR_TABLERO, (self.inicio_x, self.inicio_y, self.ancho_juego, self.ancho_juego), border_radius=20)
        for i in range(9):
            x, y = self.inicio_x + 10 + (i%3)*(TAMANO_CASILLA+10), self.inicio_y + 10 + (i//3)*(TAMANO_CASILLA+10)
            pygame.draw.rect(self.pantalla, COLOR_CASILLA, (x, y, TAMANO_CASILLA, TAMANO_CASILLA), border_radius=15)
            if tablero[i] != " ":
                c, t = (COLOR_X, "X") if tablero[i]=="X" else (COLOR_O, "O")
                txt = self.fuente_ficha.render(t, True, c)
                self.pantalla.blit(txt, txt.get_rect(center=(x+TAMANO_CASILLA/2, y+TAMANO_CASILLA/2)))

        color_btn = COLOR_BOTON_HOVER if self.rect_boton.collidepoint(pygame.mouse.get_pos()) else COLOR_BOTON
        pygame.draw.rect(self.pantalla, color_btn, self.rect_boton, border_radius=10)
        self.pantalla.blit(self.fuente_ui.render("Nueva Partida", True, COLOR_TEXTO), (self.rect_boton.x+60, self.rect_boton.y+17))

        ancho_zona = ANCHO_VENTANA - LIMITE_IZQUIERDO_ARBOL
        centro_x = LIMITE_IZQUIERDO_ARBOL + (ancho_zona // 2)
        pygame.draw.rect(self.pantalla, COLOR_FONDO, (LIMITE_IZQUIERDO_ARBOL, 0, ancho_zona, 80))
        self.pantalla.blit(self.fuente_titulo.render("Evolución de la Partida", True, COLOR_TEXTO), (centro_x - 140, 30))

        self.dibujar_arbol_unificado(trayectoria, arbol_futuro, centro_x)
        self.dibujar_controles_scroll()
        pygame.display.flip()
        
    def obtener_evento_usuario(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT: return 'SALIR'
            if e.type == pygame.MOUSEWHEEL:
                self.scroll_y -= e.y * 30
                if self.scroll_y < 0: self.scroll_y = 0
            if e.type == pygame.MOUSEBUTTONDOWN:
                if self.rect_boton.collidepoint(e.pos): 
                    self.scroll_y = 0; return 'REINICIAR'
                if self.rect_up.collidepoint(e.pos):
                    self.scroll_y -= 50
                    if self.scroll_y < 0: self.scroll_y = 0
                if self.rect_down.collidepoint(e.pos):
                    self.scroll_y += 50
                if self.inicio_x<e.pos[0]<self.inicio_x+self.ancho_juego and self.inicio_y<e.pos[1]<self.inicio_y+self.ancho_juego:
                    c = (e.pos[0]-self.inicio_x)//(TAMANO_CASILLA+10)
                    f = (e.pos[1]-self.inicio_y)//(TAMANO_CASILLA+10)
                    if 0<=c<3 and 0<=f<3: return f*3+c
        return None
    def cerrar(self): pygame.quit(); sys.exit()