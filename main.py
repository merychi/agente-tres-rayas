# main.py
import time
import sys
import pygame 

from game.logic import LogicaTresRayas
# Importamos la nueva función unificada y limpiar_cache
from game.ai import ia_decidir_movimiento, generar_arbol_visual, limpiar_cache 
from ui.interface import *
from ui.menu import MenuPrincipal
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
    
    # --- FASE 2: INICIO DEL JUEGO ---
    juego = LogicaTresRayas()
    ui = InterfazGrafica()
    
    turno = "X"
    mensaje_estado = "Juega la IA (X)"
    juego_corriendo = True
    juego_terminado_flag = False
    
    # Variables de visualización
    # estructura_arbol contendrá TODO (pasado y futuro) gracias al refactor
    estructura_arbol = [] 
    
    # Inicializamos valores de UI
    ui.scroll_camino = 0
    ui.fade_cache_camino.clear()
    ui.modal_scroll_y = 0
    ui.modal_scroll_x = 0

    # Limpiamos memoria de IA al iniciar
    limpiar_cache()

    while juego_corriendo:
        
        # 1. DIBUJAR
        # Pasamos estructura_arbol. 'camino_real' lo dejamos vacío o None
        # porque la nueva función ya incluye el camino dentro del árbol.
        ui.dibujar_interfaz(juego.tablero, mensaje_estado,
                            tablero_raiz=None, # Ya no es necesario con el nuevo método
                            estructura_arbol=estructura_arbol,
                            camino_real=[]) # Pasamos lista vacía para no romper la UI si lo pide

        # 2. EVENTOS
        evento = ui.obtener_evento_usuario()

        if evento == 'SALIR':
            juego_corriendo = False; break
        
        if evento == 'REINICIAR':
            juego.reiniciar()
            turno = "X"
            mensaje_estado = "Juega la IA (X)"
            
            # Resetear visualización
            estructura_arbol = []
            juego_terminado_flag = False
            
            # Resetear UI
            ui.scroll_camino = 0          
            ui.fade_cache_camino.clear()
            ui.scroll_x = 0
            ui.scroll_y = 0
            
            # Limpiar memoria de IA
            limpiar_cache()
            continue

        if juego_terminado_flag: 
            continue

        if juego.juego_terminado():
            ganador = juego.verificar_ganador()
            mensaje_estado = f"¡Ganó {ganador}!" if ganador else "¡Empate!"
            
            # Generar árbol final completo
            estructura_arbol = generar_arbol_visual(juego.tablero)
            
            juego_terminado_flag = True
            continue

        # 3. TURNOS
        if turno == "X":
            # --- IA ---
            mensaje_estado = "Pensando..."
            
            # Dibujar antes de pensar para que se vea el mensaje
            ui.dibujar_interfaz(juego.tablero, mensaje_estado,
                                estructura_arbol=estructura_arbol,
                                camino_real=[])
            time.sleep(0.3) 

            # IA Juega
            movimiento, _ = ia_decidir_movimiento(juego.tablero)
            
            if movimiento is None:
                turno = "O" # Caso borde (empate sin detectar)
            else:
                if juego.realizar_movimiento(movimiento, "X"):
                    turno = "O"
                    mensaje_estado = "Tu turno"
                    
                    # --- ACTUALIZAR EL ÁRBOL ---
                    # Llamamos a la función única refactorizada
                    estructura_arbol = generar_arbol_visual(juego.tablero)

        else:
            # --- HUMANO ---
            if isinstance(evento, int): 
                movimiento = evento
                if juego.es_movimiento_valido(movimiento):
                    juego.realizar_movimiento(movimiento, "O")
                    turno = "X"
                    
                    # Opcional: Actualizar árbol tras jugada humana para ver el cambio inmediato
                    # estructura_arbol = generar_arbol_visual(juego.tablero)
                else:
                    mensaje_estado = "¡Casilla ocupada!"

    ui.cerrar()

if __name__ == "__main__":
    main()