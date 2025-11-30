from game.logic import LogicaTresRayas

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
    turno = "X"  

    while not juego.juego_terminado():
        
        print(f"Turno actual: {turno}")
        imprimir_tablero(juego.tablero)

        try:
            entrada = input(f"Jugador {turno}, elige casilla (0-8): ")
            movimiento = int(entrada)
        except ValueError:
            print("ERROR: Debes escribir solo un número entero.")
            continue 

        if juego.realizar_movimiento(movimiento, turno):
            turno = "O" if turno == "X" else "X"
        else:
            print("Casilla ocupada o número inválido (debe ser 0-8).")

    print("\n--- Juego terminado ---")
    imprimir_tablero(juego.tablero) 
    
    ganador = juego.verificar_ganador()
    print("GANADOR:", ganador if ganador else "Empate")

if __name__ == "__main__":
    main()