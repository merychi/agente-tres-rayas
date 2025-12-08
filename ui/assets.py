# ui/assets.py
import pygame
import os

def cargar_fondos():
    fondos = {}

    return fondos

def cargar_fuentes():
    """
    Intenta cargar la fuente personalizada, si falla, usa las del sistema.
    Devuelve un diccionario con todas las fuentes listas.
    """
    fuentes = {}
    ruta_fuente = os.path.join(os.path.dirname(__file__), '..', 'assets', 'BubbleboddyNeue-Bold Trial.ttf')
    r_fuente = os.path.join(os.path.dirname(__file__), '..', 'assets', 'BubbleboddyNeue-ExtraBold Trial.ttf')
    rut_fuente = os.path.join(os.path.dirname(__file__), '..', 'assets', 'Boongaloo-Regular.ttf')

    try:
        # Intentar cargar fuente bonita
        fuentes['titulo'] = pygame.font.Font(ruta_fuente, 45) 
        fuentes['subtitulo'] = pygame.font.Font(ruta_fuente, 35) 
        fuentes['ficha'] = pygame.font.Font(ruta_fuente, 65)
        fuentes['boton'] = pygame.font.Font(ruta_fuente, 22)    
        fuentes['boton_menu'] = pygame.font.Font(ruta_fuente, 38)
        fuentes['mini'] = pygame.font.Font(ruta_fuente, 18)
        fuentes['ui'] = pygame.font.Font(ruta_fuente, 16)
        fuentes['numeros'] = pygame.font.SysFont(rut_fuente, 20, bold=True) 
    except FileNotFoundError:
        print("AVISO: Usando fuentes del sistema.")
        # Fallback a fuentes del sistema
        fuentes['titulo'] = pygame.font.SysFont("Arial", 32, bold=True)
        fuentes['subtitulo'] = pygame.font.SysFont("Arial", 32, bold=True)
        fuentes['ficha'] = pygame.font.SysFont("Arial", 60, bold=True)
        fuentes['boton'] = pygame.font.SysFont("Arial", 18, bold=True)
        fuentes['boton_menu'] = pygame.font.SysFont("Arial", 32, bold=True)
        fuentes['mini'] = pygame.font.SysFont("Arial", 16, bold=True)
        fuentes['ui'] = pygame.font.SysFont("Arial", 14)
        fuentes['numeros'] = pygame.font.SysFont("Arial", 20, bold=True) 
    
    return fuentes

def cargar_sonidos():
    """
    Carga los efectos de sonido del juego.
    """
    sonidos = {}
    
    ruta_sfx = os.path.join(os.path.dirname(__file__), '..', 'assets', 'plop.wav')

    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init()
            
        sonidos['colocar'] = pygame.mixer.Sound(ruta_sfx)
        sonidos['colocar'].set_volume(0.3) 

        sonidos['menu_hover'] = pygame.mixer.Sound(ruta_sfx)
        sonidos['menu_hover'].set_volume(0.4) 
        
        sonidos['menu_click'] = pygame.mixer.Sound(ruta_sfx)
        sonidos['menu_click'].set_volume(0.6)
        
    except (FileNotFoundError, pygame.error) as e:
        print(f"AVISO: No se pudo cargar el sonido: {e}")
    
    return sonidos

def iniciar_musica_fondo():
    """
    Carga y reproduce la música de fondo en bucle infinito.
    """
    ruta_musica = os.path.join(os.path.dirname(__file__), '..', 'assets', 'fondo.mp3')

    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init()

        # Cargar la música (Stream)
        pygame.mixer.music.load(ruta_musica)
        
        # Volumen bajo para que no moleste (0.0 a 1.0)
        pygame.mixer.music.set_volume(0.1) 
        
        # Reproducir en bucle infinito (-1 significa loops infinitos)
        pygame.mixer.music.play(-1)
        
        print("Música de fondo iniciada.")
        
    except (FileNotFoundError, pygame.error) as e:
        print(f"AVISO: No se pudo cargar la música: {e}")