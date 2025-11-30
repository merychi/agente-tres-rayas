# ai.py
# Módulo de Inteligencia Artificial basado en el algoritmo Minimax.
# Este módulo se encarga de calcular el movimiento óptimo para la computadora.

from game.logic import LogicaTresRayas
from copy import deepcopy 

def minimax(tablero, profundidad, es_turno_max):
    """
    Función recursiva que simula todos los posibles juegos futuros.
    
    Parámetros:
    - tablero: Estado actual del tablero (lista de 9 elementos).
    - profundidad: Nivel actual en el árbol de decisión (qué tan lejos estamos del inicio).
    - es_turno_max: Booleano. True si juega la IA (Maximizador), False si juega el Humano (Minimizador).
    """
    
    # Instanciamos la lógica solo para usar sus métodos de verificación (ganador/empate)
    juego = LogicaTresRayas()
    juego.tablero = tablero 
    ganador = juego.verificar_ganador()

    # --- 1. CASO BASE (Estados Terminales) ---
    
    # Si la IA (X) gana, retornamos un valor positivo.
    # Restamos la profundidad para premiar las victorias más rápidas (menos movimientos).
    if ganador == "X":
        return 10 - profundidad 
    
    # Si el Humano (O) gana, retornamos un valor negativo.
    # Sumamos la profundidad (o restamos de un negativo) para que la IA prefiera perder tarde a perder temprano.
    elif ganador == "O":
        return profundidad - 10 
    
    # Si no hay espacios libres y nadie ganó, es un Empate.
    elif not juego.existe_espacio_libre():
        return 0 

    # --- 2. PASO RECURSIVO ---
    
    if es_turno_max:
        # Turno de la IA (MAX): Busca el valor más alto posible.
        mejor_puntaje = -float('inf')
        
        for movimiento in juego.obtener_movimientos_posibles():
            # Simular movimiento
            juego.tablero[movimiento] = "X" 
            
            # Llamada recursiva: Ahora es turno del oponente (False)
            puntaje = minimax(juego.tablero, profundidad + 1, False)
            
            # Deshacer movimiento (Backtracking) para probar el siguiente
            juego.tablero[movimiento] = " "
            
            # Nos quedamos con el puntaje más alto encontrado
            mejor_puntaje = max(mejor_puntaje, puntaje)
            
        return mejor_puntaje
    
    else:
        # Turno del Humano (MIN): Asumimos que jugará perfecto para perjudicarnos.
        # Busca el valor más bajo posible (hacernos perder).
        mejor_puntaje = float('inf')
        
        for movimiento in juego.obtener_movimientos_posibles():
            # Simular movimiento del oponente
            juego.tablero[movimiento] = "O"
            
            # Llamada recursiva: Ahora es turno de la IA (True)
            puntaje = minimax(juego.tablero, profundidad + 1, True)
            
            # Deshacer movimiento
            juego.tablero[movimiento] = " "
            
            # Nos quedamos con el puntaje más bajo (el peor escenario para la IA)
            mejor_puntaje = min(mejor_puntaje, puntaje)
            
        return mejor_puntaje


def ia_decidir_movimiento(tablero):
    """
    Función principal que la interfaz llama para obtener la jugada de la IA.
    Retorna el mejor índice (0-8) y una lista de datos para visualizar el grafo.
    """
    datos_grafico = [] # Lista de tuplas (indice, puntaje) para el requerimiento de la GUI
    mejor_puntaje = -float('inf')
    mejor_movimiento = None

    # Iteramos sobre todas las casillas disponibles en el tablero real
    for movimiento in range(9):
        if tablero[movimiento] == " ":
            # Creamos una copia para no alterar el tablero del juego actual
            tablero_copia = deepcopy(tablero)
            
            # La IA prueba poner su ficha ("X")
            tablero_copia[movimiento] = "X" 
            
            # Calculamos el valor de esta jugada usando Minimax.
            # Pasamos 'False' porque después de que la IA juega, le toca al Humano.
            puntaje = minimax(tablero_copia, 0, False)
            
            # Guardamos el puntaje para mostrarlo en la interfaz (requisito del proyecto)
            datos_grafico.append((movimiento, puntaje))
            
            # Si esta jugada tiene mejor puntuación que la anterior, la elegimos
            if puntaje > mejor_puntaje:
                mejor_puntaje = puntaje
                mejor_movimiento = movimiento
    
    return mejor_movimiento, datos_grafico