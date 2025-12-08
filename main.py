# main.py
import time
import sys
import pygame 

from game.logic import LogicaTresRayas
from game.ai import ia_decidir_movimiento, reconstruir_camino_real, generar_arbol_rama, generar_arbol_con_camino_resaltado, limpiar_cache 
from ui.interface import *
from ui.menu import MenuPrincipal
from ui.config import * 
from ui.assets import iniciar_musica_fondo 

def main():
    pygame.init()
    pygame.mixer.init()
    
    iniciar_musica_fondo()
    
    # Creamos la ventana para el menú
    pantalla_principal = pygame.display.set_mode((ANCHO_VENTANA, ALTO_VENTANA))
    pygame.display.set_caption("Tres en Raya - Minimax")

    # --- FASE 1: BUCLE DEL MENÚ ---
    menu = MenuPrincipal(pantalla_principal)
    en_menu = True
    clock_menu = pygame.time.Clock()

    while en_menu:
        clock_menu.tick(60)
        
        # Dibujar y lógica del menú
        accion = menu.manejar_eventos()
        menu.actualizar()

        if accion == "SALIR":
            pygame.quit()
            sys.exit()
        elif accion == "JUGAR":
            en_menu = False # Rompemos el bucle y pasamos al juego
        elif accion == "AYUDA":
            print("Aquí iría la pantalla de tutorial")     
    
    juego = LogicaTresRayas()
    
    ui = InterfazGrafica()
    
    turno = "X"
    mensaje_estado = "Juega la IA (X)"
    juego_corriendo = True
    juego_terminado_flag = False
    
    # Ahora la raíz del grafo será un tablero vacío (siempre 9 hijos)
    tablero_raiz_grafo = [" " for _ in range(9)]
    estructura_arbol = [] 
    camino_real      = []

    ui.scroll_camino = 0
    ui.fade_cache_camino.clear()

    ui.modal_scroll_y = 0
    ui.modal_scroll_x = 0

    # Nota: comenzamos con que la IA juega primero (X) — como en tu diseño original
    while juego_corriendo:
        
        # 1. DIBUJAR (Pasamos la estructura compleja)
        ui.dibujar_interfaz(juego.tablero, mensaje_estado,
                            tablero_raiz=tablero_raiz_grafo,
                            estructura_arbol=estructura_arbol,
                            camino_real=camino_real)

        # 2. EVENTOS
        evento = ui.obtener_evento_usuario()

        if evento == 'SALIR':
            juego_corriendo = False; break
        
        if evento == 'REINICIAR':
            juego.reiniciar()
            turno = "X"
            mensaje_estado = "Juega la IA (X)"
            estructura_arbol = []
            tablero_raiz_grafo = [" " for _ in range(9)]
            juego_terminado_flag = False
            camino_real      = []
            ui.scroll_camino = 0          
            ui.fade_cache_camino.clear()
            ui.scroll_x = 0
            ui.scroll_y = 0
            juego_terminado_flag = False
            limpiar_cache()
            continue

        if juego_terminado_flag: 
            continue

        if juego.juego_terminado():
            ganador = juego.verificar_ganador()
            mensaje_estado = f"¡Ganó {ganador}!" if ganador else "¡Empate!"
            estructura_arbol = generar_arbol_con_camino_resaltado(juego.tablero)
            camino_real = reconstruir_camino_real(juego.tablero)
            juego_terminado_flag = True
            continue

        # 3. TURNOS
        if turno == "X":
            # --- IA ---
            mensaje_estado = "Pensando..."
            ui.dibujar_interfaz(juego.tablero, mensaje_estado,
                            tablero_raiz=tablero_raiz_grafo,
                            estructura_arbol=estructura_arbol,
                            camino_real=camino_real)
            time.sleep(0.3) 

            # IA Juega
            movimiento, _ = ia_decidir_movimiento(juego.tablero)
            
            if movimiento is None:
                # No hay movimiento posible
                turno = "O"
                mensaje_estado = "Tu turno"
            else:
                if juego.realizar_movimiento(movimiento, "X"):
                    turno = "O"
                    mensaje_estado = "Tu turno"
                    
                    # --- GENERACIÓN DEL ÁRBOL JERÁRQUICO ---
                    estructura_arbol = generar_arbol_con_camino_resaltado(juego.tablero)   # solo la rama jugada
                    camino_real = reconstruir_camino_real(juego.tablero)

        else:
            # --- HUMANO ---
            if isinstance(evento, int): 
                movimiento = evento
                if juego.es_movimiento_valido(movimiento):
                    juego.realizar_movimiento(movimiento, "O")
                    turno = "X"
                else:
                    mensaje_estado = "¡Casilla ocupada!"

    ui.cerrar()

if __name__ == "__main__":
    main()