# logic.py
# Funciones que se encargan de manejar la lógica del juego tres en rayas.

class LogicaTresRayas:

    def __init__(self):
        self.tablero = [" " for _ in range(9)]
        self.ganador = None

    def reiniciar(self):
        self.tablero = [" " for _ in range(9)]
        self.ganador = None

    def existe_espacio_libre(self):
        return " " in self.tablero

    # Función que verifica si el movimiento del jugador es válido:
    # si está colocando su ficha en un espacio que no se encuentra vacio.
    def es_movimiento_valido(self, indice):
        if indice < 0 or indice > 8:
            return False
        return self.tablero[indice] == " "
    
    # Función que añade al tablero el movimiento del jugador
    # siempre y cuando sea un movimiento válido 
    def realizar_movimiento(self, indice, jugador):
        if self.es_movimiento_valido(indice):
            self.tablero[indice] = jugador
            return True
        return False

    # Función que se encarga de verificar si uno de los jugadores ganó
    # verifica a partir de las combinaciones posibles para ganar
    # a partir de filas, columnas o diagonales
    def verificar_ganador(self):
        combinaciones_ganadoras = [
            (0, 1, 2), (3, 4, 5), (6, 7, 8), # Filas
            (0, 3, 6), (1, 4, 7), (2, 5, 8), # Columnas
            (0, 4, 8), (2, 4, 6)             # Diagonales
        ]

        for a,b,c in combinaciones_ganadoras:

            if self.tablero[a] != " " and self.tablero[a] == self.tablero[b] == self.tablero[c]:
                self.ganador = self.tablero[a]
                return self.ganador
        return None

    # Función que indica si el juego ha terminado
    def juego_terminado(self):
        if self.verificar_ganador() is not None:
            return True
        if not self.existe_espacio_libre():
            return True
        return False

    # Función que le indicará al agente como al jugador qué espacios
    # se encuentran libres en el tablero para poder jugar
    def obtener_movimientos_posibles(self):
        movimientos = []
        for i in range(9):
            if self.tablero[i] == " ":
                movimientos.append(i)
        return movimientos