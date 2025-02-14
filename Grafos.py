from gurobipy import Model, GRB, quicksum

def resolver_grafo(tipo_problema, nodos, aristas, costos, capacidades=None, demandas=None, origen=None, destino=None):
    """

    Parámetros:
    - tipo_problema: "ruta_mas_corta", "transporte", "costo_minimo", "flujo_maximo".
    - nodos: Lista de nodos.
    - aristas: Lista de tuplas (i, j) que representan las aristas.
    - costos: Diccionario de costos {(i, j): costo}.
    - capacidades: Diccionario de capacidades {(i, j): capacidad} (solo para flujo máximo).
    - demandas: Diccionario de demandas {i: demanda} (solo para transporte y costo mínimo).
    - origen: Nodo de origen (solo para ruta más corta y flujo máximo).
    - destino: Nodo de destino (solo para ruta más corta y flujo máximo).
    """
    # Crear el modelo
    modelo = Model("Problema_de_Grafo")

    # Variables de decisión
    x = modelo.addVars(aristas, name="x")

    # Función objetivo
    if tipo_problema == "ruta_mas_corta":
        modelo.setObjective(quicksum(costos[i, j] * x[i, j] for (i, j) in aristas), GRB.MINIMIZE)
    elif tipo_problema == "transporte" or tipo_problema == "costo_minimo":
        modelo.setObjective(quicksum(costos[i, j] * x[i, j] for (i, j) in aristas), GRB.MINIMIZE)
    elif tipo_problema == "flujo_maximo":
        modelo.setObjective(x[origen, destino], GRB.MAXIMIZE)

    # Restricciones
    if tipo_problema == "ruta_mas_corta":
        # Restricción de origen: flujo sale del origen
        modelo.addConstr(quicksum(x[origen, j] for j in nodos if (origen, j) in aristas) == 1)
        # Restricción de destino: flujo llega al destino
        modelo.addConstr(quicksum(x[i, destino] for i in nodos if (i, destino) in aristas) == 1)
        # Restricción de conservación de flujo en otros nodos
        for i in nodos:
            if i != origen and i != destino:
                modelo.addConstr(
                    quicksum(x[j, i] for j in nodos if (j, i) in aristas) ==
                    quicksum(x[i, j] for j in nodos if (i, j) in aristas)
    elif tipo_problema == "transporte" or tipo_problema == "costo_minimo":
        # Restricciones de oferta y demanda
        for i in nodos:
            if i in demandas:
                if demandas[i] > 0:  # Demanda
                    modelo.addConstr(quicksum(x[i, j] for j in nodos if (i, j) in aristas) == demandas[i])
                else:  # Oferta
                    modelo.addConstr(quicksum(x[j, i] for j in nodos if (j, i) in aristas) == -demandas[i])
    elif tipo_problema == "flujo_maximo":
        # Restricciones de capacidad
        for (i, j) in aristas:
            modelo.addConstr(x[i, j] <= capacidades[i, j])
        # Restricción de conservación de flujo en todos los nodos excepto origen y destino
        for i in nodos:
            if i != origen and i != destino:
                modelo.addConstr(
                    quicksum(x[j, i] for j in nodos if (j, i) in aristas) ==
                    quicksum(x[i, j] for j in nodos if (i, j) in aristas))

    # Resolver el modelo
    modelo.optimize()

    # Mostrar resultados
    if modelo.status == GRB.OPTIMAL:
        print("Solución óptima encontrada:")
        for (i, j) in aristas:
            if x[i, j].x > 0:
                print(f"Flujo en arista ({i}, {j}): {x[i, j].x}")
        if tipo_problema == "ruta_mas_corta":
            print(f"Costo total de la ruta más corta: {modelo.objVal}")
        elif tipo_problema == "flujo_maximo":
            print(f"Flujo máximo: {modelo.objVal}")
    else:
        print("No se encontró una solución óptima.")

# Ejemplo de uso
if __name__ == "__main__":
    # Definir el grafo
    nodos = [1, 2, 3, 4]
    aristas = [(1, 2), (2,4), (2,3), (1,4), (3,1)]
    costos = {(1, 2): 2, (1, 3): 4, (2, 3): 1, (2, 4): 7, (3, 4): 3}
    capacidades = {(1, 2): 5, (1, 3): 3, (2, 3): 2, (2, 4): 4, (3, 4): 5}
    demandas = {1: -10, 2: 0, 3: 0, 4: 10}  # Oferta en 1, demanda en 4

    # Resolver diferentes tipos de problemas
    print("=== Ruta más corta ===")
    resolver_grafo("ruta_mas_corta", nodos, aristas, costos, origen=1, destino=4)

    # print("\n=== Problema de transporte ===")
    # resolver_grafo("transporte", nodos, aristas, costos, demandas=demandas)

    # print("\n=== Flujo máximo ===")
    # resolver_grafo("flujo_maximo", nodos, aristas, costos, capacidades=capacidades, origen=1, destino=4)