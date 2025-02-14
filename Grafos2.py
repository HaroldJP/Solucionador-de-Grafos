import gurobipy as gp
from gurobipy import GRB

class OptimizacionRedes:
    def __init__(self, grafo):
        self.grafo = grafo
        self.modelo = gp.Model("Optimización en Redes")
    
    def flujo_maximo(self, origen, destino):
        """Resuelve el problema de flujo máximo"""
        flujo = self.modelo.addVars(self.grafo, name="flujo")
        self.modelo.setObjective(gp.quicksum(flujo[origen, j] for j in self.grafo if (origen, j) in self.grafo), GRB.MAXIMIZE)
        
        for i, j in self.grafo:
            self.modelo.addConstr(flujo[i, j] <= self.grafo[i, j]['capacidad'], f"cap_{i}_{j}")
        
        for nodo in set(i for i, _ in self.grafo) | set(j for _, j in self.grafo):
            if nodo != origen and nodo != destino:
                self.modelo.addConstr(
                    gp.quicksum(flujo[i, nodo] for i in self.grafo if (i, nodo) in self.grafo) ==
                    gp.quicksum(flujo[nodo, j] for j in self.grafo if (nodo, j) in self.grafo),
                    f"conserv_flujo_{nodo}")
        
        self.modelo.optimize()
        return {arco: flujo[arco].x for arco in self.grafo if flujo[arco].x > 0}
    
    def ruta_mas_corta(self, inicio, fin):
        """Resuelve el problema de la ruta más corta"""
        x = self.modelo.addVars(self.grafo, vtype=GRB.BINARY, name="x")
        self.modelo.setObjective(gp.quicksum(self.grafo[i, j]['costo'] * x[i, j] for i, j in self.grafo), GRB.MINIMIZE)
        
        for nodo in set(i for i, _ in self.grafo) | set(j for _, j in self.grafo):
            if nodo == inicio:
                self.modelo.addConstr(gp.quicksum(x[nodo, j] for j in self.grafo if (nodo, j) in self.grafo) -
                                     gp.quicksum(x[i, nodo] for i in self.grafo if (i, nodo) in self.grafo) == 1)
            elif nodo == fin:
                self.modelo.addConstr(gp.quicksum(x[nodo, j] for j in self.grafo if (nodo, j) in self.grafo) -
                                     gp.quicksum(x[i, nodo] for i in self.grafo if (i, nodo) in self.grafo) == -1)
            else:
                self.modelo.addConstr(gp.quicksum(x[nodo, j] for j in self.grafo if (nodo, j) in self.grafo) -
                                     gp.quicksum(x[i, nodo] for i in self.grafo if (i, nodo) in self.grafo) == 0)
        
        self.modelo.optimize()
        return [arco for arco in self.grafo if x[arco].x > 0.5]
    
    def problema_transporte(self, oferta, demanda):
        """Resuelve el problema de transporte"""
        flujo = self.modelo.addVars(self.grafo, name="flujo")
        self.modelo.setObjective(gp.quicksum(self.grafo[i, j]['costo'] * flujo[i, j] for i, j in self.grafo), GRB.MINIMIZE)
        
        for i in oferta:
            self.modelo.addConstr(gp.quicksum(flujo[i, j] for j in self.grafo if (i, j) in self.grafo) == oferta[i])
        
        for j in demanda:
            self.modelo.addConstr(gp.quicksum(flujo[i, j] for i in self.grafo if (i, j) in self.grafo) == demanda[j])
        
        self.modelo.optimize()
        return {arco: flujo[arco].x for arco in self.grafo if flujo[arco].x > 0}
    
    def costo_minimo(self):
        """Resuelve el problema de costo mínimo"""
        x = self.modelo.addVars(self.grafo, vtype=GRB.BINARY, name="x")
        self.modelo.setObjective(gp.quicksum(self.grafo[i, j]['costo'] * x[i, j] for i, j in self.grafo), GRB.MINIMIZE)
        
        for i, j in self.grafo:
            self.modelo.addConstr(x[i, j] <= 1, f"arco_{i}_{j}")
        
        self.modelo.optimize()
        return {arco: x[arco].x for arco in self.grafo if x[arco].x > 0}
    
    def resolver(self, tipo_problema, **kwargs):
        if tipo_problema == 'flujo_maximo':
            return self.flujo_maximo(kwargs['origen'], kwargs['destino'])
        elif tipo_problema == 'ruta_mas_corta':
            return self.ruta_mas_corta(kwargs['inicio'], kwargs['fin'])
        elif tipo_problema == 'transporte':
            return self.problema_transporte(kwargs['oferta'], kwargs['demanda'])
        elif tipo_problema == 'costo_minimo':
            return self.costo_minimo()
        else:
            raise ValueError("Tipo de problema no soportado")

# Ejemplo de uso:
grafo = {
    ("A", "B"): {'capacidad': 10, 'costo': 1},
    ("A", "C"): {'capacidad': 15, 'costo': 2},
    ("B", "D"): {'capacidad': 10, 'costo': 1},
    ("C", "D"): {'capacidad': 10, 'costo': 1}
}

optimizador = OptimizacionRedes(grafo)
print(optimizador.resolver('flujo_maximo', origen='A', destino='D'))
print(optimizador.resolver('ruta_mas_corta', inicio='A', fin='D'))

oferta = {"A": 20, "B": 10}
demanda = {"C": 15, "D": 15}
print(optimizador.resolver('transporte', oferta=oferta, demanda=demanda))

print(optimizador.resolver('costo_minimo'))
