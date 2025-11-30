import time
from game.logic import LogicaTresRayas
from game.ai import ia_decidir_movimiento
from ui.interface import InterfazGrafica

def main():
    juego = LogicaTresRayas()
    ui = InterfazGrafica()
    
    # Variables de estado
    turno = "X"
    mensaje_estado = "Juega la IA (X)"
    juego_corriendo = True
    juego_terminado_flag = False # Bandera para detener jugadas pero permitir reinicio

    while juego_corriendo:
        
        # 1. Dibujar
        ui.dibujar_interfaz(juego.tablero, mensaje_estado)

        # 2. Escuchar eventos
        evento = ui.obtener_evento_usuario()

        if evento == 'SALIR':
            juego_corriendo = False
            break
        
        # --- LÓGICA DE REINICIO ---
        if evento == 'REINICIAR':
            juego.reiniciar()
            turno = "X"
            mensaje_estado = "Juega la IA (X)"
            juego_terminado_flag = False
            continue

        # Si el juego terminó, no procesamos más turnos (solo esperamos reinicio o salir)
        if juego_terminado_flag:
            continue

        # Verificar fin de juego
        if juego.juego_terminado():
            ganador = juego.verificar_ganador()
            if ganador:
                mensaje_estado = f"¡Ganó {ganador}!"
            else:
                mensaje_estado = "¡Empate!"
            juego_terminado_flag = True
            continue

        # 3. Lógica de Turnos
        if turno == "X":
            # --- TURNO IA ---
            mensaje_estado = "Pensando..."
            ui.dibujar_interfaz(juego.tablero, mensaje_estado)
            time.sleep(0.3) 

            # Ignoramos el grafo (_) por ahora como pediste
            movimiento, _ = ia_decidir_movimiento(juego.tablero)
            
            if juego.realizar_movimiento(movimiento, "X"):
                turno = "O"
                mensaje_estado = "Tu turno"
            
        else:
            # --- TURNO HUMANO ---
            if isinstance(evento, int): # Si recibimos un número de casilla
                movimiento = evento
                if juego.es_movimiento_valido(movimiento):
                    juego.realizar_movimiento(movimiento, "O")
                    turno = "X"
                else:
                    mensaje_estado = "¡Casilla ocupada!"

    ui.cerrar()

if __name__ == "__main__":
    main()