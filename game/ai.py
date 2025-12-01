# game/ai.py
from game.logic import LogicaTresRayas
from copy import deepcopy 

# --- (MANTENER minimax y ia_decidir_movimiento IGUALES) ---
def minimax(tablero, profundidad, es_turno_max):
    juego = LogicaTresRayas()
    juego.tablero = tablero 
    ganador = juego.verificar_ganador()

    if ganador == "X": return 10 - profundidad 
    elif ganador == "O": return profundidad - 10 
    elif not juego.existe_espacio_libre(): return 0 

    if es_turno_max:
        mejor = -float('inf')
        for mov in juego.obtener_movimientos_posibles():
            juego.tablero[mov] = "X" 
            puntaje = minimax(juego.tablero, profundidad + 1, False)
            juego.tablero[mov] = " "
            mejor = max(mejor, puntaje)
        return mejor
    else:
        mejor = float('inf')
        for mov in juego.obtener_movimientos_posibles():
            juego.tablero[mov] = "O"
            puntaje = minimax(juego.tablero, profundidad + 1, True)
            juego.tablero[mov] = " "
            mejor = min(mejor, puntaje)
        return mejor

def ia_decidir_movimiento(tablero):
    mejor_puntaje = -float('inf')
    mejor_movimiento = None
    for movimiento in range(9):
        if tablero[movimiento] == " ":
            tablero_copia = deepcopy(tablero)
            tablero_copia[movimiento] = "X"
            puntaje = minimax(tablero_copia, 0, False)
            if puntaje > mejor_puntaje:
                mejor_puntaje = puntaje
                mejor_movimiento = movimiento
    return mejor_movimiento, [] 

# --- SIN LÍMITES: MUESTRA TODO EL ABANICO ---
def generar_camino_visual(tablero, profundidad_max=4):
    
    def construir_nivel(tablero_actual, profundidad, es_turno_ia):
        juego = LogicaTresRayas()
        juego.tablero = tablero_actual
        if profundidad == 0 or juego.juego_terminado():
            return []

        movimientos = juego.obtener_movimientos_posibles()
        nodos_hermanos = []
        
        # 1. Generar TODOS los hijos
        for mov in movimientos:
            tablero_futuro = deepcopy(tablero_actual)
            ficha = "X" if es_turno_ia else "O"
            tablero_futuro[mov] = ficha
            
            utilidad = minimax(tablero_futuro, 0, not es_turno_ia)
            
            nodo = {
                "movimiento": mov,
                "tablero": tablero_futuro,
                "puntaje": utilidad,
                "es_turno_ia": es_turno_ia,
                "es_camino_ganador": False, 
                "sub_ramas": [] 
            }
            nodos_hermanos.append(nodo)
        
        if not nodos_hermanos: return []

        # 2. Identificar MEJOR
        if es_turno_ia:
            mejor_nodo = max(nodos_hermanos, key=lambda x: x["puntaje"])
        else:
            mejor_nodo = min(nodos_hermanos, key=lambda x: x["puntaje"])
        
        mejor_nodo["es_camino_ganador"] = True
        
        # 3. Profundidad Selectiva (Solo el mejor tiene hijos)
        if profundidad > 1:
            mejor_nodo["sub_ramas"] = construir_nivel(
                mejor_nodo["tablero"], 
                profundidad - 1, 
                not es_turno_ia
            )
            
        # 4. Devolvemos TODOS los hermanos (sin recortar a 3)
        # Y ordenamos para que los mejores queden cerca (opcional, pero ayuda visualmente)
        reverse_sort = True if es_turno_ia else False
        nodos_hermanos = sorted(nodos_hermanos, key=lambda x: x["puntaje"], reverse=reverse_sort)

        return nodos_hermanos

    return construir_nivel(tablero, profundidad_max, True)