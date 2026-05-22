"""
Construcción del grafo de colaboración científica.
Área: Sistemas Distribuidos

Nodos  : investigadores (authorId, name)
Aristas: colaboraciones entre autores
Peso   : número de papers compartidos
"""

import json
import os
from itertools import combinations
import networkx as nx

DATA_FILE  = os.path.join("data", "papers.json")
GRAPH_FILE = os.path.join("data", "graph.graphml")


def load_papers(path: str) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def build_graph(papers: list[dict]) -> nx.Graph:
    G = nx.Graph()

    for paper in papers:
        authors = paper["authors"]

        for author in authors:
            aid = author["authorId"]
            if not G.has_node(aid):
                G.add_node(aid, name=author["name"])

        for a1, a2 in combinations(authors, 2):
            id1, id2 = a1["authorId"], a2["authorId"]
            if G.has_edge(id1, id2):
                G[id1][id2]["weight"] += 1
            else:
                G.add_edge(id1, id2, weight=1)

    return G


def print_stats(G: nx.Graph) -> None:
    degrees = [d for _, d in G.degree()]
    components = list(nx.connected_components(G))
    giant = max(components, key=len)

    print(f"\n{'='*50}")
    print(f"  ESTADISTICAS DEL GRAFO")
    print(f"{'='*50}")
    print(f"Nodos (autores)         : {G.number_of_nodes():,}")
    print(f"Aristas (colaboraciones): {G.number_of_edges():,}")
    print(f"Densidad                : {nx.density(G):.6f}")
    print(f"Grado promedio          : {sum(degrees)/len(degrees):.2f}")
    print(f"Grado maximo            : {max(degrees)}")
    print(f"Componentes conexas     : {len(list(nx.connected_components(G)))}")
    print(f"Componente gigante      : {len(giant):,} nodos ({len(giant)/G.number_of_nodes()*100:.1f}%)")

    top5 = sorted(G.degree(), key=lambda x: x[1], reverse=True)[:5]
    print(f"\nTop 5 autores por colaboraciones:")
    for i, (aid, deg) in enumerate(top5, 1):
        name = G.nodes[aid].get("name", "Desconocido")
        print(f"  {i}. {name} - {deg} colaboradores")

    top_edges = sorted(G.edges(data=True), key=lambda x: x[2]["weight"], reverse=True)[:5]
    print(f"\nTop 5 colaboraciones mas frecuentes:")
    for a1, a2, data in top_edges:
        n1 = G.nodes[a1].get("name", "?")
        n2 = G.nodes[a2].get("name", "?")
        print(f"  {n1} <-> {n2} (peso: {data['weight']})")
    print(f"{'='*50}\n")


def main() -> nx.Graph:
    print("Cargando papers...")
    papers = load_papers(DATA_FILE)
    print(f"  {len(papers)} papers cargados.")

    print("Construyendo grafo...")
    G = build_graph(papers)

    print_stats(G)

    nx.write_graphml(G, GRAPH_FILE)
    print(f"Grafo guardado en: {GRAPH_FILE}")

    return G


if __name__ == "__main__":
    main()
