import pygame
import os
import sys
from ui.config import *
from ui.assets import *

class MenuPrincipal:
    def __init__(self, pantalla):
        self.pantalla = pantalla
        self.fuentes = cargar_fuentes()
        self.sonidos = cargar_sonidos()

        self.ultimo_boton_hover = None 
        r_fondo = os.path.join(os.path.dirname(__file__), '..', 'assets', 'fondo_menu.png')
        try:
            self.fondo = pygame.image.load(r_fondo)
            self.fondo = pygame.transform.scale(self.fondo, (ANCHO_VENTANA, ALTO_VENTANA))
        except FileNotFoundError:
            print("ERROR: No se encontró fondo_menu.png. Usando color sólido.")
            self.fondo = None

        ruta_fuente = os.path.join(os.path.dirname(__file__), '..', 'assets', 'BubbleboddyNeue-ExtraBold Trial.ttf')
        r_fuente = os.path.join(os.path.dirname(__file__), '..', 'assets', 'BubbleboddyNeue-Bold Trial.ttf')
        try:
            self.f_titulo_menu = pygame.font.Font(ruta_fuente, 95) 
            self.f_sub_menu = pygame.font.Font(r_fuente, 45)
        except FileNotFoundError:
            self.f_titulo_menu = pygame.font.SysFont("Arial", 80, bold=True)
            self.f_sub_menu = pygame.font.SysFont("Arial", 40, bold=True)

        # Definir botones (Rectángulos)
        center_x = ANCHO_VENTANA // 2
        start_y = 320  

        self.btn_jugar = pygame.Rect(0, 0, 390, 100)
        self.btn_jugar.center = (center_x, start_y)

        self.btn_ayuda = pygame.Rect(0, 0, 390, 100)
        self.btn_ayuda.center = (center_x, start_y + 140)
        
        self.btn_salir = pygame.Rect(0, 0, 390, 100)
        self.btn_salir.center = (center_x, start_y + 280)  

    def dibujar_boton(self, rect, texto, color_base, color_hover):
        mouse_pos = pygame.mouse.get_pos()
        es_hover = rect.collidepoint(mouse_pos)
        
        color_actual = color_hover if es_hover else color_base

        elevacion = 6 if es_hover else 0
        
        rect_sombra = rect.copy()
        rect_sombra.y += 12
        pygame.draw.rect(self.pantalla, (79, 87, 175), rect_sombra, border_radius=30)
        
        # Dibujar el botón principal
        rect_visual = rect.copy()
        rect_visual.y -= elevacion  # Restamos Y para que suba
        pygame.draw.rect(self.pantalla, color_actual, rect_visual, border_radius=30)
        
        # Texto del botón
        txt_surf = self.fuentes['boton_menu'].render(texto, True, (255, 255, 255))
        txt_rect = txt_surf.get_rect(center=rect_visual.center) 
        self.pantalla.blit(txt_surf, txt_rect)
        
        return es_hover
    
    def actualizar(self):
        # Fondo
        if self.fondo:
            self.pantalla.blit(self.fondo, (0, 0))
        else:
            self.pantalla.fill((100, 100, 200)) # Color de respaldo

        #Títulos 
        color_titulo = (45, 42, 85) 
        texto_titulo = self.f_titulo_menu.render("TIC TAC TOE", True, color_titulo)
        self.pantalla.blit(texto_titulo, (40, 90))

        # Subtítulo
        color_sub = (235, 186, 239)
        texto_sub = self.f_sub_menu.render("Tres en raya", True, color_sub)
        self.pantalla.blit(texto_sub, (45, 185))
        
        self.dibujar_boton(self.btn_jugar, "Nuevo Juego", (44, 44, 84), (32, 32, 61))
        self.dibujar_boton(self.btn_ayuda, "¿Cómo Jugar?", (44, 44, 84), (32, 32, 61))
        self.dibujar_boton(self.btn_salir, "Salir",       (44, 44, 84), (32, 32, 61))

        boton_actual_hover = None # ¿Sobre qué botón estamos AHORA?

        # Dibujamos y verificamos uno por uno
        if self.dibujar_boton(self.btn_jugar, "Nuevo Juego", (44, 44, 84), (32, 32, 61)):
            boton_actual_hover = "JUGAR"
        
        elif self.dibujar_boton(self.btn_ayuda, "¿Cómo Jugar?", (44, 44, 84), (32, 32, 61)):
            boton_actual_hover = "AYUDA"
            
        elif self.dibujar_boton(self.btn_salir, "Salir", (44, 44, 84), (32, 32, 61)):
            boton_actual_hover = "SALIR"

        # Comparamos con el frame anterior para saber si ACABAMOS de entrar
        if boton_actual_hover != self.ultimo_boton_hover:
            if boton_actual_hover is not None:
                # ¡Es un botón nuevo! Reproducir sonido
                if 'menu_hover' in self.sonidos:
                    self.sonidos['menu_hover'].play()
            
            # Actualizamos la memoria
            self.ultimo_boton_hover = boton_actual_hover

        pygame.display.flip()

    def manejar_eventos(self):
        """Retorna 'JUGAR', 'SALIR' o None"""
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return "SALIR"
            
            if evento.type == pygame.MOUSEBUTTONDOWN:
                if evento.button == 1: 
                    mouse_pos = pygame.mouse.get_pos()
                    
                    accion = None
                    if self.btn_jugar.collidepoint(mouse_pos):
                        accion = "JUGAR"
                    elif self.btn_ayuda.collidepoint(mouse_pos):
                        accion = "AYUDA"
                    elif self.btn_salir.collidepoint(mouse_pos):
                        accion = "SALIR"
                    
                    if accion:
                        if 'menu_click' in self.sonidos:
                            self.sonidos['menu_click'].play()
                        return accion
            
        return None    

