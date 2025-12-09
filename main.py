# MENU.PY: Ejecutador del juego"
import time
import sys
import pygame 

from game.logic import LogicaTresRayas
from game.ai import ia_decidir_movimiento, generar_arbol_visual, limpiar_cache 
from ui.interface import *
from ui.menu import MenuPrincipal
from ui.assets import iniciar_musica_fondo 
from ui.help import *

def main():
    pygame.init()
    pygame.mixer.init()
    
    iniciar_musica_fondo()
    
    pantalla_principal = pygame.display.set_mode((ANCHO_VENTANA, ALTO_VENTANA))
    pygame.display.set_caption("Tres en Raya - Minimax")

    # --- BUCLE MAESTRO: Permite que el juego se reinicie desde el menú ---
    while True:
        # ---  MENÚ ---
        menu = MenuPrincipal(pantalla_principal)
        en_menu = True
        clock_menu = pygame.time.Clock()

        proximo_estado = "JUEGO" 

        while en_menu:
            clock_menu.tick(60)
            accion = menu.manejar_eventos()
            menu.actualizar()

            if accion == "SALIR":
                pygame.quit(); sys.exit()
            
            elif accion == "JUGAR":
                proximo_estado = "JUEGO"
                en_menu = False
            
            elif accion == "AYUDA":  
                proximo_estado = "AYUDA"
                en_menu = False 

        # --- PANTALLA DE AYUDA ---
        if proximo_estado == "AYUDA":
            ayuda = PantallaAyuda(pantalla_principal)
            en_ayuda = True
            while en_ayuda:
                clock_menu.tick(60)
                accion = ayuda.manejar_eventos()
                ayuda.actualizar()

                if accion == "SALIR":
                    pygame.quit(); sys.exit()
                elif accion == "MENU":
                    en_ayuda = False 
            
            continue 

        # --- INICIO DEL JUEGO ---
        juego = LogicaTresRayas()
        ui = InterfazGrafica()
        
        turno = "X"
        mensaje_estado = "Juega la IA (X)"
        juego_corriendo = True
        juego_terminado_flag = False
        
        estructura_arbol = [] 
        
        ui.scroll_camino = 0
        ui.fade_cache_camino.clear()
        ui.modal_scroll_y = 0
        ui.modal_scroll_x = 0

        limpiar_cache()

        while juego_corriendo:
            
            # 1. DIBUJAR
            ui.dibujar_interfaz(juego.tablero, mensaje_estado,
                                tablero_raiz=None, 
                                estructura_arbol=estructura_arbol,
                                camino_real=[],
                                combo_ganador=juego.combo_ganador) 

            # 2. EVENTOS
            evento = ui.obtener_evento_usuario()

            if evento == 'SALIR':
                pygame.quit()
                sys.exit()

            if evento == 'MENU':
                juego_corriendo = False 
                break 
            # ------------------------------------------
            
            if evento == 'REINICIAR':
                juego.reiniciar()
                turno = "X"
                mensaje_estado = "Juega la IA (X)"
                
                estructura_arbol = []
                juego_terminado_flag = False
                
                ui.scroll_camino = 0          
                ui.fade_cache_camino.clear()
                ui.scroll_x = 0
                ui.scroll_y = 0
                
                limpiar_cache()
                continue

            if juego_terminado_flag: 
                continue

            if juego.juego_terminado():
                ganador = juego.verificar_ganador()
                mensaje_estado = f"¡Ganó {ganador}!" if ganador else "¡Empate!"

                if ganador: 
                    if 'win' in ui.sonidos:
                        ui.sonidos['win'].play()
                        
                estructura_arbol = generar_arbol_visual(juego.tablero)
                juego_terminado_flag = True
                continue

            # TURNOS
            if turno == "X":
                # --- IA ---
                mensaje_estado = "Pensando..."
                ui.dibujar_interfaz(juego.tablero, mensaje_estado,
                                    estructura_arbol=estructura_arbol,
                                    camino_real=[],
                                    combo_ganador=juego.combo_ganador)
                time.sleep(0.3) 

                movimiento, _ = ia_decidir_movimiento(juego.tablero)
                
                if movimiento is None:
                    turno = "O" 
                else:
                    if juego.realizar_movimiento(movimiento, "X"):
                        turno = "O"
                        mensaje_estado = "Tu turno"
                        estructura_arbol = generar_arbol_visual(juego.tablero)

            else:
                # --- HUMANO ---
                if isinstance(evento, int): 
                    movimiento = evento
                    if juego.es_movimiento_valido(movimiento):
                        juego.realizar_movimiento(movimiento, "O")
                        turno = "X"
                    else:
                        mensaje_estado = "¡Casilla ocupada!"

if __name__ == "__main__":
    main()