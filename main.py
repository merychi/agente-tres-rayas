# main.py
import time
from game.logic import LogicaTresRayas
# Importamos el nuevo generador de árbol
from game.ai import ia_decidir_movimiento, generar_arbol_combinado
from ui.interface import InterfazGrafica

def main():
    juego = LogicaTresRayas()
    ui = InterfazGrafica()
    
    turno = "X"
    mensaje_estado = "Juega la IA (X)"
    juego_corriendo = True
    juego_terminado_flag = False
    
    # Ahora la raíz del grafo será un tablero vacío (siempre 9 hijos)
    tablero_raiz_grafo = [" " for _ in range(9)]
    estructura_arbol = [] 

    # Nota: comenzamos con que la IA juega primero (X) — como en tu diseño original
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
            tablero_raiz_grafo = [" " for _ in range(9)]
            juego_terminado_flag = False
            continue

        if juego_terminado_flag: 
            continue

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
            
            if movimiento is None:
                # No hay movimiento posible
                turno = "O"
                mensaje_estado = "Tu turno"
            else:
                if juego.realizar_movimiento(movimiento, "X"):
                    turno = "O"
                    mensaje_estado = "Tu turno"
                    
                    # --- GENERACIÓN DEL ÁRBOL JERÁRQUICO ---
                    # Generamos la estructura combinada:
                    estructura_arbol = generar_arbol_combinado(juego.tablero)
                    # tablero_raiz_grafo se mantiene como tablero vacío para mostrar siempre 9 hijos

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
