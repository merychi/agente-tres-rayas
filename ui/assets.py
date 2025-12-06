# ui/assets.py
import pygame
import os

def cargar_fuentes():
    """
    Intenta cargar la fuente personalizada, si falla, usa las del sistema.
    Devuelve un diccionario con todas las fuentes listas.
    """
    fuentes = {}
    ruta_fuente = os.path.join(os.path.dirname(__file__), '..', 'assets', 'Boogaloo-Regular.ttf')

    try:
        # Intentar cargar fuente bonita
        fuentes['titulo'] = pygame.font.Font(ruta_fuente, 45) 
        fuentes['subtitulo'] = pygame.font.Font(ruta_fuente, 35) 
        fuentes['ficha'] = pygame.font.Font(ruta_fuente, 65)
        fuentes['boton'] = pygame.font.Font(ruta_fuente, 22)
        fuentes['mini'] = pygame.font.Font(ruta_fuente, 18)
        fuentes['ui'] = pygame.font.Font(ruta_fuente, 16)
    except FileNotFoundError:
        print("AVISO: Usando fuentes del sistema.")
        # Fallback a fuentes del sistema
        fuentes['titulo'] = pygame.font.SysFont("Arial", 32, bold=True)
        fuentes['subtitulo'] = pygame.font.SysFont("Arial", 32, bold=True)
        fuentes['ficha'] = pygame.font.SysFont("Arial", 60, bold=True)
        fuentes['boton'] = pygame.font.SysFont("Arial", 18, bold=True)
        fuentes['mini'] = pygame.font.SysFont("Arial", 16, bold=True)
        fuentes['ui'] = pygame.font.SysFont("Arial", 14)
    
    return fuentes