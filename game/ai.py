# game/ai.py
from game.logic import LogicaTresRayas
from copy import deepcopy

def minimax(tablero, profundidad, es_turno_max):
    """
    Función recursiva que simula todos los posibles juegos futuros.
    """
    juego = LogicaTresRayas()
    juego.tablero = list(tablero)
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

# -------------------------
# Funciones nuevas para mostrar raíz fija + camino real
# -------------------------

def generar_arbol_inicial():
    """
    Genera el nivel raíz: tablero vacío y sus 9 hijos (X en cada casilla).
    Cada hijo contiene su tablero y su puntaje (minimax desde ahí).
    """
    tablero_vacio = [" " for _ in range(9)]
    hijos = []

    for mov in range(9):
        tablero_fut = deepcopy(tablero_vacio)
        tablero_fut[mov] = "X"
        # Tras colocar X, el siguiente turno es O -> es_turno_max False
        puntaje = minimax(tablero_fut, 0, False)
        nodo = {
            "movimiento": mov,
            "tablero": tablero_fut,
            "puntaje": puntaje,
            "es_turno_ia": True,
            "sub_ramas": []
        }
        hijos.append(nodo)

    return {
        "movimiento": None,
        "tablero": tablero_vacio,
        "puntaje": None,
        "es_turno_ia": True,
        "sub_ramas": hijos
    }

def reconstruir_camino_real(tablero_actual, profundidad_max=8):
    """
    Reconstruye un camino real plausible (un único nodo por nivel) a partir
    del tablero actual, asumiendo que la partida comenzó vacío y que las
    jugadas se alternan X (IA) -> O (humano) -> X -> ...
    Devuelve una lista de nodos en orden (tableros después de cada jugada).
    """
    # Copia para no modificar original
    objetivo = list(tablero_actual)
    tablero_sim = [" " for _ in range(9)]
    camino_nodos = []

    # Conteo de fichas ya en el tablero: nos indica cuántos pasos hubo
    total_jugadas = sum(1 for c in objetivo if c != " ")

    # Simulamos jugadas desde 0 hasta total_jugadas-1
    for paso in range(total_jugadas):
        ficha = "X" if paso % 2 == 0 else "O"  # X inicia
        # Elegir una casilla que en 'objetivo' tiene la ficha y que aún no esté puesta en 'tablero_sim'
        candidato = None
        for i in range(9):
            if objetivo[i] == ficha and tablero_sim[i] == " ":
                candidato = i
                break
        if candidato is None:
            # No se encontró (caso borde) -> rompe
            break

        tablero_sim[candidato] = ficha
        # Después de esta jugada, calculamos puntaje para visualización.
        # Tras haber jugado ficha en candidato, el siguiente turno es opuesto:
        es_turno_max = (ficha == "X")  # si acaba de jugar X, es_turno_max True para X? Para minimax pasamos el turno siguiente
        # Minimun/Max flag expected for next recursive call: if next turn is X => es_turno_max True
        # Pero aquí queremos una evaluación desde el tablero actual: si next is X => es_turno_max True
        siguiente_turno_es_X = (ficha == "O")
        puntaje = minimax(deepcopy(tablero_sim), 0, siguiente_turno_es_X)

        nodo = {
            "movimiento": candidato,
            "tablero": deepcopy(tablero_sim),
            "puntaje": puntaje,
            "es_turno_ia": (ficha == "X"),
            "sub_ramas": []
        }
        camino_nodos.append(nodo)

    return camino_nodos

def generar_arbol_combinado(tablero_actual, profundidad_camino=8):
    """
    Genera el árbol completo que se dibujará:
    - Raíz = tablero vacío con 9 hijos (X en cada casilla).
    - Encuentra la PRIMERA jugada de la IA (primer 'X' en tablero_actual).
    - Reconstruye el camino real desde el inicio y lo inserta como sub_ramas
      del hijo inicial correspondiente (solo 1 nodo por nivel).
    """
    # Generamos la raíz con las 9 posibilidades
    raiz = generar_arbol_inicial()
    hijos = raiz["sub_ramas"]

    # Reconstruimos el camino real desde el tablero actual
    camino = reconstruir_camino_real(tablero_actual, profundidad_max=profundidad_camino)

    if not camino:
        # No hay jugadas aún, retornamos solo la raíz
        return raiz["sub_ramas"]

    # Identificamos la PRIMERA jugada de la IA en el tablero actual
    # Buscamos el primer nodo en 'camino' que tenga 'es_turno_ia' True (debe ser el paso 0 normalmente)
    primera_x_idx = None
    for nodo in camino:
        if nodo["es_turno_ia"]:
            primera_x_idx = nodo["movimiento"]
            break

    # Si no encontramos una X (raro), no combinamos.
    if primera_x_idx is None:
        return raiz["sub_ramas"]

    # Localizamos el hijo correspondiente en la raíz (movimiento == primera_x_idx)
    hijo_objetivo = None
    for hijo in hijos:
        if hijo["movimiento"] == primera_x_idx:
            hijo_objetivo = hijo
            break

    if hijo_objetivo is None:
        # Por seguridad, devolvemos la raíz sin modificar
        return raiz["sub_ramas"]

    # Ahora creamos la sub_rama única que representa el resto del camino real,
    # empezando desde el nodo que coincide con la primera X (es decir, omitimos el primer nodo del camino,
    # porque el hijo de la raíz ya representa el primer X).
    # Encontramos la posición en 'camino' del primer nodo con movimiento == primera_x_idx
    pos_inicio = next((i for i, n in enumerate(camino) if n["movimiento"] == primera_x_idx and n["es_turno_ia"]), None)

    if pos_inicio is None:
        return raiz["sub_ramas"]

    # Construir sub_ramas encadenadas (cada nodo tiene sub_ramas = [siguiente_nodo])
    # Empezamos desde pos_inicio + 1, porque el hijo de la raíz ya es el tablero tras la primera X.
    sub_actual = []
    for i in range(pos_inicio + 1, len(camino)):
        nodo = deepcopy(camino[i])
        nodo["sub_ramas"] = []  # se irá encadenando
        if not sub_actual:
            sub_actual = [nodo]
        else:
            # anidar: el último nodo en sub_actual debe contener este nodo como sub_ramas
            # Para recorrer hasta el último en la cadena:
            cursor = sub_actual[0]
            while cursor["sub_ramas"]:
                cursor = cursor["sub_ramas"][0]
            cursor["sub_ramas"] = [nodo]

    # Asignar las sub_ramas creadas al hijo objetivo
    hijo_objetivo["sub_ramas"] = sub_actual

    return raiz["sub_ramas"]
