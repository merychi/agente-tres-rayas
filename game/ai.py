# game/ai.py
from game.logic import LogicaTresRayas
from copy import deepcopy

# --- MEMORIA GLOBAL (CACHE) ---
CACHE_MINIMAX = {}

def limpiar_cache():
    """Limpia la memoria para reiniciar partida"""
    CACHE_MINIMAX.clear()

def minimax(tablero, profundidad, es_turno_max):
    """
    Algoritmo Minimax estándar.
    Retorna el puntaje de utilidad del tablero dado.
    """
    # Usamos tupla para que sea hashable en el diccionario
    estado_clave = (tuple(tablero), es_turno_max)
    
    if estado_clave in CACHE_MINIMAX:
        return CACHE_MINIMAX[estado_clave]

    juego = LogicaTresRayas()
    juego.tablero = list(tablero)
    ganador = juego.verificar_ganador()

    # Evaluación estática
    if ganador == "X":
        return 10 - profundidad
    elif ganador == "O":
        return profundidad - 10
    elif not juego.existe_espacio_libre():
        return 0

    # Recursión
    movimientos = juego.obtener_movimientos_posibles()
    
    if es_turno_max: # Turno de la IA (X)
        mejor_puntaje = -float('inf')
        for mov in movimientos:
            juego.tablero[mov] = "X"
            puntaje = minimax(juego.tablero, profundidad + 1, False)
            juego.tablero[mov] = " " # Backtracking
            mejor_puntaje = max(mejor_puntaje, puntaje)
    else: # Turno del Humano (O)
        mejor_puntaje = float('inf')
        for mov in movimientos:
            juego.tablero[mov] = "O"
            puntaje = minimax(juego.tablero, profundidad + 1, True)
            juego.tablero[mov] = " " # Backtracking
            mejor_puntaje = min(mejor_puntaje, puntaje)
    
    CACHE_MINIMAX[estado_clave] = mejor_puntaje
    return mejor_puntaje

def ia_decidir_movimiento(tablero):
    """
    Decide el mejor movimiento para la IA en el estado actual.
    Retorna: (mejor_movimiento, datos_visuales_no_usados)
    """
    mejor_puntaje = -float('inf')
    mejor_movimiento = None
    
    # Probamos todas las opciones disponibles
    for movimiento in range(9):
        if tablero[movimiento] == " ":
            tablero_copia = list(tablero)
            tablero_copia[movimiento] = "X"
            
            # Calculamos qué tan buena es esta jugada
            puntaje = minimax(tablero_copia, 0, False)
            
            if puntaje > mejor_puntaje:
                mejor_puntaje = puntaje
                mejor_movimiento = movimiento
                
    return mejor_movimiento, []

# ---------------------------------------------------------
#  NUEVA FUNCIÓN DE VISUALIZACIÓN UNIFICADA (REFACTORIZADA)
# ---------------------------------------------------------

def generar_arbol_visual(tablero_final):
    """
    Reconstruye la historia de la partida para generar el árbol visual completo.
    
    Lógica:
    1. Deduce el orden de los movimientos realizados en 'tablero_final'.
    2. Simula la partida desde el tablero vacío.
    3. En CADA turno, genera todos los hijos posibles (abanico).
    4. Marca el hijo que coincide con la jugada real como 'es_camino_ganador'.
    5. Solo ese hijo real tendrá 'sub_ramas' (el siguiente nivel).
    """
    
    # 1. Deducir la secuencia de jugadas (Ingeniería inversa simple)
    # Asumimos X empieza. Buscamos qué fichas hay puestas.
    # Nota: Como el orden exacto no se guarda en el tablero estático, 
    # esta reconstrucción asume un orden secuencial lógico para visualización.
    # Si quieres precisión histórica exacta, deberías pasar el historial real desde main.py.
    # Pero para mantener compatibilidad con tu código actual, usamos la lógica de reconstrucción.
    
    secuencia_reconstruida = []
    tablero_temp = [" "]*9
    copia_final = list(tablero_final)
    total_fichas = sum(1 for c in copia_final if c != " ")
    
    for _ in range(total_fichas):
        turno_actual = "X" if len(secuencia_reconstruida) % 2 == 0 else "O"
        
        # Buscamos la primera diferencia entre el tablero vacío temporal y el final
        # Si el tablero final es el resultado de una partida,
        # esta lógica reconstruye el camino jugado.
        movimiento_encontrado = None
        
        # Esta heurística simple busca la primera casilla que coincida.
        # Funciona visualmente para mostrar un camino válido.
        for i in range(9):
            if copia_final[i] == turno_actual and tablero_temp[i] == " ":
                movimiento_encontrado = i
                break
        
        if movimiento_encontrado is not None:
            secuencia_reconstruida.append((movimiento_encontrado, turno_actual))
            tablero_temp[movimiento_encontrado] = turno_actual
        else:
            break

    # 2. Construir el Árbol Recursivo (Nivel por Nivel)
    def construir_nivel_recursivo(tablero_actual, paso_idx):
        # Condición de parada: Si ya llegamos al final de la historia
        if paso_idx >= len(secuencia_reconstruida):
            return []

        mov_real, turno_quien_jugo = secuencia_reconstruida[paso_idx]
        
        # Generar todos los posibles movimientos desde este estado
        nodos_hermanos = []
        movimientos_posibles = [i for i, c in enumerate(tablero_actual) if c == " "]
        
        nodo_camino_real = None

        for mov in movimientos_posibles:
            t_futuro = list(tablero_actual)
            t_futuro[mov] = turno_quien_jugo
            
            # Calculamos puntaje
            es_turno_max_siguiente = (turno_quien_jugo == "O") # Si jugó O, le toca a X (MAX)
            puntaje = minimax(t_futuro, 0, es_turno_max_siguiente)
            
            es_el_elegido = (mov == mov_real)
            
            nodo = {
                "movimiento": mov,
                "tablero": t_futuro,
                "puntaje": puntaje,
                "es_camino_ganador": es_el_elegido, # Marca dorada
                "sub_ramas": [] 
            }
            nodos_hermanos.append(nodo)
            
            if es_el_elegido:
                nodo_camino_real = nodo
        
        # RECURSIVIDAD: Solo el nodo real genera el siguiente nivel
        if nodo_camino_real:
            nodo_camino_real["sub_ramas"] = construir_nivel_recursivo(
                nodo_camino_real["tablero"], 
                paso_idx + 1
            )
            
        return nodos_hermanos

    # Arrancamos desde tablero vacío
    return construir_nivel_recursivo([" "]*9, 0)
