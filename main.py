import time
from game.logic import LogicaTresRayas
from game.ai import ia_decidir_movimiento, generar_camino_visual
from ui.interface import InterfazGrafica

def main():
    juego = LogicaTresRayas()
    ui = InterfazGrafica()
    
    turno = "X"
    mensaje_estado = "Juega la IA (X)"
    juego_corriendo = True
    
    # Estado Inicial
    nodo_inicio = {
        "movimiento": None,
        "tablero": list(juego.tablero),
        "puntaje": "Inicio",
        "es_camino_ganador": True,
        "sub_ramas": []
    }
    
    trayectoria_contextual = []
    trayectoria_contextual.append({
        "elegido": nodo_inicio,
        "hermanos": [nodo_inicio] 
    })

    arbol_futuro = []

    while juego_corriendo:
        ui.dibujar_interfaz(juego.tablero, mensaje_estado, 
                            trayectoria=trayectoria_contextual, 
                            arbol_futuro=arbol_futuro)

        evento = ui.obtener_evento_usuario()
        if evento == 'SALIR': break
        if evento == 'REINICIAR':
            juego.reiniciar()
            turno = "X"
            mensaje_estado = "Juega la IA (X)"
            trayectoria_contextual = [{"elegido": nodo_inicio, "hermanos": [nodo_inicio]}]
            arbol_futuro = []
            continue

        if juego.juego_terminado():
            ganador = juego.verificar_ganador()
            mensaje_estado = f"¡Ganó {ganador}!" if ganador else "¡Empate!"
            continue

        if turno == "X":
            mensaje_estado = "Pensando..."
            ui.dibujar_interfaz(juego.tablero, mensaje_estado, 
                                trayectoria=trayectoria_contextual, 
                                arbol_futuro=arbol_futuro)
            
            # Generar futuro (Nivel 1 ancho, niveles 2+ recortados a 3)
            arbol_futuro = generar_camino_visual(juego.tablero, profundidad_max=4)
            
            ui.dibujar_interfaz(juego.tablero, mensaje_estado, 
                                trayectoria=trayectoria_contextual, 
                                arbol_futuro=arbol_futuro)
            time.sleep(0.5)

            # Mover
            movimiento, _ = ia_decidir_movimiento(juego.tablero)
            juego.realizar_movimiento(movimiento, "X")
            
            # Guardar Contexto
            nodo_elegido = None
            todos_los_hermanos = []
            
            if arbol_futuro:
                # 'arbol_futuro' ya viene filtrado (max 3 nodos) desde ai.py si estamos profundizando,
                # o completo si es el primer nivel.
                todos_los_hermanos = arbol_futuro 
                for nodo in arbol_futuro:
                    if nodo["movimiento"] == movimiento:
                        nodo_elegido = nodo
                        nodo_elegido["es_camino_ganador"] = True
                        nodo_elegido["puntaje"] = ""
                        nodo_elegido["sub_ramas"] = []
                    else:
                        nodo["es_camino_ganador"] = False
                        nodo["sub_ramas"] = []
            
            if not nodo_elegido: 
                 nodo_elegido = {"tablero": list(juego.tablero), "es_camino_ganador": True, "puntaje": "", "sub_ramas": []}
                 todos_los_hermanos = [nodo_elegido]

            # --- GUARDAR TODO EL CONTEXTO (Elegido + sus 2 mejores alternativas) ---
            trayectoria_contextual.append({
                "elegido": nodo_elegido, 
                "hermanos": todos_los_hermanos 
            })
            
            arbol_futuro = [] 
            turno = "O"
            mensaje_estado = "Tu turno"

        else: # Turno Humano
            if isinstance(evento, int):
                if juego.es_movimiento_valido(evento):
                    # Generar opciones para el humano
                    opciones_humano = generar_camino_visual(juego.tablero, profundidad_max=1)
                    
                    juego.realizar_movimiento(evento, "O")
                    
                    nodo_elegido = None
                    # Aquí también aplicamos el filtro manual si queremos consistencia
                    # Ordenamos y nos quedamos con top 3 para el historial
                    opciones_ordenadas = sorted(opciones_humano, key=lambda x: x["puntaje"]) # Humano minimiza
                    
                    # Buscar el elegido
                    for nodo in opciones_ordenadas:
                        if nodo["movimiento"] == evento:
                            nodo_elegido = nodo
                            nodo_elegido["es_camino_ganador"] = True
                            nodo_elegido["puntaje"] = ""
                            nodo_elegido["sub_ramas"] = []
                            break
                    
                    # Si el elegido está entre los top 3, guardamos top 3.
                    # Si el humano hizo una jugada "mala" (fuera del top 3), tenemos que incluirla.
                    if nodo_elegido in opciones_ordenadas[:3]:
                        todos_los_hermanos = opciones_ordenadas[:3]
                    else:
                        # Caso especial: Jugada atípica. Mostramos Top 2 + La jugada real
                        todos_los_hermanos = opciones_ordenadas[:2] + [nodo_elegido]
                        # Reordenamos por movimiento para que se vea ordenado
                        todos_los_hermanos = sorted(todos_los_hermanos, key=lambda x: x["movimiento"])

                    if not nodo_elegido: # Fallback
                        nodo_elegido = {"tablero": list(juego.tablero), "es_camino_ganador": True, "puntaje": "", "sub_ramas": []}
                        todos_los_hermanos = [nodo_elegido]

                    trayectoria_contextual.append({
                        "elegido": nodo_elegido,
                        "hermanos": todos_los_hermanos
                    })

                    arbol_futuro = []
                    turno = "X"
    ui.cerrar()

if __name__ == "__main__":
    main()