# ASSETS.PY: ARCHIVO CONTIENE FUENTES Y MUSICA DEL JUEGO"

import pygame
import os

def cargar_fondos():
    fondos = {}

    return fondos

# ------------------------------
# Carga y establece el icono de la ventana del juego.
# ------------------------------
def establecer_icono_ventana():

    ruta_icono = os.path.join(os.path.dirname(__file__), '..', 'assets', 'icono.png')
    
    try:
        icono = pygame.image.load(ruta_icono)
        pygame.display.set_icon(icono)
    except FileNotFoundError:
        print("AVISO: No se encontró 'assets/icono.png'. Se usará el icono predeterminado.")
    except pygame.error:
        print("AVISO: Error al leer el formato de la imagen del icono.")

# ------------------------------
# Intenta cargar la fuente personalizada, si falla, usa las del sistema.
# Devuelve un diccionario con todas las fuentes listas.
# ------------------------------
def cargar_fuentes():

    fuentes = {}
    ruta_fuente = os.path.join(os.path.dirname(__file__), '..', 'assets', 'BubbleboddyNeue-Bold Trial.ttf')
    r_fuente = os.path.join(os.path.dirname(__file__), '..', 'assets', 'BubbleboddyNeue-ExtraBold Trial.ttf')
    rut_fuente = os.path.join(os.path.dirname(__file__), '..', 'assets', 'Boongaloo-Regular.ttf')

    try:
        # Intentar cargar fuente bonita
        fuentes['titulo'] = pygame.font.Font(ruta_fuente, 45) 
        fuentes['subtitulo'] = pygame.font.Font(ruta_fuente, 35) 
        fuentes['titulo_menu'] = pygame.font.Font(r_fuente, 95) 
        fuentes['subtitulo_menu'] = pygame.font.Font(ruta_fuente, 45) 
        fuentes['ficha'] = pygame.font.Font(ruta_fuente, 65)
        fuentes['boton'] = pygame.font.Font(ruta_fuente, 22)    
        fuentes['boton_menu'] = pygame.font.Font(ruta_fuente, 38)
        fuentes['ayuda'] = pygame.font.Font(ruta_fuente, 20)
        fuentes['mini'] = pygame.font.Font(ruta_fuente, 18)
        fuentes['ayuda_sub'] = pygame.font.Font(ruta_fuente, 19)
        fuentes['ui'] = pygame.font.Font(ruta_fuente, 16)
        fuentes['numeros'] = pygame.font.SysFont(rut_fuente, 20, bold=True) 
        fuentes['creditos'] = pygame.font.Font(ruta_fuente, 20)
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

# ------------------------------
# Carga los efectos de sonido del juego.
# ------------------------------
def cargar_sonidos():

    sonidos = {}
    
    ruta_sfx = os.path.join(os.path.dirname(__file__), '..', 'assets', 'plop.wav')
    ruta_win = os.path.join(os.path.dirname(__file__), '..', 'assets', 'ganar.mp3') 

    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init()
            
        sonidos['colocar'] = pygame.mixer.Sound(ruta_sfx)
        sonidos['colocar'].set_volume(0.3) 

        sonidos['menu_hover'] = pygame.mixer.Sound(ruta_sfx)
        sonidos['menu_hover'].set_volume(0.4) 
        
        sonidos['menu_click'] = pygame.mixer.Sound(ruta_sfx)
        sonidos['menu_click'].set_volume(0.6)

        sonidos['win'] = pygame.mixer.Sound(ruta_win)
        sonidos['win'].set_volume(0.6)
        
    except (FileNotFoundError, pygame.error) as e:
        print(f"AVISO: No se pudo cargar el sonido: {e}")
    
    return sonidos
# ------------------------------
# Carga y reproduce la música de fondo en bucle infinito.
# ------------------------------
def iniciar_musica_fondo():

    ruta_musica = os.path.join(os.path.dirname(__file__), '..', 'assets', 'fondo.mp3')

    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init()

        # Cargar la música (Stream)
        pygame.mixer.music.load(ruta_musica)
        
        pygame.mixer.music.set_volume(0.1) 
        
        pygame.mixer.music.play(-1)
        
        print("Música de fondo iniciada.")
        
    except (FileNotFoundError, pygame.error) as e:
        print(f"AVISO: No se pudo cargar la música: {e}")