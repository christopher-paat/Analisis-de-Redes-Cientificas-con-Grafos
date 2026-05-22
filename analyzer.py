"""
Análisis de la red de colaboración científica.
Área: Sistemas Distribuidos

Incluye:
  a) Caminos mínimos (Dijkstra y BFS)
  b) Centralidad (Degree, Betweenness, Closeness)
  c) Componentes conexas
  d) Detección de comunidades (Louvain)
"""

import os
import networkx as nx
import community as community_louvain

GRAPH_FILE = os.path.join("data", "graph.graphml")


def load_graph(path: str) -> nx.Graph:
    G = nx.read_graphml(path)
    # Convertir pesos a enteros
    for u, v, d in G.edges(data=True):
        d["weight"] = int(d.get("weight", 1))
    return G


# ─────────────────────────────────────────
# a) CAMINOS MÍNIMOS
# ─────────────────────────────────────────

def analizar_caminos(G: nx.Graph) -> None:
    print(f"\n{'='*55}")
    print("  a) CAMINOS MINIMOS")
    print(f"{'='*55}")

    # Seleccionar los 2 autores con mayor grado para el ejemplo
    top2 = sorted(G.degree(), key=lambda x: x[1], reverse=True)[:2]
    origen_id,  _ = top2[0]
    destino_id, _ = top2[1]
    origen_name  = G.nodes[origen_id].get("name", origen_id)
    destino_name = G.nodes[destino_id].get("name", destino_id)

    # Verificar que estén en el mismo componente
    if not nx.has_path(G, origen_id, destino_id):
        print(f"  {origen_name} y {destino_name} no estan conectados.")
        return

    # Dijkstra (considera pesos — menor peso = camino preferido)
    # Usamos 1/weight para que mayor colaboración = distancia menor
    for u, v, d in G.edges(data=True):
        d["inv_weight"] = 1 / d["weight"]

    path_dijkstra = nx.dijkstra_path(G, origen_id, destino_id, weight="inv_weight")
    dist_dijkstra = nx.dijkstra_path_length(G, origen_id, destino_id, weight="inv_weight")

    # BFS (sin peso — menor número de saltos)
    path_bfs = nx.shortest_path(G, origen_id, destino_id)

    print(f"\n  Origen : {origen_name}")
    print(f"  Destino: {destino_name}")

    print(f"\n  [Dijkstra] Distancia ponderada: {dist_dijkstra:.4f}")
    print(f"  Ruta ({len(path_dijkstra)-1} saltos):")
    for nid in path_dijkstra:
        print(f"    -> {G.nodes[nid].get('name', nid)}")

    print(f"\n  [BFS] Saltos minimos: {len(path_bfs)-1}")
    print(f"  Ruta:")
    for nid in path_bfs:
        print(f"    -> {G.nodes[nid].get('name', nid)}")

    # Diámetro y radio sobre el componente gigante
    giant_nodes = max(nx.connected_components(G), key=len)
    Gc = G.subgraph(giant_nodes)
    print(f"\n  Diametro de la componente gigante : {nx.diameter(Gc)}")
    print(f"  Radio de la componente gigante    : {nx.radius(Gc)}")


# ─────────────────────────────────────────
# b) CENTRALIDAD
# ─────────────────────────────────────────

def analizar_centralidad(G: nx.Graph) -> dict:
    print(f"\n{'='*55}")
    print("  b) CENTRALIDAD")
    print(f"{'='*55}")

    degree_cent     = nx.degree_centrality(G)
    betweenness_cent = nx.betweenness_centrality(G, weight="inv_weight")
    closeness_cent  = nx.closeness_centrality(G)

    def top5(metric: dict, label: str) -> None:
        ranking = sorted(metric.items(), key=lambda x: x[1], reverse=True)[:5]
        print(f"\n  Top 5 - {label}:")
        for i, (nid, val) in enumerate(ranking, 1):
            name = G.nodes[nid].get("name", nid)
            print(f"    {i}. {name} ({val:.4f})")

    top5(degree_cent,      "Degree Centrality      (mas colaboradores directos)")
    top5(betweenness_cent, "Betweenness Centrality (mayor puente entre autores)")
    top5(closeness_cent,   "Closeness Centrality   (mas cercano a todos)")

    return {
        "degree": degree_cent,
        "betweenness": betweenness_cent,
        "closeness": closeness_cent,
    }


# ─────────────────────────────────────────
# c) COMPONENTES CONEXAS
# ─────────────────────────────────────────

def analizar_componentes(G: nx.Graph) -> None:
    print(f"\n{'='*55}")
    print("  c) COMPONENTES CONEXAS")
    print(f"{'='*55}")

    components = sorted(nx.connected_components(G), key=len, reverse=True)
    aislados   = [n for n, d in G.degree() if d == 0]

    print(f"\n  Total de componentes  : {len(components)}")
    print(f"  Autores aislados      : {len(aislados)}")
    print(f"  Componente gigante    : {len(components[0])} nodos")

    print(f"\n  Tamano de las 10 componentes mas grandes:")
    for i, comp in enumerate(components[:10], 1):
        print(f"    {i}. {len(comp)} nodos")

    print(f"\n  Autores en la componente gigante (muestra de 5):")
    for nid in list(components[0])[:5]:
        print(f"    - {G.nodes[nid].get('name', nid)}")


# ─────────────────────────────────────────
# d) DETECCIÓN DE COMUNIDADES (Louvain)
# ─────────────────────────────────────────

def analizar_comunidades(G: nx.Graph) -> dict:
    print(f"\n{'='*55}")
    print("  d) DETECCION DE COMUNIDADES (Louvain)")
    print(f"{'='*55}")

    partition = community_louvain.best_partition(G, weight="weight")
    modularity = community_louvain.modularity(partition, G, weight="weight")

    # Agrupar nodos por comunidad
    comunidades: dict[int, list] = {}
    for nid, cid in partition.items():
        comunidades.setdefault(cid, []).append(nid)

    comunidades_ord = sorted(comunidades.items(), key=lambda x: len(x[1]), reverse=True)

    print(f"\n  Comunidades detectadas : {len(comunidades)}")
    print(f"  Modularidad            : {modularity:.4f}")
    print(f"  (Modularidad > 0.3 indica estructura de comunidad significativa)")

    print(f"\n  Top 5 comunidades mas grandes:")
    for i, (cid, miembros) in enumerate(comunidades_ord[:5], 1):
        nombres = [G.nodes[n].get("name", n) for n in miembros[:3]]
        print(f"    Comunidad {cid} - {len(miembros)} autores | Ej: {', '.join(nombres)}...")

    return partition


# ─────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────

def main():
    print("Cargando grafo...")
    G = load_graph(GRAPH_FILE)
    print(f"  {G.number_of_nodes()} nodos | {G.number_of_edges()} aristas")

    analizar_caminos(G)
    centralidad = analizar_centralidad(G)
    analizar_componentes(G)
    particion   = analizar_comunidades(G)

    print(f"\n{'='*55}")
    print("  Analisis completado.")
    print(f"{'='*55}\n")

    return G, centralidad, particion


if __name__ == "__main__":
    main()
