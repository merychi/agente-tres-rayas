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
        self.pantalla = pygame.display.set_mode((ANCHO_VENTANA, ALTO_VENTANA))
        pygame.display.set_caption("Tres en Raya - Minimax")
        
        # Fuentes
        self.fuente_titulo = pygame.font.SysFont("Arial", 28, bold=True)
        self.fuente_ficha = pygame.font.SysFont("Arial", 60, bold=True)
        self.fuente_mini = pygame.font.SysFont("Arial", 16, bold=True)
        self.fuente_ui = pygame.font.SysFont("Arial", 14)

        self.ancho_juego = (TAMANO_CASILLA * 3) + (ESPACIO * 4)
        self.inicio_x = 50
        self.inicio_y = 150
        self.rect_boton = pygame.Rect(50, ALTO_VENTANA - 90, 200, 50)

        # --- SCROLL DEL ÁRBOL ---
        self.scroll_arbol = 0
        self.scroll_velocidad = 40
        self.scroll_min = -2500   # límite inferior
        self.scroll_max = 200     # límite superior

    # ------------------------------
    # MINI TABLERO (sin cambios)
    # ------------------------------
    def dibujar_mini_tablero(self, x, y, tablero_data, tamano, puntaje=None):
        padding = 2
        ancho_total = (tamano * 3) + (padding * 4)
        
        # Borde de utilidad por puntaje
        color_borde = COLOR_TABLERO
        if puntaje is not None:
            if puntaje > 0: color_borde = "#33ff33"
            elif puntaje < 0: color_borde = "#ff3333"
            else: color_borde = "#cccccc"

        pygame.draw.rect(self.pantalla, color_borde, (x, y, ancho_total, ancho_total), border_radius=4)
        pygame.draw.rect(self.pantalla, COLOR_TABLERO, (x+2, y+2, ancho_total-4, ancho_total-4), border_radius=4)

        for i in range(9):
            fila = i // 3
            col = i % 3
            px = x + padding + col * (tamano + padding)
            py = y + padding + fila * (tamano + padding)
            
            pygame.draw.rect(self.pantalla, COLOR_CASILLA, (px, py, tamano, tamano), border_radius=2)
            
            if tablero_data[i] != " ":
                color = COLOR_X if tablero_data[i] == "X" else COLOR_O
                txt = self.fuente_mini.render(tablero_data[i], True, color)
                rect = txt.get_rect(center=(px + tamano/2, py + tamano/2))
                self.pantalla.blit(txt, rect)
        
        return (x + ancho_total // 2, y + ancho_total)

    # ------------------------------
    # ÁRBOL RECURSIVO CON SCROLL
    # ------------------------------
    def dibujar_arbol_recursivo(self, nodos, x_min, x_max, y_nivel, padre_pos=None):
        if not nodos: return

        cantidad = len(nodos)
        
        if cantidad == 1 and padre_pos:
            ancho_nodo_px = (TAMANO_MINI * 3) + 8
            pos_x = padre_pos[0] - (ancho_nodo_px / 2)
            espacio_por_nodo = 0
        else:
            ancho_disponible = x_max - x_min
            espacio_por_nodo = ancho_disponible / cantidad
            ancho_nodo_px = (TAMANO_MINI * 3) + 8
        
        for i, nodo in enumerate(nodos):

            # POSICIÓN X
            if not (cantidad == 1 and padre_pos):
                center_x = x_min + (i * espacio_por_nodo) + (espacio_por_nodo / 2)
                pos_x = center_x - (ancho_nodo_px / 2)

            # POSICIÓN Y CON SCROLL
            pos_y = y_nivel + self.scroll_arbol
            punto_conexion_top = (pos_x + ancho_nodo_px / 2, pos_y)

            # LÍNEAS CON SCROLL
            if padre_pos:
                mid_y = pos_y - (ESPACIO_VERTICAL_ARBOL / 2)
                pygame.draw.line(self.pantalla, COLOR_LINEA, (padre_pos[0], padre_pos[1]), (padre_pos[0], mid_y), 2)
                pygame.draw.line(self.pantalla, COLOR_LINEA, (padre_pos[0], mid_y), (punto_conexion_top[0], mid_y), 2)
                pygame.draw.line(self.pantalla, COLOR_LINEA, (punto_conexion_top[0], mid_y), punto_conexion_top, 2)

            # MINI TABLERO
            punto_conexion_bottom = self.dibujar_mini_tablero(
                pos_x, pos_y, nodo["tablero"], TAMANO_MINI, nodo["puntaje"]
            )

            # Puntaje
            p_val = nodo["puntaje"]
            col_p = "#ccffcc" if p_val > 0 else ("#ffcccc" if p_val < 0 else "#ffffff")
            self.pantalla.blit(self.fuente_ui.render(str(p_val), True, col_p), (pos_x + ancho_nodo_px + 3, pos_y + 10))

            # RECURSIVIDAD
            if nodo["sub_ramas"]:
                if cantidad == 1:
                    self.dibujar_arbol_recursivo(nodo["sub_ramas"], x_min, x_max,
                                                 y_nivel + ESPACIO_VERTICAL_ARBOL,
                                                 punto_conexion_bottom)
                else:
                    x_min_hijo = x_min + (i * espacio_por_nodo)
                    x_max_hijo = x_min + ((i + 1) * espacio_por_nodo)
                    self.dibujar_arbol_recursivo(nodo["sub_ramas"], x_min_hijo, x_max_hijo,
                                                 y_nivel + ESPACIO_VERTICAL_ARBOL,
                                                 punto_conexion_bottom)

    # ------------------------------
    # DIBUJAR INTERFAZ COMPLETA
    # ------------------------------
    def dibujar_interfaz(self, tablero, mensaje, tablero_raiz=None, estructura_arbol=None):
        self.pantalla.fill(COLOR_FONDO)
        
        # ------------------ IZQUIERDA ------------------
        self.pantalla.blit(self.fuente_titulo.render(mensaje, True, COLOR_TEXTO), (self.inicio_x, 80))
        pygame.draw.rect(self.pantalla, COLOR_TABLERO,
                         (self.inicio_x, self.inicio_y, self.ancho_juego, self.ancho_juego),
                         border_radius=20)

        for i in range(9):
            fila, col = i // 3, i % 3
            x = self.inicio_x + ESPACIO + col*(TAMANO_CASILLA+ESPACIO)
            y = self.inicio_y + ESPACIO + fila*(TAMANO_CASILLA+ESPACIO)
            pygame.draw.rect(self.pantalla, COLOR_CASILLA, (x, y, TAMANO_CASILLA, TAMANO_CASILLA), border_radius=15)
            if tablero[i] != " ":
                color = COLOR_X if tablero[i] == "X" else COLOR_O
                txt = self.fuente_ficha.render(tablero[i], True, color)
                self.pantalla.blit(txt, txt.get_rect(center=(x + TAMANO_CASILLA/2, y + TAMANO_CASILLA/2)))

        # Botón
        color_btn = COLOR_BOTON_HOVER if self.rect_boton.collidepoint(pygame.mouse.get_pos()) else COLOR_BOTON
        pygame.draw.rect(self.pantalla, color_btn, self.rect_boton, border_radius=10)
        self.pantalla.blit(self.fuente_ui.render("Nueva Partida", True, COLOR_TEXTO),
                           (self.rect_boton.x + 55, self.rect_boton.y + 17))

        # ------------------ DERECHA (ÁRBOL) ------------------
        titulo_arbol = self.fuente_titulo.render("Árbol de Decisiones (scroll ↑ ↓ o rueda)", True, COLOR_TEXTO)
        self.pantalla.blit(titulo_arbol, (ANCHO_VENTANA - ANCHO_SECCION_ARBOL//2 - 150, 40))
        
        inicio_arbol_x = ANCHO_VENTANA - ANCHO_SECCION_ARBOL - 20
        fin_arbol_x = ANCHO_VENTANA - 20
        centro_arbol_x = inicio_arbol_x + (ANCHO_SECCION_ARBOL // 2)

        tablero_a_usar = tablero_raiz if tablero_raiz else tablero
        ancho_nodo = (TAMANO_MINI * 3) + 8

        # Raíz con scroll
        punto_raiz = self.dibujar_mini_tablero(
            centro_arbol_x - ancho_nodo//2,
            100 + self.scroll_arbol,
            tablero_a_usar,
            TAMANO_MINI
        )

        # Árbol completo
        if estructura_arbol:
            self.dibujar_arbol_recursivo(
                estructura_arbol,
                inicio_arbol_x, fin_arbol_x,
                100 + ESPACIO_VERTICAL_ARBOL,
                punto_raiz
            )

        pygame.display.flip()

    # ------------------------------
    # EVENTOS Y SCROLL
    # ------------------------------
    def obtener_evento_usuario(self):
        for evento in pygame.event.get():

            if evento.type == pygame.QUIT:
                return 'SALIR'

            # Scroll con rueda del mouse
            if evento.type == pygame.MOUSEWHEEL:
                self.scroll_arbol += evento.y * self.scroll_velocidad
                self.scroll_arbol = max(self.scroll_min, min(self.scroll_max, self.scroll_arbol))

            # Flechas ↑ ↓
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_UP:
                    self.scroll_arbol += self.scroll_velocidad
                if evento.key == pygame.K_DOWN:
                    self.scroll_arbol -= self.scroll_velocidad
                self.scroll_arbol = max(self.scroll_min, min(self.scroll_max, self.scroll_arbol))

            # Botón nueva partida
            if evento.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                if self.rect_boton.collidepoint(x, y):
                    return 'REINICIAR'

                # Tablero clic
                if (self.inicio_x < x < self.inicio_x + self.ancho_juego and
                    self.inicio_y < y < self.inicio_y + self.ancho_juego):

                    col = (x - self.inicio_x) // (TAMANO_CASILLA + ESPACIO)
                    fila = (y - self.inicio_y) // (TAMANO_CASILLA + ESPACIO)

                    if 0 <= col < 3 and 0 <= fila < 3:
                        return fila * 3 + col

        return None

    def cerrar(self):
        pygame.quit()
        sys.exit()
