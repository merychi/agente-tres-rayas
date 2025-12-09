# HELP.PY: ARCHIVO QUE DIBUJA LA INTERFAZ DE "AYUDA / CÓMO JUGAR"

import pygame
import os
from ui.config import *
from ui.assets import cargar_fuentes, cargar_sonidos
from ui.components import dibujar_mini_tablero 

class PantallaAyuda:
    def __init__(self, pantalla):
        self.pantalla = pantalla
        self.fuentes = cargar_fuentes()
        self.sonidos = cargar_sonidos()
        
        self.fade_cache = {}
        self.ultimo_boton_hover = None 

        ruta_fondo = os.path.join(os.path.dirname(__file__), '..', 'assets', 'fondo_ayuda.png')
        try:
            self.fondo = pygame.image.load(ruta_fondo)
            self.fondo = pygame.transform.scale(self.fondo, (ANCHO_VENTANA, ALTO_VENTANA))
        except:
            self.fondo = None

        self.rect_volver = pygame.Rect(30, 30, 50, 50)

    # ---------------------------------------------------------
    #  BOTÓN VOLVER (Casita)
    #  Dibuja un botón casita con sombra y efecto hover; devuelve True si el ratón está encima
    # ---------------------------------------------------------
    def dibujar_boton_volver(self, rect):
        mouse_pos = pygame.mouse.get_pos()
        es_hover = rect.collidepoint(mouse_pos)
        
        color_base = (44, 44, 84)
        color_hover = (70, 70, 130)
        color_sombra = (40, 40, 70) 
        color_icono = (255, 255, 255)
        
        color_actual = color_hover if es_hover else color_base
        elevacion = 3 if es_hover else 0
        
        rect_sombra = rect.copy()
        rect_sombra.y += 5 
        pygame.draw.rect(self.pantalla, color_sombra, rect_sombra, border_radius=15)
        
        rect_visual = rect.copy()
        rect_visual.y -= elevacion
        pygame.draw.rect(self.pantalla, color_actual, rect_visual, border_radius=15)
        
        cx, cy = rect_visual.centerx, rect_visual.centery
        techo = [(cx, cy - 8), (cx - 12, cy + 2), (cx + 12, cy + 2)]
        pygame.draw.polygon(self.pantalla, color_icono, techo)
        pygame.draw.rect(self.pantalla, color_icono, (cx - 8, cy + 2, 16, 14))
        pygame.draw.rect(self.pantalla, color_actual, (cx - 3, cy + 8, 6, 8), border_top_left_radius=2, border_top_right_radius=2)

        return es_hover

    # ---------------------------------------------------------
    #  MINI-ÁRBOL GRÁFICO 
    # Pinta una línea vertical y dos mini-tableros con etiquetas "IA"/"Humano" para mostrar cómo se ramifica el árbol.
    # ---------------------------------------------------------
    def dibujar_mini_arbol_grafico(self, center_x, start_y):
        nodos = [
            {"tablero": ["X", " ", " ", " ", " ", " ", " ", " ", " "], "quien": "IA"},
            {"tablero": ["X", " ", " ", " ", "O", " ", " ", " ", " "], "quien": "Humano"}
        ]

        ancho = (TAMANO_MINI * 3) + 8
        espacio_y = 90

        alto_total = (len(nodos) - 1) * espacio_y
        pygame.draw.line(self.pantalla, (180, 200, 255), (center_x, start_y + 25), (center_x, start_y + 25 + alto_total), 3)

        pos_y = start_y
        
        start_board_x = center_x - (ancho // 2)

        for i, nodo in enumerate(nodos):
            fake_id = f"minihelp_{i}"

            dibujar_mini_tablero(
                self.pantalla,
                self.fuentes['mini'],
                start_board_x,  
                pos_y,
                nodo["tablero"],
                TAMANO_MINI,
                self.fade_cache,
                15,
                None,
                fake_id
            )

            label = self.fuentes['ui'].render(nodo["quien"], True, (255, 255, 255))
            r_label = label.get_rect(midright=(start_board_x - 15, pos_y + 25))
            self.pantalla.blit(label, r_label)

            pos_y += espacio_y

    # ---------------------------------------------------------
    #  BOTÓN DE EJEMPLO
    # Dibuja un botón grande con texto, sombra y elevación al pasar el ratón; devuelve True si está en hover.
    # ---------------------------------------------------------
    def dibujar_boton_ejemplo(self, center_x, center_y, texto):
        rect = pygame.Rect(0, 0, 240, 65)
        rect.center = (center_x, center_y)

        mouse_pos = pygame.mouse.get_pos()
        es_hover = rect.collidepoint(mouse_pos)
        
        color_base = (44, 44, 84)
        color_hover = (70, 70, 130)
        color_actual = color_hover if es_hover else color_base

        elevacion = 6 if es_hover else 0
        
        rect_sombra = rect.copy()
        rect_sombra.y += 12
        pygame.draw.rect(self.pantalla, (79, 87, 175), rect_sombra, border_radius=30)
        
        rect_visual = rect.copy()
        rect_visual.y -= elevacion
        pygame.draw.rect(self.pantalla, color_actual, rect_visual, border_radius=30)
        
        fuente_btn = self.fuentes['boton'] 
        txt_surf = fuente_btn.render(texto, True, (255, 255, 255))
        
        txt_surf = fuente_btn.render(texto, True, (255, 255, 255))
        txt_rect = txt_surf.get_rect(center=rect_visual.center) 
        self.pantalla.blit(txt_surf, txt_rect)
        
        return es_hover

    # ---------------------------------------------------------
    #  WRAP TEXT
    # Parte un texto en lista de líneas que no superen el ancho dado, cortando por palabras.
    # ---------------------------------------------------------
    def wrap_text(self, text, font, max_width):
        words = text.split(' ')
        lines = []
        current = []
        for w in words:
            current.append(w)
            width, _ = font.size(' '.join(current))
            if width > max_width:
                current.pop()
                lines.append(' '.join(current))
                current = [w]
        lines.append(' '.join(current))
        return lines

    # ---------------------------------------------------------
    #  ACTUALIZAR
    # Pinta fondo, título, texto introductorio y dos columnas con 
    # subtítulos, explicaciones, mini-tablero y botones; reproduce sonido hover.
    # ---------------------------------------------------------
    def actualizar(self):
        if self.fondo:
            self.pantalla.blit(self.fondo, (0, 0))
        else:
            self.pantalla.fill((30, 30, 60))

        panel_x = 90
        panel_y = 90
        panel_w = ANCHO_VENTANA - 180
        
        y = panel_y + 35

        # TÍTULO
        center_screen_x = ANCHO_VENTANA // 2
        titulo = self.fuentes['titulo'].render("Mecánicas del Juego", True, (255, 180, 220))
        r = titulo.get_rect(center=(center_screen_x, y))
        self.pantalla.blit(titulo, r)
        y += 60

        # INTRODUCCIÓN
        intro = (
            "Enfréntate a una Inteligencia Artificial diseñada mediante el algoritmo Minimax. "
            "El objetivo es alinear tres fichas antes que el agente. Ten en cuenta que el sistema "
            "juega de forma óptima: buscará ganar o forzar un empate."
        )
        lines = self.wrap_text(intro, self.fuentes['ayuda'], panel_w - 140)
        for line in lines:
            t = self.fuentes['ayuda'].render(line, True, (220, 220, 220))
            r = t.get_rect(center=(center_screen_x, y))
            self.pantalla.blit(t, r)
            y += 26

        y += 40 

        # COLUMNAS
        col_gap = 100
        col_width = (panel_w - col_gap) // 2
        
        col1_center_x = panel_x + col_width // 2
        col2_center_x = ANCHO_VENTANA - panel_x - col_width // 2

        start_cols_y = y

        # === COLUMNA IZQUIERDA ===
        y_c1 = start_cols_y
        
        sub1_lines = self.wrap_text("Decisiones del Agente", self.fuentes['subtitulo'], int(col_width * 0.8))
        for line in sub1_lines:
            txt = self.fuentes['subtitulo'].render(line, True, (150, 200, 255))
            r = txt.get_rect(center=(col1_center_x, y_c1))
            self.pantalla.blit(txt, r)
            y_c1 += 35
        
        y_c1 += 10
        txt1 = "A la derecha del tablero encontrarás el panel el árbol de estados que el agente evalúa. Puedes observar las ramas de decisión"
        lineas1 = self.wrap_text(txt1, self.fuentes['mini'], int(col_width * 0.9))
        for ln in lineas1:
            t = self.fuentes['mini'].render(ln, True, (220, 220, 220))
            r = t.get_rect(center=(col1_center_x, y_c1))
            self.pantalla.blit(t, r)
            y_c1 += 22
            
        # Mini Árbol
        self.dibujar_mini_arbol_grafico(col1_center_x + 30, y_c1 + 20)

        # === COLUMNA DERECHA ===
        y_c2 = start_cols_y
        
        # === COLUMNA DERECHA ===
        y_c2 = start_cols_y

        # Subtítulo
        sub2_lines = self.wrap_text("Lógica del Agente", self.fuentes['subtitulo'], int(col_width * 0.8))
        for line in sub2_lines:
            txt = self.fuentes['subtitulo'].render(line, True, (150, 200, 255))
            r = txt.get_rect(center=(col2_center_x, y_c2))
            self.pantalla.blit(txt, r)
            y_c2 += 35

        y_c2 += 12

        # Texto explicativo
        txt2 = "Utiliza el botón 'Ver árbol completo' para abrir una vista modal detallada. Podrás navegar por todos los nodos generados y entender la lógica matemática detrás de cada jugada"
        lineas2 = self.wrap_text(txt2, self.fuentes['mini'], int(col_width * 0.9))
        for ln in lineas2:
            t = self.fuentes['mini'].render(ln, True, (220, 220, 220))
            r = t.get_rect(center=(col2_center_x, y_c2))
            self.pantalla.blit(t, r)
            y_c2 += 22

        # Botón Ejemplo
        hover_actual = None
        y_boton = y_c2 + 60
        if self.dibujar_boton_ejemplo(col2_center_x, y_boton + 30, "Ver árbol Completo"):
            hover_actual = "EJEMPLO"

        # Botón Volver
        if self.dibujar_boton_volver(self.rect_volver):
            hover_actual = "VOLVER"

        # Sonido Hover
        if hover_actual != self.ultimo_boton_hover:
            if hover_actual is not None:
                if 'menu_hover' in self.sonidos:
                    self.sonidos['menu_hover'].play()
            self.ultimo_boton_hover = hover_actual

        pygame.display.flip()

    # ---------------------------------------------------------
    # MANEJAR EVENTOS
    # Detecta salir o clic en el botón casita y devuelve "SALIR"/"MENU"; también reproduce sonido de clic.
    # ---------------------------------------------------------
    def manejar_eventos(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return "SALIR"

            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                # Clic en volver
                if self.rect_volver.collidepoint(pygame.mouse.get_pos()):
                    if 'menu_click' in self.sonidos:
                        self.sonidos['menu_click'].play()
                    return "MENU"
        return None