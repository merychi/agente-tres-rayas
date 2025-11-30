# main.py
# Punto de entrada principal para la versión de consola del juego.

from game.logic import LogicaTresRayas
# Importamos la función que conecta con el algoritmo Minimax
from game.ai import ia_decidir_movimiento 

def imprimir_tablero(tablero):
    print("\n")
    print(f"  {tablero[0]} | {tablero[1]} | {tablero[2]} ")
    print(" ---+---+---")
    print(f"  {tablero[3]} | {tablero[4]} | {tablero[5]} ")
    print(" ---+---+---")
    print(f"  {tablero[6]} | {tablero[7]} | {tablero[8]} ")
    print("\n")


def main():
    juego = LogicaTresRayas()
    print("--- Tres en raya (modo consola) ---")
    print("Instrucciones: Escribe el número de la casilla (0-8)")
    
    # Configuración inicial: Asignamos roles fijos para esta prueba.
    turno = "X"  # La IA será 'X' (Maximizado) y el Humano 'O' (Minimizado)

    while not juego.juego_terminado():
        print(f"Turno actual: {turno}")
        imprimir_tablero(juego.tablero)

        # --- BLOQUE DE DECISIÓN DE TURNO ---
        if turno == "X":
            # Turno de la IA (Automático)
            print("La IA está pensando...")
            
            # Llamada al cerebro de la IA (Minimax).
            # La función retorna una tupla: (mejor_movimiento, datos_para_graficar).
            # Usamos la variable '_' para descartar los datos del gráfico, 
            # ya que en la consola solo necesitamos el movimiento.
            movimiento, _ = ia_decidir_movimiento(juego.tablero)
            
            print(f"La IA (X) elige la casilla: {movimiento}")
        else:
            # Turno del Humano (Manual)
            try:
                entrada = input(f"Jugador {turno}, elige casilla (0-8): ")
                movimiento = int(entrada)
            except ValueError:
                print("ERROR: Debes escribir solo un número entero.")
                continue

        # --- EJECUCIÓN DEL MOVIMIENTO ---
        if juego.realizar_movimiento(movimiento, turno):
            # Si el movimiento fue válido, cambiamos de turno
            turno = "O" if turno == "X" else "X"
        else:
            print("Casilla ocupada o número inválido (debe ser 0-8).")

    # --- FIN DEL JUEGO ---
    print("\n--- Juego terminado ---")
    imprimir_tablero(juego.tablero)
    ganador = juego.verificar_ganador()
    
    # Mostramos el resultado final
    print("GANADOR:", ganador if ganador else "Empate")

if __name__ == "__main__":
    main()