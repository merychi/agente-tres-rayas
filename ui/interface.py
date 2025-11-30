# interface.py
import pygame
import sys
import os

# Ajuste de rutas
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# --- CONFIGURACIÓN DE COLORES ---
COLOR_FONDO = "#929df6"
COLOR_TABLERO = "#373a7f"
COLOR_CASILLA = "#4f57af"
COLOR_X = "#ebbaef"
COLOR_O = "#e0e9e0"
COLOR_TEXTO = "#FFFFFF"
COLOR_BOTON = "#2c2f66"         # Color del botón
COLOR_BOTON_HOVER = "#3e4291"   # Color al pasar el mouse

# --- DIMENSIONES ---
ANCHO_VENTANA = 600  # Volvemos a un tamaño más compacto
ALTO_VENTANA = 750   # Un poco más alto para el botón
TAMANO_CASILLA = 100
ESPACIO = 15

class InterfazGrafica:
    def __init__(self):
        pygame.init()
        self.pantalla = pygame.display.set_mode((ANCHO_VENTANA, ALTO_VENTANA))
        pygame.display.set_caption("Tres en Raya - Minimax")
        
        # Fuentes
        self.fuente_titulo = pygame.font.SysFont("Arial", 40, bold=True)
        self.fuente_ficha = pygame.font.SysFont("Arial", 80, bold=True)
        self.fuente_btn = pygame.font.SysFont("Arial", 25, bold=True)

        # Geometría del Tablero
        self.ancho_tablero = (TAMANO_CASILLA * 3) + (ESPACIO * 4)
        self.inicio_x = (ANCHO_VENTANA - self.ancho_tablero) // 2
        self.inicio_y = (ALTO_VENTANA - self.ancho_tablero) // 2 

        # Geometría del Botón "Nueva Partida"
        self.rect_boton = pygame.Rect(0, 0, 200, 60)
        self.rect_boton.center = (ANCHO_VENTANA // 2, ALTO_VENTANA - 80)

    def dibujar_interfaz(self, tablero, mensaje):
        self.pantalla.fill(COLOR_FONDO)

        # 1. Título y Estado
        texto_msg = self.fuente_titulo.render(mensaje, True, COLOR_TEXTO)
        rect_msg = texto_msg.get_rect(center=(ANCHO_VENTANA // 2, 60))
        self.pantalla.blit(texto_msg, rect_msg)

        # 2. Tablero
        rect_fondo = pygame.Rect(self.inicio_x, self.inicio_y, self.ancho_tablero, self.ancho_tablero)
        pygame.draw.rect(self.pantalla, COLOR_TABLERO, rect_fondo, border_radius=20)

        for i in range(9):
            fila = i // 3
            col = i % 3
            x = self.inicio_x + ESPACIO + col * (TAMANO_CASILLA + ESPACIO)
            y = self.inicio_y + ESPACIO + fila * (TAMANO_CASILLA + ESPACIO)
            
            rect_casilla = pygame.Rect(x, y, TAMANO_CASILLA, TAMANO_CASILLA)
            pygame.draw.rect(self.pantalla, COLOR_CASILLA, rect_casilla, border_radius=15)

            contenido = tablero[i]
            if contenido != " ":
                color = COLOR_X if contenido == "X" else COLOR_O
                texto = self.fuente_ficha.render(contenido, True, color)
                rect_texto = texto.get_rect(center=rect_casilla.center)
                self.pantalla.blit(texto, rect_texto)

        # 3. Botón Nueva Partida
        pos_mouse = pygame.mouse.get_pos()
        color_btn = COLOR_BOTON_HOVER if self.rect_boton.collidepoint(pos_mouse) else COLOR_BOTON
        
        pygame.draw.rect(self.pantalla, color_btn, self.rect_boton, border_radius=15)
        texto_btn = self.fuente_btn.render("Nueva Partida", True, COLOR_TEXTO)
        rect_txt_btn = texto_btn.get_rect(center=self.rect_boton.center)
        self.pantalla.blit(texto_btn, rect_txt_btn)

        pygame.display.flip()

    def obtener_evento_usuario(self):
        """
        Retorna:
         - 'SALIR'
         - 'REINICIAR' (si clic en botón)
         - int (0-8) (si clic en casilla)
         - None
        """
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return 'SALIR'
            
            if evento.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()

                # A. Clic en Botón Reiniciar
                if self.rect_boton.collidepoint(x, y):
                    return 'REINICIAR'
                
                # B. Clic en Tablero
                if (self.inicio_x < x < self.inicio_x + self.ancho_tablero and
                    self.inicio_y < y < self.inicio_y + self.ancho_tablero):
                    
                    col = (x - self.inicio_x) // (TAMANO_CASILLA + ESPACIO)
                    fila = (y - self.inicio_y) // (TAMANO_CASILLA + ESPACIO)
                    
                    if 0 <= col < 3 and 0 <= fila < 3:
                        return fila * 3 + col
        return None

    def cerrar(self):
        pygame.quit()
        sys.exit()