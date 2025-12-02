# main.py
import time
from game.logic import LogicaTresRayas
# Importamos el nuevo generador de árbol
from game.ai import ia_decidir_movimiento, generar_arbol_juego 
from ui.interface import InterfazGrafica

def main():
    juego = LogicaTresRayas()
    ui = InterfazGrafica()
    
    turno = "X"
    mensaje_estado = "Juega la IA (X)"
    juego_corriendo = True
    juego_terminado_flag = False
    
    # Esta variable ahora guardará la estructura jerárquica
    estructura_arbol = [] 
    tablero_raiz_grafo = list(juego.tablero)

    while juego_corriendo:
        
        # 1. DIBUJAR (Pasamos la estructura compleja)
        ui.dibujar_interfaz(juego.tablero, mensaje_estado, 
                            tablero_raiz=tablero_raiz_grafo, 
                            estructura_arbol=estructura_arbol)

        # 2. EVENTOS
        evento = ui.obtener_evento_usuario()

        if evento == 'SALIR':
            juego_corriendo = False; break
        
        if evento == 'REINICIAR':
            juego.reiniciar()
            turno = "X"
            mensaje_estado = "Juega la IA (X)"
            estructura_arbol = []
            tablero_raiz_grafo = list(juego.tablero)
            juego_terminado_flag = False
            continue

        if juego_terminado_flag: continue

        if juego.juego_terminado():
            ganador = juego.verificar_ganador()
            mensaje_estado = f"¡Ganó {ganador}!" if ganador else "¡Empate!"
            estructura_arbol = [] # Limpiamos al final
            juego_terminado_flag = True
            continue

        # 3. TURNOS
        if turno == "X":
            # --- IA ---
            mensaje_estado = "Pensando..."
            ui.dibujar_interfaz(juego.tablero, mensaje_estado, 
                                tablero_raiz=tablero_raiz_grafo,
                                estructura_arbol=estructura_arbol)
            time.sleep(0.3) 

            # IA Juega
            movimiento, _ = ia_decidir_movimiento(juego.tablero)
            
            if juego.realizar_movimiento(movimiento, "X"):
                turno = "O"
                mensaje_estado = "Tu turno"
                
                # --- GENERACIÓN DEL ÁRBOL JERÁRQUICO ---
                # Una vez la IA movió, generamos el árbol:
                # Nivel 1: Tus opciones ('O')
                # Nivel 2: La reacción de la IA ('X')
                tablero_raiz_grafo = list(juego.tablero)
                estructura_arbol = generar_arbol_juego(juego.tablero)

        else:
            # --- HUMANO ---
            if isinstance(evento, int): 
                movimiento = evento
                if juego.es_movimiento_valido(movimiento):
                    juego.realizar_movimiento(movimiento, "O")
                    turno = "X"
                    # No borramos el árbol para que se vea hasta que la IA piense de nuevo
                else:
                    mensaje_estado = "¡Casilla ocupada!"

    ui.cerrar()

if __name__ == "__main__":
    main()