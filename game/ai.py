# game/ai.py
from game.logic import LogicaTresRayas
from copy import deepcopy 

def minimax(tablero, profundidad, es_turno_max):
    """
    Función recursiva que simula todos los posibles juegos futuros.
    """
    juego = LogicaTresRayas()
    juego.tablero = tablero 
    ganador = juego.verificar_ganador()

    if ganador == "X":
        return 10 - profundidad 
    elif ganador == "O":
        return profundidad - 10 
    elif not juego.existe_espacio_libre():
        return 0 

    if es_turno_max:
        mejor_puntaje = -float('inf')
        for movimiento in juego.obtener_movimientos_posibles():
            juego.tablero[movimiento] = "X" 
            puntaje = minimax(juego.tablero, profundidad + 1, False)
            juego.tablero[movimiento] = " "
            mejor_puntaje = max(mejor_puntaje, puntaje)
        return mejor_puntaje
    else:
        mejor_puntaje = float('inf')
        for movimiento in juego.obtener_movimientos_posibles():
            juego.tablero[movimiento] = "O"
            puntaje = minimax(juego.tablero, profundidad + 1, True)
            juego.tablero[movimiento] = " "
            mejor_puntaje = min(mejor_puntaje, puntaje)
        return mejor_puntaje

def ia_decidir_movimiento(tablero):
    datos_grafico = [] 
    mejor_puntaje = -float('inf')
    mejor_movimiento = None

    for movimiento in range(9):
        if tablero[movimiento] == " ":
            tablero_copia = deepcopy(tablero)
            tablero_copia[movimiento] = "X" 
            puntaje = minimax(tablero_copia, 0, False)
            datos_grafico.append((movimiento, puntaje, tablero_copia))
            if puntaje > mejor_puntaje:
                mejor_puntaje = puntaje
                mejor_movimiento = movimiento
    return mejor_movimiento, datos_grafico

def generar_arbol_juego(tablero, profundidad_max=2):
    """
    Genera el árbol.
    CORRECCIÓN: Filtra las respuestas de la IA para mostrar solo la mejor jugada (Ruta Óptima).
    """
    def construir_nodo(tablero_actual, profundidad, es_turno_ia):
        juego = LogicaTresRayas()
        juego.tablero = tablero_actual
        if profundidad == 0 or juego.juego_terminado():
            return []

        hijos = []
        movimientos = juego.obtener_movimientos_posibles()
        
        for mov in movimientos:
            tablero_futuro = deepcopy(tablero_actual)
            ficha = "X" if es_turno_ia else "O"
            tablero_futuro[mov] = ficha
            
            puntaje = minimax(tablero_futuro, 0, not es_turno_ia)
            
            nodo = {
                "movimiento": mov,
                "tablero": tablero_futuro,
                "puntaje": puntaje,
                "es_turno_ia": es_turno_ia,
                "sub_ramas": [] 
            }
            
            if profundidad > 1:
                # Generamos las respuestas del siguiente nivel
                respuestas = construir_nodo(tablero_futuro, profundidad - 1, not es_turno_ia)
                
                if respuestas:
                    # --- AQUÍ ESTABA EL ERROR VISUAL ---
                    # Si el turno actual NO es de la IA (es Humano), significa que las 'respuestas'
                    # son jugadas de la IA. Queremos ver solo la MEJOR respuesta de la IA.
                    if not es_turno_ia: 
                        mejor_respuesta = max(respuestas, key=lambda x: x["puntaje"])
                        nodo["sub_ramas"] = [mejor_respuesta]
                    else:
                        # Si las respuestas fueran del humano, las mostramos todas (opcional)
                        nodo["sub_ramas"] = respuestas

            hijos.append(nodo)
        return hijos

    return construir_nodo(tablero, profundidad_max, False)